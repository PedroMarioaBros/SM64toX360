"""Execute the game's actual PowerPC menu code in a bounded Unicorn harness.

This is NOT Xbox 360 system emulation. Save-file reads, numeric formatting,
and compiler register-save helpers are controlled test boundaries.
The file-star-count routine and the HUD renderer execute their
original/patched PowerPC instructions. Texture addresses
emitted by the HUD renderer are checked before any graphics backend runs.

Requires Unicorn 2.1.4. Use --previous PATH to also check a previous mapped image.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct

from unicorn import Uc, UC_ARCH_PPC, UC_MODE_32, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn import ppc_const as pc

ROOT = Path(__file__).resolve().parent.parent
BASE = 0x82000000
STACK = 0x10000000
STACK_SIZE = 0x10000
DISPLAY = 0x11000000
DISPLAY_SIZE = 0x40000
STOP = 0x12000000
HEAD_PTR = BASE + 0xe47b80
LIMIT_PTR = BASE + 0xe47b18
HUD_LUT = BASE + 0x9df2c8
GPR = [getattr(pc, f'UC_PPC_REG_{i}') for i in range(32)]


class MenuHarness:
    def __init__(self, data, saves):
        self.data = data
        self.saves = saves  # None is an empty slot, an integer is a star count.
        self.uc = Uc(UC_ARCH_PPC, UC_MODE_32 | UC_MODE_BIG_ENDIAN)
        self.uc.mem_map(BASE, (len(data) + 0xfff) & ~0xfff)
        self.uc.mem_write(BASE, data)
        self.uc.mem_map(STACK, STACK_SIZE)
        self.uc.mem_map(DISPLAY, DISPLAY_SIZE)
        self.uc.mem_map(STOP, 0x1000)
        self.uc.mem_write(HEAD_PTR, struct.pack('>I', DISPLAY))
        self.uc.mem_write(LIMIT_PTR, struct.pack('>I', DISPLAY + DISPLAY_SIZE))
        self.saved_frames = []
        self.calls = []
        self.textures = []
        self.errors = []
        self.finished = False
        self.uc.hook_add(UC_HOOK_CODE, self._hook)

    def r(self, index):
        return self.uc.reg_read(GPR[index]) & 0xffffffff

    def w(self, index, value):
        self.uc.reg_write(GPR[index], value & 0xffffffff)

    def read32(self, address):
        return struct.unpack('>I', self.uc.mem_read(address, 4))[0]

    def return_to_caller(self):
        self.uc.reg_write(pc.UC_PPC_REG_PC, self.uc.reg_read(pc.UC_PPC_REG_LR))

    def string(self, address):
        out = bytearray()
        for n in range(256):
            char = self.uc.mem_read(address + n, 1)[0]
            if char == 0xff:
                return bytes(out)
            out.append(char)
        raise AssertionError(f'Unterminated menu string at {address:#x}')

    def valid_texture(self, address, size):
        return BASE + 0x3c0000 <= address <= BASE + len(self.data) - size

    def capture_text(self, kind, pointer):
        text = self.string(pointer)
        self.calls.append({'kind': kind, 'pointer': hex(pointer), 'bytes': text.hex()})
        # The actual HUD renderer performs the texture lookup below.

    def _hook(self, uc, address, size, _):
        offset = address - BASE
        if address == STOP:
            self.finished = True
            uc.emu_stop()
            return

        # Xbox compiler helpers contain PPC64 stores. Model only their documented
        # ABI effect, preserving actual nonvolatile registers and the saved LR.
        if 0x3a7600 <= offset <= 0x3a7644 and offset % 4 == 0:
            first = 14 + (offset - 0x3a7600) // 4
            self.saved_frames.append((first, [self.r(i) for i in range(first, 32)],
                                      self.r(12), self.r(1)))
            self.return_to_caller()
            return
        if 0x3a7650 <= offset <= 0x3a7694 and offset % 4 == 0:
            first = 14 + (offset - 0x3a7650) // 4
            saved_first, values, lr, sp = self.saved_frames.pop()
            assert first == saved_first and self.r(1) == sp
            for i, value in enumerate(values, first):
                self.w(i, value)
            uc.reg_write(pc.UC_PPC_REG_LR, lr)
            uc.reg_write(pc.UC_PPC_REG_PC, lr)
            return

        if offset == 0x12efa8:  # save_file_exists(slot)
            self.w(3, int(self.saves[self.r(3)] is not None))
            self.return_to_caller()
        elif offset == 0x12f840:  # save_file_get_total_star_count(slot, 0, 24)
            assert self.r(4) == 0 and self.r(5) == 24
            self.w(3, self.saves[self.r(3)])
            self.return_to_caller()
        elif offset == 0xd16c8:  # int_to_str(stars, stack_buffer)
            uc.mem_write(self.r(4), bytes(int(c) for c in str(self.r(3))) + b'\xff')
            self.return_to_caller()
        elif offset == 0x398c78:  # segmented_to_virtual: NO_SEGMENTED_MEMORY build
            self.return_to_caller()
        elif offset == 0xd0a80:
            self.capture_text('hud', self.r(6))
            # Execute the actual renderer, including its table lookups and stores.
        elif offset == 0xd0bf4:
            # stw r6, 4(r11): the actual selected texture is now in r6.
            texture = self.r(6)
            char = uc.mem_read(self.r(26), 1)[0]
            self.textures.append({'character': hex(char), 'texture': hex(texture)})
            if not self.valid_texture(texture, 512):
                self.errors.append({'kind': 'hud', 'character': hex(char),
                                    'texture': hex(texture)})
        elif offset == 0xcc900:
            raise AssertionError('Display-list capacity exhausted in the bounded test')
        elif not (0x143280 <= offset < 0x143360 or 0xd0a80 <= offset < 0xd0d20
                  or 0x3bc600 <= offset < 0x3c0000):
            raise AssertionError(f'Unmodelled external call {address:#x}')

    def run(self, slot=0):
        for i in range(32):
            self.w(i, 0x60000000 + i * 0x100)
        self.w(1, STACK + STACK_SIZE - 0x1000)
        self.w(3, slot)
        self.w(4, 92)
        self.w(5, 78)
        self.uc.reg_write(pc.UC_PPC_REG_LR, STOP)
        start = BASE + 0x143280
        self.uc.emu_start(start, STOP + 4, count=100000)
        assert self.finished and not self.saved_frames, 'Routine did not return'
        assert self.read32(HEAD_PTR) <= DISPLAY + DISPLAY_SIZE
        # Independently inspect the renderer's actual display-list output.
        commands = self.uc.mem_read(DISPLAY, self.read32(HEAD_PTR) - DISPLAY)
        textures = [v for op, v in struct.iter_unpack('>II', commands) if op == 0xfd100000]
        assert textures == [int(row['texture'], 16) for row in self.textures]
        return {'saves': self.saves, 'slot': slot,
                'errors': self.errors, 'strings': self.calls,
                'textures_emitted': len(self.textures), 'returned': True}


def check_image(path):
    data = path.read_bytes()
    cases = []
    for slot in range(4):
        for count in [None, 0, 1, 42, 99, 100, 120]:
            saves = [None] * 4
            saves[slot] = count
            result = MenuHarness(data, saves).run(slot)
            expected_count = 1 if count is None else (3 if count < 100 else 2)
            assert len(result['strings']) == expected_count
            result['expected_strings_match'] = True
            if count is not None:
                expected = [b'\x35']
                if count < 100:
                    expected.append(b'\x32')
                expected.append(bytes(int(c) for c in str(count)))
                result['expected_strings_match'] = [bytes.fromhex(row['bytes']) for row in result['strings']] == expected
            cases.append(result)
    return {'mapped_sha256': hashlib.sha256(data).hexdigest(),
            'case_count': len(cases), 'cases_with_invalid_textures': sum(bool(c['errors']) for c in cases),
            'cases_with_wrong_symbols': sum(not c['expected_strings_match'] for c in cases),
            'cases': cases}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--previous', type=Path)
    args = parser.parse_args()
    result = {'scope': 'PowerPC routines only; controlled save and compiler-helper boundaries. '
                        'No full Xbox 360 system or graphics-backend execution.',
              'original': check_image(ROOT / 'inspect/base.bin'),
              'revised': check_image(ROOT / 'inspect/translated-base.bin')}
    assert result['original']['cases_with_invalid_textures'] == 0
    assert result['revised']['cases_with_invalid_textures'] == 0
    assert result['original']['cases_with_wrong_symbols'] == 0
    assert result['revised']['cases_with_wrong_symbols'] == 0
    if args.previous:
        result['previous_0_2'] = check_image(args.previous)
        assert result['previous_0_2']['cases_with_invalid_textures'] == 16
        assert result['previous_0_2']['cases_with_wrong_symbols'] == 24
    result['status'] = 'PASS - bounded binary regression; console test still required'
    (ROOT / 'ptbr-work/regressao-menu.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: {name: value for name, value in v.items() if name != 'cases'}
                      if isinstance(v, dict) else v for k, v in result.items()}, indent=2))


if __name__ == '__main__':
    main()
