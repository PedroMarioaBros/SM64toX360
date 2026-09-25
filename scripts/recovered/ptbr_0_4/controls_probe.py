"""Verify the supplied port's actual PowerPC input mapper with controlled XInput.

Unicorn executes instructions 0x821659AC..0x82165C74. The XInputGetState call
returns a synthetic state, two PPC64 zero stores are modelled, and prologue/
epilogue register saves are outside the bounded run. This is not console testing.
"""
from pathlib import Path
import hashlib
import json
import struct
from unicorn import Uc, UC_ARCH_PPC, UC_MODE_32, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn import ppc_const as pc

ROOT = Path(__file__).resolve().parent.parent
BASE = 0x82000000
INPUT_START, INPUT_END = 0x165998, 0x165c90
PREVIOUS = BASE + 0xf9e364
FRAME_DUMP = BASE + 0xf6ca20
SKIP_DECALS = BASE + 0xf6ca24
BUTTONS = {'D-pad cima': 0x0001, 'D-pad baixo': 0x0002, 'D-pad esquerda': 0x0004,
           'D-pad direita': 0x0008, 'START': 0x0010, 'BACK': 0x0020,
           'Clique analogico esquerdo': 0x0040, 'Clique analogico direito': 0x0080,
           'LB': 0x0100, 'RB': 0x0200, 'A': 0x1000, 'B': 0x2000,
           'X': 0x4000, 'Y': 0x8000}
EXPECTED = {'D-pad cima': 0x0800, 'D-pad baixo': 0x0400,
            'D-pad esquerda': 0x0200, 'D-pad direita': 0x0100,
            'START': 0x1000, 'BACK': 0, 'Clique analogico esquerdo': 0,
            'Clique analogico direito': 0, 'LB': 0x2000, 'RB': 0x0010,
            'A': 0x8000, 'B': 0, 'X': 0x4000, 'Y': 0}
GPR = [getattr(pc, f'UC_PPC_REG_{i}') for i in range(32)]


def probe(data, buttons=0, lt=0, rt=0, lx=0, ly=0, rx=0, ry=0,
          previous=0, disconnected=False, skip_decals=0):
    uc = Uc(UC_ARCH_PPC, UC_MODE_32 | UC_MODE_BIG_ENDIAN)
    uc.mem_map(BASE, (len(data) + 0xfff) & ~0xfff)
    uc.mem_write(BASE, data)
    uc.mem_map(0x10000000, 0x20000)
    stack, pad = 0x10008000, 0x10010000
    uc.reg_write(GPR[1], stack)
    uc.reg_write(GPR[3], pad)
    uc.mem_write(PREVIOUS, struct.pack('>H', previous))
    uc.mem_write(FRAME_DUMP, bytes(4))
    uc.mem_write(SKIP_DECALS, struct.pack('>I', skip_decals))
    state = struct.pack('>IHBBhhhh', 1, buttons, lt, rt, lx, ly, rx, ry)
    calls = 0

    def hook(u, address, size, user):
        nonlocal calls
        if address == BASE + 0x39e010:
            assert u.reg_read(GPR[3]) == 0, 'Unexpected controller index'
            ptr = u.reg_read(GPR[4])
            if not disconnected:
                u.mem_write(ptr, state)
            u.reg_write(GPR[3], 1167 if disconnected else 0)
            u.reg_write(pc.UC_PPC_REG_PC, u.reg_read(pc.UC_PPC_REG_LR))
            calls += 1
        elif address in (BASE + 0x1659c0, BASE + 0x1659c4):
            # std r31, 0/8(r11), with r31 == 0. Keep the original binary untouched.
            assert u.reg_read(GPR[31]) == 0
            ptr = u.reg_read(GPR[11]) + (8 if address == BASE + 0x1659c4 else 0)
            u.mem_write(ptr, bytes(8))
            u.reg_write(pc.UC_PPC_REG_PC, address + 4)
        elif not BASE + 0x1659ac <= address < BASE + 0x165c78:
            raise AssertionError(f'Unexpected execution at {address:#x}')

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(BASE + 0x1659ac, BASE + 0x165c78, count=10000)
    assert calls == 1 and uc.reg_read(pc.UC_PPC_REG_PC) == BASE + 0x165c78
    bits, sx, sy = struct.unpack('>Hbb', uc.mem_read(pad, 4))
    read32 = lambda at: struct.unpack('>I', uc.mem_read(at, 4))[0]
    return {'game_button_bits': bits, 'stick_x': sx, 'stick_y': sy,
            'frame_dump_requested': read32(FRAME_DUMP), 'skip_decals': read32(SKIP_DECALS)}


