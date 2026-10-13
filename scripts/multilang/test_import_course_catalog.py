"""Testes de alinhamento 15 cursos x 6 missões entre inglês e espanhol."""
import copy
import json
import unittest
from import_course_catalog import (
    parse_course_source,apply_spanish_course_errata,audit_course_alignment
)


def fixture_text(es=False):
    text=[]
    for i in range(15):
        key=("COURSE_WF" if i==1 else f"COURSE_{i:02}")
        acts=[f"ACT_{j}" for j in range(6)]
        if es and i==1:
            acts[3]="MONEDAS ROJAS EN LA ISLA FLOANTE"
        labels=[f" {i+1} COURSE"]+acts
        text.append("COURSE_ACTS("+key+", "+", ".join('_("'+z+'")' for z in labels)+")")
    for i in range(10):
        text.append(f'SECRET_STAR(COURSE_S{i:02}, _("SECRET_{i}"))')
    text.append('CASTLE_SECRET_STARS(_("CASTLE STARS"))')
    for i in range(7):
        text.append(f'EXTRA_TEXT({i}, _("EXTRA_{i}"))')
    return "\n".join(text)


class CourseCatalogTests(unittest.TestCase):
    def test_all_courses_and_missions_match_structure(self):
        en=parse_course_source(fixture_text())
        es=parse_course_source(fixture_text(es=True))
        corrections=apply_spanish_course_errata(es)
        report=audit_course_alignment(en,es)
        self.assertEqual(report["named_missions"],90)
        self.assertEqual(report["main_courses"],15)
        self.assertEqual(len(corrections),1)
        self.assertIn("ISLA FLOTANTE",es["courses"]["COURSE_WF"]["acts"][3])

    def test_json_roundtrip_preserves_valid_extra_ids(self):
        # JSON converts numeric object keys to strings. This MUST remain
        # compatible with the real private TEST3 staging pipeline.
        en=json.loads(json.dumps(parse_course_source(fixture_text())))
        es=json.loads(json.dumps(parse_course_source(fixture_text(es=True))))
        report=audit_course_alignment(en,es)
        self.assertEqual(report["status"],"PASS_STAGE_ID_ALIGNMENT")
        self.assertEqual(report["auxiliary_strings"],7)

    def test_duplicate_source_id_is_rejected(self):
        source=fixture_text().replace("COURSE_ACTS(COURSE_00", "COURSE_ACTS(COURSE_WF")
        with self.assertRaisesRegex(ValueError,"duplicate course"):
            parse_course_source(source)

    def test_missing_act_rejected(self):
        source=fixture_text().replace('_("ACT_5")', "", 1)
        with self.assertRaisesRegex(ValueError,"malformed course"):
            parse_course_source(source)

    def test_order_divergence_rejected(self):
        en=parse_course_source(fixture_text())
        es=parse_course_source(fixture_text(es=True))
        a=es["courses"].pop("COURSE_00")
        es["courses"]["COURSE_00"]=a
        with self.assertRaisesRegex(ValueError,"course"):
            audit_course_alignment(en,es)

    def test_unexpected_spanish_edit_anchor_rejected(self):
        es=parse_course_source(fixture_text(es=True))
        es["courses"]["COURSE_WF"]["acts"][3]="WRONG"
        with self.assertRaisesRegex(ValueError,"unexpected source text"):
            apply_spanish_course_errata(es)


if __name__=="__main__":
    unittest.main()
