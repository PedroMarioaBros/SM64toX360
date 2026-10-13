"""Regressões de equivalência ES/EN e de rótulos reais do Xbox 360."""
import copy
import unittest

from es_semantic_errata import ERRATA, apply_errata
from localize_controller_texts import convert, LEGACY_RE


class LocaleSemanticErrataTests(unittest.TestCase):
    def fixtures(self):
        rows = [{"id": i, "lines": 6, "text": "texto neutro"} for i in range(170)]
        rows[15]["text"] = (
            "Pulsa A para saltar, y X\npara dar un puñetazo.\n"
            "Para recoger algo, pulsa X."
        )
        rows[30]["text"] = "Hermanos Lakitu, ¡en comentando el progreso de Mario."
        rows[32]["text"] = (
            "Solo\ntienes que dar un triple\nsalto, es decir, saltar\n"
            "tres veces seguidas,\npara despegar.\n"
            "para\nmirad a tu alrededor"
        )
        rows[34]["text"] = "De momento, esto ha sido\ntodo."
        rows[46]["text"] = "y luego vuelve a\nsaltar cuando la toques."
        return rows

    def test_restore_omitted_kick_and_camera_instruction(self):
        rows = self.fixtures()
        before_other = rows[35]["text"]
        result = apply_errata(rows)
        self.assertEqual(result["errata_dialog_ids"], [15, 30, 32, 34, 46])
        self.assertIn("Pulsa A y luego X", rows[15]["text"])
        self.assertIn("patada", rows[15]["text"])
        self.assertIn("Cambia de cámara con RB/RT", rows[34]["text"])
        self.assertIn("Pulsa A para seguir jugando", rows[34]["text"])
        self.assertEqual(rows[35]["text"], before_other)

    def test_restore_wing_cap_and_wall_kick(self):
        rows = self.fixtures()
        apply_errata(rows)
        self.assertIn("Ponte la gorra", rows[32]["text"])
        self.assertIn("mirar a tu alrededor", rows[32]["text"])
        self.assertIn("pulsa A otra vez", rows[46]["text"])
        self.assertNotIn("¡en comentando", rows[30]["text"])

    def test_anchored_substitutions_fail_on_changed_source(self):
        rows = self.fixtures()
        rows[15]["text"] = "traducción externa desconocida"
        with self.assertRaisesRegex(ValueError, "anchored erratum"):
            apply_errata(rows)

    def test_duplicate_anchors_are_not_silently_replaced(self):
        rows = self.fixtures()
        rows[34]["text"] += "\nDe momento, esto ha sido\ntodo."
        with self.assertRaisesRegex(ValueError, "found 2"):
            apply_errata(rows)

    def test_n64_to_xbox_buttons_in_english(self):
        raw = "Press [A] to jump, [B] to talk and [Z] to crouch. Use the [C] Buttons. Press [R]."
        got = convert(raw, "en")
        self.assertIn("A to jump", got)
        self.assertIn("X to talk", got)
        self.assertIn("LT/LB to crouch", got)
        self.assertIn("right stick", got)
        self.assertIn("RB/RT", got)
        self.assertFalse(LEGACY_RE.search(got))

    def test_n64_to_xbox_buttons_and_stick_in_spanish(self):
        raw = "Pulsa [A], [B], [Z], [R]. Mueve el stick de control. Usa [C]^ o [C]|."
        got = convert(raw, "es")
        self.assertIn("Pulsa A, X, LT/LB, RB/RT.", got)
        self.assertIn("stick izquierdo", got)
        self.assertIn("stick derecho arriba", got)
        self.assertIn("stick derecho abajo", got)
        self.assertFalse(LEGACY_RE.search(got))

    def test_right_stick_not_mistaken_for_movement(self):
        raw = "Usa el stick derecho para cámara y el stick para mover a Mario."
        got = convert(raw, "es")
        self.assertIn("stick derecho", got)
        self.assertIn("stick izquierdo para mover", got)
        self.assertNotIn("stick izquierdo derecho", got)

    def test_pt_br_rows_unchanged(self):
        rows = self.fixtures()
        pt = copy.deepcopy(rows)
        apply_errata(rows)
        self.assertEqual(pt[5], rows[5])
        self.assertEqual(pt[100], rows[100])
        self.assertEqual(len(rows), 170)


if __name__ == "__main__":
    unittest.main()
