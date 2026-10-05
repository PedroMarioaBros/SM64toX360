#!/usr/bin/env python3
"""Generate the PowerPC pre-game language gate for the canonical SM64 Xbox 360 v0.4.

Hook contract:
  The original call at 0x820CD128 is:
      bl level_script_execute (0x82095448)
  It is replaced by:
      bl pregame_gate (0x823BC900)

Before language selection, the gate builds a valid frame without advancing the
original level script. After selection, it delegates to the original
level_script_execute unchanged.

.lang ABI v2:
  0x83040014 selector state: 0 credits, 1 language, 2 done
  0x83040018 selected language: 0 PT-BR, 1 ES, 2 EN
  0x8304001C credits timer
  0x83040040..0x6C selector text pointers
"""

from __future__ import annotations
import hashlib
import json
import struct

GATE_VA = 0x823BC900
LANG_BASE = 0x83040000
ORIG_LEVEL_SCRIPT_EXECUTE = 0x82095448
INIT_RCP = 0x820CE780
RENDER_GAME = 0x82099498
CREATE_DL_ORTHO = 0x820D0470
PRINT_GENERIC_STRING_FADE = 0x82143110
END_MASTER_DISPLAY_LIST = 0x820CE7B0
ALLOC_DISPLAY_LIST = 0x820FB8A0
ACTIVATE_LANGUAGE = 0x823BC800
PLAYER1_CONTROLLER_PTR = 0x823C8990

class Asm:
    def __init__(self, base: int):
        self.base = base
        self.words: list[int] = []
        self.labels: dict[str, int] = {}
        self.fixups: list[tuple[int, str, str]] = []

    def pc(self): return self.base + len(self.words) * 4
    def emit(self, word): self.words.append(word & 0xFFFFFFFF)
    def label(self, name): self.labels[name] = self.pc()
    def lis(self, rt, imm): self.emit(0x3C000000 | (rt << 21) | (imm & 0xFFFF))
    def addi(self, rt, ra, imm): self.emit(0x38000000 | (rt << 21) | (ra << 16) | (imm & 0xFFFF))
    def li(self, rt, imm): self.addi(rt, 0, imm)
    def lwz(self, rt, d, ra): self.emit(0x80000000 | (rt << 21) | (ra << 16) | (d & 0xFFFF))
    def stw(self, rs, d, ra): self.emit(0x90000000 | (rs << 21) | (ra << 16) | (d & 0xFFFF))
    def lhz(self, rt, d, ra): self.emit(0xA0000000 | (rt << 21) | (ra << 16) | (d & 0xFFFF))
    def stb(self, rs, d, ra): self.emit(0x98000000 | (rs << 21) | (ra << 16) | (d & 0xFFFF))
    def cmpwi(self, ra, imm): self.emit(0x2C000000 | (ra << 16) | (imm & 0xFFFF))
    def andi(self, ra, rs, imm): self.emit(0x70000000 | (rs << 21) | (ra << 16) | (imm & 0xFFFF))
    def mr(self, ra, rs): self.emit(0x7C000378 | (rs << 21) | (ra << 16) | (rs << 11))
    def mflr(self): self.emit(0x7C0802A6)
    def mtlr(self): self.emit(0x7C0803A6)
    def blr(self): self.emit(0x4E800020)

    def branch(self, label, kind="b"):
        self.fixups.append((len(self.words), label, kind))
        self.emit(0)

    def call(self, target):
        disp = target - self.pc()
        if disp % 4 or not -(1 << 25) <= disp < (1 << 25):
            raise ValueError(f"BL out of range: {self.pc():#x}->{target:#x}")
        self.emit(0x48000001 | (disp & 0x03FFFFFC))

    def resolve(self):
        for idx, label, kind in self.fixups:
            pc = self.base + idx * 4
            disp = self.labels[label] - pc
            if kind == "b":
                word = 0x48000000 | (disp & 0x03FFFFFC)
            else:
                if not -0x8000 <= disp < 0x8000:
                    raise ValueError(f"BC out of range: {label}")
                op = {"beq": 0x41820000, "bne": 0x40820000}[kind]
                word = op | (disp & 0x0000FFFC)
            self.words[idx] = word
        return b"".join(struct.pack(">I", w) for w in self.words)

