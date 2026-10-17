#!/usr/bin/env python3
"""Marca APENAS dois recursos ASCII da tela inicial para testar carregamento.

DIAGNÓSTICO VISUAL TEST6. Não implementa seletor nem altera código/jogabilidade.
Só opera no PE mapeado AES da TEST5, nunca no XEX criptografado.
"""
import argparse
import hashlib
import json
from pathlib import Path

TEST5_PE_SHA256 = "a6c0a1c451f6dd114f73bd324cb297d42f3ed6f6c027c8237d3244284e622672"
MARKERS = {
    0x778: (b"APERTE", b"TESTE6"),
    0x1C98: (b"APERTE START", b"TESTE6 START"),
}
LANG_BOUNDS=(0x1040000,0x1060000)
LEVEL_SCRIPT_CALL=(0xCD128,0xCD12C)
TITLE_CALL=(0x147448,0x14744C)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def mark(pe, *, require_known_sha=True):
    if require_known_sha and sha(pe)!=TEST5_PE_SHA256:
        raise ValueError("source must be exact mapped TEST5 PE; never guess")
    out=bytearray(pe)
    valid=set()
    for offset,(before,after) in MARKERS.items():
        if len(before)!=len(after):
            raise ValueError("marker changes source layout size")
        if pe[offset:offset+len(before)]!=before:
            raise ValueError(f"unexpected title resource at {offset:#x}")
        valid.update(range(offset,offset+len(before)))
        out[offset:offset+len(after)]=after
    changed=[i for i,(a,b) in enumerate(zip(pe,out)) if a!=b]
    if any(i not in valid for i in changed):
        raise ValueError("code or unrelated game data changed")
    for lo,hi in (LANG_BOUNDS,LEVEL_SCRIPT_CALL,TITLE_CALL):
        if pe[lo:hi]!=out[lo:hi]:
            raise ValueError("immutable game/runtime region changed")
    return bytes(out),{
        "status":"TITLE_MARKER_DIAGNOSTIC_NOT_FUNCTIONAL_LANGUAGE_SELECTOR",
        "marker":"TESTE6",
        "source_pe_sha256":sha(pe),
        "new_pe_sha256":sha(out),
        "changed_bytes":len(changed),
        "changed_positions":[hex(i) for i in changed],
        "allowed_intervals":[[hex(a),len(b)] for a,(b,_) in MARKERS.items()],
        "lang_section_byte_identical":True,
        "selector_code_unchanged":True,
        "level_script_code_unchanged":True,
        "no_dubbing_work":True,
        "xbox_hardware_pending":True,
    }

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("test5_mapped_pe",type=Path)
    a.add_argument("output_mapped_pe",type=Path)
    a.add_argument("--report",type=Path)
    opts=a.parse_args()
    output,report=mark(opts.test5_mapped_pe.read_bytes())
    opts.output_mapped_pe.write_bytes(output)
    if opts.report:
        opts.report.parent.mkdir(parents=True,exist_ok=True)
        opts.report.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
