import unittest

import helper
from preprocessor import preprocess


CHAT = """12/08/24, 9:05 am - Alice: Hello 😊 https://example.com
12/08/24, 10:15 - Bob: <Media omitted>
12/08/24, 11:00 - Alice: second line
continues here
12/08/24, 12:00 - Alice changed the group description
"""


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.df = preprocess(CHAT)

    def test_parses_common_timestamp_variants_and_multiline_messages(self):
        self.assertEqual(len(self.df), 4)
        self.assertEqual(self.df.loc[0, "user"], "Alice")
        self.assertIn("continues here", self.df.loc[2, "message"])
        self.assertEqual(self.df.loc[3, "user"], "group notification")

    def test_stats_and_empty_optional_analyses_are_safe(self):
        self.assertEqual(helper.fetch_stats("Overall", self.df), (4, 14, 1, 1))
        self.assertEqual(helper.emoji_helper("Bob", self.df).shape[0], 0)
        self.assertIsNone(helper.create_cloud("Bob", self.df))
        self.assertEqual(helper.activity_heatmap("Overall", self.df).shape, (7, 24))

    def test_rejects_non_chat_content(self):
        with self.assertRaises(ValueError):
            preprocess("This is not an exported WhatsApp chat.")


if __name__ == "__main__":
    unittest.main()