def suite(data):
    cases = []
    def check(name, params, bits=None, **expected):
        out = probe(data, **params)
        if bits is not None:
            assert out['game_button_bits'] == bits, (name, out)
        for key, value in expected.items():
            assert out[key] == value, (name, key, value, out)
        cases.append({'input': name, 'parameters': params, 'output': out})

    for name, value in BUTTONS.items():
        check(name, {'buttons': value}, EXPECTED[name],
              skip_decals=int(name == 'Y'), frame_dump_requested=0)
    for axis, bits in [('lt', 0x2000), ('rt', 0x0010)]:
        for value in [0, 64, 65, 255]:
            check(f'{axis.upper()} {value}', {axis: value}, bits if value > 64 else 0)
    for axis, neg, pos in [('rx', 2, 1), ('ry', 4, 8)]:
        for value in [-32768, -16001, -16000, 0, 16000, 16001, 32767]:
            check(f'{axis} {value}', {axis: value}, neg if value < -16000 else pos if value > 16000 else 0)
    for axis, out_axis in [('lx', 'stick_x'), ('ly', 'stick_y')]:
        for value, expected in [(-32768, -128), (-7849, -30), (-7848, 0),
                                (0, 0), (7848, 0), (7849, 30), (32767, 127)]:
            check(f'{axis} {value}', {axis: value}, 0, **{out_axis: expected})
    check('A+LT, salto agachado', {'buttons': 0x1000, 'lt': 255}, 0xa000)
    check('X+RB', {'buttons': 0x4200}, 0x4010)
    check('Y segurado nao alterna novamente', {'buttons': 0x8000, 'previous': 0x8000}, 0, skip_decals=0)
    check('Y alterna de volta', {'buttons': 0x8000, 'skip_decals': 1}, 0, skip_decals=0)
    check('BACK+START pede dump, nao pausa', {'buttons': 0x30}, 0, frame_dump_requested=1)
    check('BACK+START segurados', {'buttons': 0x30, 'previous': 0x30}, 0, frame_dump_requested=0)
    check('Controle desconectado', {'disconnected': True, 'buttons': 0xffff}, 0, stick_x=0, stick_y=0)
    return cases


def main():
    data = (ROOT / 'inspect/base.bin').read_bytes()
    assert hashlib.sha256(data).hexdigest() == '75f653c7383b8cbbd218449bbd7ea45c787b7bf62db3d9e312356517834a91c7'
    cases = suite(data)
    report = {'status': 'PASS - controlled PowerPC input routine execution',
              'routine': ['0x82165998', '0x82165C90'],
              'xinput_wrapper': '0x8239E010', 'xam_input_get_state_ordinal': '0x191',
              'case_count': len(cases), 'cases': cases,
              'input_routine_sha256': hashlib.sha256(data[INPUT_START:INPUT_END]).hexdigest(),
              'sources': ['https://learn.microsoft.com/en-us/windows/win32/api/xinput/ns-xinput-xinput_gamepad',
                          'https://raw.githubusercontent.com/xenia-project/xenia/master/src/xenia/kernel/xam/xam_table.inc'],
              'limits': 'Synthetic XInput states; not a physical Xbox 360 controller test.'}
    revised = ROOT / 'inspect/translated-base.bin'
    if revised.exists():
        updated = revised.read_bytes()
        assert updated[INPUT_START:INPUT_END] == data[INPUT_START:INPUT_END]
        assert suite(updated) == cases
        report['revised_input_identical_and_verified'] = True
    (ROOT / 'ptbr-work/controles-verificados.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'cases'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
