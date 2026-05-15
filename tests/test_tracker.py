import unittest
import pandas as pd
import re
from main import calculate_progress


class TestCoreProgressLogic(unittest.TestCase):

    def setUp(self):
        # Mock Curriculum Setup
        self.core_df = pd.DataFrame(
            {
                "course_code": ["DS-501", "DS-502", "STATS-400"],
                "sections": ["Data Foundations", "Data Foundations", "Advanced Stats"],
                "categories": [
                    "KNOWLEDGE AND UNDERSTANDING",
                    "KNOWLEDGE AND UNDERSTANDING",
                    "KNOWLEDGE AND UNDERSTANDING",
                ],
                "section_credit_min": [3.0, 3.0, 3.0],
                "section_credit_max": [6.0, 6.0, 4.0],
            }
        )

    def test_calculate_progress_standard(self):
        # Student takes exactly what is required
        registrations = pd.DataFrame(
            {
                "code": ["DS-501", "STATS-400"],
                "grade": ["A", ""],  # DS-501 completed, STATS-400 in progress
                "section": ["Data Foundations", "Advanced Stats"],
                "credits": [3.0, 4.0],
                "is_transfer": [False, False],
            }
        )

        comp, ip, ip_codes, rem, rem_details = calculate_progress(
            registrations, self.core_df
        )

        self.assertEqual(comp.get("Data Foundations"), 3.0)
        self.assertEqual(ip.get("Advanced Stats"), 4.0)
        self.assertIn("STATS-400", ip_codes)
        self.assertNotIn("DS-501", ip_codes)

    def test_fuzzy_matching_unassigned(self):
        # Course not in core CSV but matches section text
        registrations = pd.DataFrame(
            {
                "code": ["DS-999"],
                "grade": ["B"],
                "section": ["Data Foundations Override"],
                "credits": [3.0],
                "is_transfer": [False],
            }
        )

        comp, ip, ip_codes, rem, rem_details = calculate_progress(
            registrations, self.core_df
        )

        self.assertEqual(rem.get("Data Foundations"), 3.0)
        self.assertEqual(rem_details["Data Foundations"][0]["code"], "DS-999")

    def test_transfer_ap_regex_logic(self):
        # Simulates the regex scraping done in the main() function on transcript load
        raw_registrations = pd.Series(
            [
                "COMM 101 - Oral Rhetoric (Transfer Credit)",
                "HIST CORE - AP/Transfer History Core",
                "PHYS 221 - General Physics (Repeat)",
                "APPLIED MATH 101",
            ]
        )

        is_transfers = raw_registrations.str.contains(
            r"(?i)(transfer|\bap\b)", na=False
        ).tolist()

        # Expected: True (Transfer), True (AP/Transfer), False (Repeat), False (APPLIED has 'AP' but not as word boundary)
        self.assertEqual(is_transfers, [True, True, False, False])

    def test_empty_dataframe_handling(self):
        # Handle blank submissions gracefully
        empty_df = pd.DataFrame()
        comp, ip, ip_codes, rem, rem_details = calculate_progress(
            empty_df, self.core_df
        )

        self.assertEqual(comp, {})
        self.assertEqual(ip, {})
        self.assertEqual(len(ip_codes), 0)


if __name__ == "__main__":
    unittest.main()
