#!/usr/bin/env python3
"""Diagnóstico reproduzível: crash ao voltar para o castelo após pegar estrela.

Compara dois pacotes XEX Basic criptografados, decripta apenas para leitura e
confere que o build com créditos mudou exclusivamente o hook principal e o
code cave de 264 bytes. NÃO recompila nem assina executáveis.

Este PASS é uma prova de diferença binária, NÃO prova de estabilidade no Xbox.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_bps_xex_overlap import read_xex_pe

TEST3_PE_SHA = "a1bc5c6db7e32d4214c2d1329874f68dee058c91063b67bbacde7ae197a48f6c"
CREDITS_PE_SHA = "bb1a7ecd3c7deb0e10c316a92bf467ca0ea1104dae86bc602af9c6802aab6b56"
TEST3_XEX_SHA = "b90ae1d1be953c1f817e9c64286c67da855778ac7c671098a3cd8495d8b6afd9"
CREDITS_XEX_SHA = "6d5d94f681796b66024c2b820908eee3c49f101f08ebdc87c4694c6da67824b0"
CALL_OFFSET = 0xCD128
CODE_BEGIN = 0x3BC900
CODE_END = 0x3BCA08
ORIGINAL_BL = bytes.fromhex("4bfc8321")
CREDITS_BL = bytes.fromhex("482ef7d9")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def compare_pe(control, failing):
    if len(control) != len(failing) or len(control) < CODE_END:
        raise ValueError("imagens PE com tamanhos inesperados")
    if control[CALL_OFFSET:CALL_OFFSET + 4] != ORIGINAL_BL:
        raise ValueError("TEST3 não apresenta a chamada original esperada")
    if failing[CALL_OFFSET:CALL_OFFSET + 4] != CREDITS_BL:
        raise ValueError("build de créditos não contém hook esperado")
    if any(control[CODE_BEGIN:CODE_END]):
        raise ValueError("região reservada no TEST3 não está vazia")
    changes = [idx for idx, (a, b) in enumerate(zip(control, failing)) if a != b]
    outside = [idx for idx in changes if not (
        CALL_OFFSET <= idx < CALL_OFFSET + 4
        or CODE_BEGIN <= idx < CODE_END
    )]
    if outside:
        raise ValueError(f"diferenças inesperadas fora do hook: primeira={outside[0]:#x}")
    reverted = bytearray(failing)
    reverted[CALL_OFFSET:CALL_OFFSET + 4] = control[CALL_OFFSET:CALL_OFFSET + 4]
    reverted[CODE_BEGIN:CODE_END] = control[CODE_BEGIN:CODE_END]
    if reverted != control:
        raise ValueError("rollback de hook/cave não restaura TEST3 exatamente")
    return {
        "status": "STATIC_AB_ISOLATION_VERIFIED_CONSOLE_TEST_REQUIRED",
        "pe_size": len(control),
        "modified_bytes": len(changes),
        "hook": {
            "pe_offset": hex(CALL_OFFSET),
            "test3_original_call": ORIGINAL_BL.hex(),
            "credits_hook": CREDITS_BL.hex(),
        },
        "experimental_code": {
            "pe_start": hex(CODE_BEGIN),
            "pe_end_exclusive": hex(CODE_END),
            "reserved_bytes": CODE_END - CODE_BEGIN,
            "nonzero_bytes": sum(x != 0 for x in failing[CODE_BEGIN:CODE_END]),
        },
        "no_other_pe_differences": True,
        "restored_pe_sha256": sha(reverted),
        "control_pe_sha256": sha(control),
        "failing_pe_sha256": sha(failing),
        "hardware_result": "PENDING",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("approved_test3_zip", type=Path)
    parser.add_argument("crashing_credits_zip", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    control_raw, control = read_xex_pe(args.approved_test3_zip)
    failing_raw, failing = read_xex_pe(args.crashing_credits_zip)
    for description, got, expected in (
        ("TEST3 XEX", sha(control_raw), TEST3_XEX_SHA),
        ("Créditos XEX", sha(failing_raw), CREDITS_XEX_SHA),
        ("TEST3 PE", sha(control), TEST3_PE_SHA),
        ("Créditos PE", sha(failing), CREDITS_PE_SHA),
    ):
        if got != expected:
            raise ValueError(f"{description}: SHA-256 não corresponde aos binários auditados")
    report = compare_pe(control, failing)
    report["assets"] = {
        "test3_xex_sha256": sha(control_raw),
        "credits_xex_sha256": sha(failing_raw),
    }
    result = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(result, encoding="utf-8")
    print(result)


if __name__ == "__main__":
    main()
