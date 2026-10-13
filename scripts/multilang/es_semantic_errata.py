#!/usr/bin/env python3
"""Erratas verificáveis de equivalência do roteiro ES contra fonte US original.

A tradução espanhola Reonu já tem todos os 170 IDs. Estas correções estritas
reintroduzem orientações de controle presentes na fonte inglesa e omitidas
no espanhol e corrigem erros evidentes de escrita. As alterações são aplicadas
SOMENTE após localizar os botões para Xbox e ANTES do reflow. Não modificar PT-BR.

Cada substituição exige correspondência exata uma única vez: se a fonte fixa
mudar, a preparação da build FALHA ao invés de alterar texto não verificado.
"""
from __future__ import annotations

from collections import Counter

ERRATA = {
    15: [
        # Missing from ES: Press A then B to Kick.
        ("para dar un puñetazo.\nPara recoger",
         "para dar un puñetazo.\nPulsa A y luego X para dar\nuna patada.\nPara recoger"),
    ],
    30: [
        ("¡en comentando el", "comentando el"),
    ],
    32: [
        # Missing US instruction: put the Wing Cap on before triple jumping.
        ("Solo\ntienes que dar un triple\nsalto, es decir, saltar\ntres veces seguidas,\npara despegar.",
         "Ponte la gorra y da un\ntriple salto: salta tres\nveces seguidas para\ndespegar."),
        ("para mirad a tu alrededor", "para mirar a tu alrededor"),
    ],
    34: [
        # US dialog explains resuming play, changing cameras and that signs
        # repeat the instructions. All three were omitted from Spanish.
        ("De momento, esto ha sido\ntodo.",
         "Pulsa A para seguir jugando.\nCambia de cámara con RB/RT.\nLos carteles del camino\nrepasan estas instrucciones.\n\nDe momento, esto ha sido\ntodo."),
    ],
    46: [
        # Restore the explicit wall-kick jump input, absent from ES.
        ("y luego vuelve a\nsaltar cuando la toques.",
         "y pulsa A otra vez\ncuando la toques."),
    ],
}


def apply_errata(rows):
    ids = [row["id"] for row in rows]
    if ids != list(range(170)):
        raise ValueError("ES needs exactly 170 dialog IDs 000..169")
    modified = []
    for dialog_id, changes in ERRATA.items():
        row = rows[dialog_id]
        text = row["text"]
        for before, after in changes:
            occurrences = text.count(before)
            if occurrences != 1:
                raise ValueError(
                    f"ES dialog {dialog_id:03}: anchored erratum expected once, "
                    f"found {occurrences}; do not apply unverified localization"
                )
            text = text.replace(before, after, 1)
        row["text"] = text
        modified.append(dialog_id)
    return {
        "source_translation": "Reonu/ultrasm64-spanish@b720e8328c4ead21e3eac5dfceb21edba38ed79b",
        "english_reference": "n64decomp/sm64@9921382a68bb0c865e5e45eb594d9c64db59b1af",
        "errata_dialog_ids": modified,
        "all_edits_anchored": True,
        "pt_br_unchanged": True,
        "english_original_except_controller_labels": True,
        "semantics_scope": "audited input/action omissions and obvious source typos only",
        "full_semantic_equivalence_proven": False,
    }