def build() -> bytes:
    a = Asm(GATE_VA)

    a.mflr()
    a.emit(0x9421FF60)  # stwu r1,-0xA0(r1)
    a.stw(0, 0x98, 1)
    a.stw(30, 0x90, 1)
    a.stw(31, 0x94, 1)
    a.mr(31, 3)         # preserve levelCommandAddr
    a.lis(30, 0x8304)   # .lang base

    a.lwz(10, 0x14, 30)
    a.cmpwi(10, 2)
    a.branch("original", "beq")

    # Reproduce the rendering tail of level_script_execute without executing
    # a single original level-script command.
    a.call(INIT_RCP)
    a.call(RENDER_GAME)
    a.call(CREATE_DL_ORTHO)

    # print_generic_string_fade uses file-select's private alpha bytes.
    a.lis(11, 0x82E5)
    a.li(10, 255)
    a.stb(10, 0x2F88, 11)
    a.li(10, 0)
    a.stb(10, 0x2F8B, 11)

    a.lwz(10, 0x14, 30)
    a.cmpwi(10, 0)
    a.branch("credits", "beq")
    a.branch("language")

    a.label("credits")
    for x, y, off in (
        (92, 210, 0x40),
        (105, 188, 0x44),
        (50, 164, 0x48),
        (72, 138, 0x4C),
        (63, 116, 0x50),
        (51, 88, 0x54),
    ):
        a.li(3, x); a.li(4, y); a.lwz(5, off, 30); a.call(PRINT_GENERIC_STRING_FADE)

    a.lwz(10, 0x1C, 30)
    a.addi(10, 10, 1)
    a.stw(10, 0x1C, 30)

    # A skips the credits page.
    a.lis(11, 0x823D)
    a.lwz(10, -0x7670, 11)
    a.cmpwi(10, 0)
    a.branch("credit_timer", "beq")
    a.lhz(9, 0x12, 10)
    a.andi(8, 9, 0x8000)
    a.cmpwi(8, 0)
    a.branch("to_language", "bne")

    a.label("credit_timer")
    a.lwz(10, 0x1C, 30)
    a.cmpwi(10, 45)     # ~1.5 s at the canonical 30 FPS
    a.branch("finish_frame", "bne")

    a.label("to_language")
    a.li(10, 1)
    a.stw(10, 0x14, 30)
    a.li(10, 0)
    a.stw(10, 0x18, 30)
    a.stw(10, 0x1C, 30)
    a.branch("finish_frame")

    a.label("language")
    for x, y, off in (
        (76, 195, 0x58),
        (118, 145, 0x5C),
        (118, 115, 0x60),
        (118, 85, 0x64),
        (104, 30, 0x68),
    ):
        a.li(3, x); a.li(4, y); a.lwz(5, off, 30); a.call(PRINT_GENERIC_STRING_FADE)

    # Selection marker.
    a.lwz(10, 0x18, 30)
    a.li(3, 96)
    a.cmpwi(10, 0); a.branch("star_pt", "beq")
    a.cmpwi(10, 1); a.branch("star_es", "beq")
    a.li(4, 85); a.branch("draw_star")
    a.label("star_pt"); a.li(4, 145); a.branch("draw_star")
    a.label("star_es"); a.li(4, 115)
    a.label("draw_star")
    a.lwz(5, 0x6C, 30)
    a.call(PRINT_GENERIC_STRING_FADE)

    # Read already-normalized SM64 buttonPressed.
    a.lis(11, 0x823D)
    a.lwz(10, -0x7670, 11)
    a.cmpwi(10, 0)
    a.branch("finish_frame", "beq")
    a.lhz(9, 0x12, 10)

    # D-pad Up: 0 -> 2 -> 1 -> 0
    a.andi(8, 9, 0x0800); a.cmpwi(8, 0); a.branch("check_down", "beq")
    a.lwz(10, 0x18, 30); a.cmpwi(10, 0); a.branch("up_dec", "bne")
    a.li(10, 2); a.branch("store_selection")
    a.label("up_dec"); a.addi(10, 10, -1); a.branch("store_selection")

    # D-pad Down: 0 -> 1 -> 2 -> 0
    a.label("check_down")
    a.andi(8, 9, 0x0400); a.cmpwi(8, 0); a.branch("check_confirm", "beq")
    a.lwz(10, 0x18, 30); a.cmpwi(10, 2); a.branch("down_inc", "bne")
    a.li(10, 0); a.branch("store_selection")
    a.label("down_inc"); a.addi(10, 10, 1)

    a.label("store_selection")
    a.stw(10, 0x18, 30)
    a.branch("finish_frame")

    # A confirms the selected language.
    a.label("check_confirm")
    a.andi(8, 9, 0x8000); a.cmpwi(8, 0); a.branch("finish_frame", "beq")
    a.lwz(3, 0x18, 30)
    a.call(ACTIVATE_LANGUAGE)
    a.li(10, 2)
    a.stw(10, 0x14, 30)

    # Restore original file-select fade defaults.
    a.lis(11, 0x82E5)
    a.li(10, 0)
    a.stb(10, 0x2F88, 11)
    a.stb(10, 0x2F8B, 11)

    a.label("finish_frame")
    a.call(END_MASTER_DISPLAY_LIST)
    a.li(3, 0)
    a.call(ALLOC_DISPLAY_LIST)
    a.mr(3, 31)        # unchanged levelCommandAddr
    a.branch("epilogue")

    a.label("original")
    a.mr(3, 31)
    a.call(ORIG_LEVEL_SCRIPT_EXECUTE)

    a.label("epilogue")
    a.lwz(30, 0x90, 1)
    a.lwz(31, 0x94, 1)
    a.lwz(0, 0x98, 1)
    a.emit(0x382100A0)  # addi r1,r1,0xA0
    a.mtlr()
    a.blr()

    return a.resolve()

def report():
    raw = build()
    return {
        "gate_va": hex(GATE_VA),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "original_hook_call": "0x820CD128",
        "original_level_script_execute": hex(ORIG_LEVEL_SCRIPT_EXECUTE),
        "frame_functions": {
            "init_rcp": hex(INIT_RCP),
            "render_game": hex(RENDER_GAME),
            "create_dl_ortho_matrix": hex(CREATE_DL_ORTHO),
            "print_generic_string_fade": hex(PRINT_GENERIC_STRING_FADE),
            "end_master_display_list": hex(END_MASTER_DISPLAY_LIST),
            "alloc_display_list": hex(ALLOC_DISPLAY_LIST),
        },
    }

if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
