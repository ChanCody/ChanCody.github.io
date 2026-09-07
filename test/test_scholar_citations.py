"""Regression tests at the Scholar client and atomic-file boundaries."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import yaml

spec = importlib.util.spec_from_file_location('citations', Path(__file__).resolve().parents[1] / 'bin/update_scholar_citations.py')
citations = importlib.util.module_from_spec(spec)
spec.loader.exec_module(citations)


class CitationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.output = Path(self.directory.name) / 'citations.yml'
        self.client = Mock()
        self.client.fill.return_value = {'publications': [
            {'author_pub_id': 'author:paper', 'bib': {'title': 'Paper', 'pub_year': '2025'}, 'num_citations': 3}
        ]}
        identity = patch.object(citations, 'load_scholar_user_id', return_value='test-author')
        identity.start()
        self.addCleanup(identity.stop)

    def update(self):
        return citations.get_scholar_citations(self.client, self.output)

    def old_data(self, count=2):
        self.output.write_text(yaml.safe_dump({
            'metadata': {'last_updated': '2020-01-01'},
            'papers': {'author:paper': {'title': 'Paper', 'year': '2025', 'citations': count}}
        }))
        return self.output.read_bytes()

    def test_first_creation(self):
        self.assertTrue(self.update())
        self.assertEqual(yaml.safe_load(self.output.read_text())['papers']['author:paper']['citations'], 3)

    def test_changed_data(self):
        self.old_data()
        self.assertTrue(self.update())
        self.assertEqual(yaml.safe_load(self.output.read_text())['papers']['author:paper']['citations'], 3)

    def test_unchanged_data_does_not_rewrite(self):
        before = self.old_data(3)
        self.assertFalse(self.update())
        self.assertEqual(before, self.output.read_bytes())

    def test_updated_today_skips_network(self):
        self.update()
        self.client.reset_mock()
        self.assertFalse(self.update())
        self.client.fill.assert_not_called()

    def test_corrupt_data_is_preserved(self):
        for value in ['invalid: [', '[]', '{}', 'papers: {}\nmetadata: []']:
            with self.subTest(value=value):
                self.output.write_text(value)
                with self.assertRaises((ValueError, yaml.YAMLError)):
                    self.update()
                self.assertEqual(value, self.output.read_text())
        self.client.fill.assert_not_called()

    def test_network_failure_or_timeout_preserves_old_data(self):
        before = self.old_data()
        for error in [RuntimeError('network unavailable'), TimeoutError('timed out')]:
            with self.subTest(error=error):
                self.client.fill.side_effect = error
                with self.assertRaises(type(error)):
                    self.update()
                self.assertEqual(before, self.output.read_bytes())

    def test_failed_first_fetch_does_not_create_file(self):
        self.client.fill.side_effect = RuntimeError('unavailable')
        with self.assertRaises(RuntimeError):
            self.update()
        self.assertFalse(self.output.exists())

    def test_partial_response_is_not_written(self):
        before = self.old_data()
        for response in [None, {}, {'publications': [{}]}, {'publications': [None]}]:
            with self.subTest(response=response):
                self.client.fill.return_value = response
                with self.assertRaises((ValueError, AttributeError)):
                    self.update()
                self.assertEqual(before, self.output.read_bytes())

    def test_failed_replace_preserves_old_data_and_cleans_temporary_file(self):
        before = self.old_data()
        with patch.object(os, 'replace', side_effect=OSError('write failed')):
            with self.assertRaises(OSError):
                self.update()
        self.assertEqual(before, self.output.read_bytes())
        self.assertEqual(list(self.output.parent.iterdir()), [self.output])


if __name__ == '__main__':
    unittest.main()
