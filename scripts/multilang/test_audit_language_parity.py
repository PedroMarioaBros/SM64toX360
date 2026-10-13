"""Testa auditoria das classes de controles EN/ES sem usar ROMs/ativos."""
import copy
import unittest
from audit_language_parity import audit


class DialogueParityTests(unittest.TestCase):
    def fixtures(self):
        en=[{"id":i,"text":"Hello Mario."} for i in range(170)]
        es=[{"id":i,"text":"Hola Mario."} for i in range(170)]
        en[15]["text"]="Press [A] then [B] to kick."
        en[35]["text"]="Use the [C] controls; press [R] and the Control Stick."
        en[60]["text"]="Hold [Z] and press [A]."
        es[15]["text"]="Pulsa [A] y después [B] para dar una patada."
        es[35]["text"]="Usa [C]; pulsa [R] y el stick de control."
        es[60]["text"]="Mantén [Z] y pulsa [A]."
        enx=copy.deepcopy(en)
        esx=copy.deepcopy(es)
        enx[15]["text"]="Press A then X to kick."
        enx[35]["text"]="Use the right stick controls; press RB/RT and the left stick."
        enx[60]["text"]="Hold LT/LB and press A."
        esx[15]["text"]="Pulsa A y después X para dar una patada."
        esx[35]["text"]="Usa el stick derecho; pulsa RB/RT y el stick izquierdo."
        esx[60]["text"]="Mantén LT/LB y pulsa A."
        return en,enx,es,esx

    def test_matching_controller_classes_pass(self):
        report=audit(*self.fixtures(),pt_pool_sha="immutable")
        self.assertEqual(report["status"],"PASS_INPUT_CLASS_COVERAGE")
        self.assertEqual(report["missing_input_classes"],[])
        self.assertEqual(report["remaining_legacy_n64_tokens"],[])
        self.assertFalse(report["human_translation_parity_certified"])

    def test_missing_spanish_jump_stops_build(self):
        args=self.fixtures()
        args[3][15]["text"]="Pulsa X para dar una patada."
        report=audit(*args)
        self.assertEqual(report["status"],"FAIL_INPUT_CLASS_COVERAGE")
        self.assertIn("A",report["missing_input_classes"][0]["missing_es"])

    def test_legacy_button_reference_stops_build(self):
        args=self.fixtures()
        args[3][35]["text"]+=" Press [R] to change the camera."
        self.assertEqual(audit(*args)["status"],"FAIL_INPUT_CLASS_COVERAGE")

    def test_unlocalized_movement_stick_stops_build(self):
        args=self.fixtures()
        args[3][35]["text"]="Usa el stick de control y RB/RT."
        report=audit(*args)
        self.assertEqual(report["status"],"FAIL_INPUT_CLASS_COVERAGE")
        self.assertTrue(report["ambiguous_n64_analog_references"])

    def test_missing_id_stops_build(self):
        args=self.fixtures()
        args[3].pop()
        with self.assertRaisesRegex(ValueError,"IDs must"):
            audit(*args)


if __name__=="__main__":
    unittest.main()
