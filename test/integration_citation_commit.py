"""Exercise the actual commit script against disposable local Git remotes."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'bin/commit-citations'


class CommitTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.repo = self.root / 'worker'
        self.other = self.root / 'other'
        self.remote = self.root / 'remote.git'
        self.env = dict(os.environ, GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_AUTHOR_NAME='CI Test', GIT_AUTHOR_EMAIL='ci@example.invalid',
                        GIT_COMMITTER_NAME='CI Test', GIT_COMMITTER_EMAIL='ci@example.invalid',
                        GITHUB_REF_NAME='main')
        self.git('init', '--bare', '--initial-branch=main', str(self.remote), cwd=self.root)
        self.git('clone', str(self.remote), str(self.repo), cwd=self.root)
        (self.repo / 'README.md').write_text('test\n')
        self.git('add', '.')
        self.git('commit', '-m', 'initial')
        self.git('push', '-u', 'origin', 'main')
        self.git('clone', str(self.remote), str(self.other), cwd=self.root)

    def git(self, *args, cwd=None):
        return subprocess.check_output(['git', *args], cwd=cwd or self.repo, env=self.env, stderr=subprocess.STDOUT, text=True).strip()

    def run_script(self):
        return subprocess.run(['bash', str(SCRIPT)], cwd=self.repo, env=self.env, capture_output=True, text=True)

    def write_citations(self, repo=None, value='papers: {}\n'):
        target = (repo or self.repo) / '_data/citations.yml'
        target.parent.mkdir(exist_ok=True)
        target.write_text(value)

    def test_new_file_push_and_no_change(self):
        self.write_citations()
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        head = self.git('rev-parse', 'HEAD')
        self.assertEqual(head, self.git('rev-parse', 'main', cwd=self.remote))
        self.assertEqual(self.run_script().returncode, 0)
        self.assertEqual(head, self.git('rev-parse', 'HEAD'))

    def test_remote_advance_is_preserved(self):
        (self.other / 'remote.txt').write_text('remote change\n')
        self.git('add', '.', cwd=self.other)
        self.git('commit', '-m', 'remote change', cwd=self.other)
        self.git('push', cwd=self.other)
        remote_head = self.git('rev-parse', 'HEAD', cwd=self.other)
        self.write_citations()
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.git('merge-base', '--is-ancestor', remote_head, 'HEAD')
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.git('rev-parse', 'main', cwd=self.remote))

    def test_conflict_does_not_overwrite_remote(self):
        self.write_citations(self.other, 'papers: {remote: {}}\n')
        self.git('add', '.', cwd=self.other)
        self.git('commit', '-m', 'remote citations', cwd=self.other)
        self.git('push', cwd=self.other)
        before = self.git('rev-parse', 'main', cwd=self.remote)
        self.write_citations()
        self.assertNotEqual(self.run_script().returncode, 0)
        self.assertEqual(before, self.git('rev-parse', 'main', cwd=self.remote))

    def test_missing_file_fails_without_commit(self):
        before = self.git('rev-parse', 'HEAD')
        self.assertNotEqual(self.run_script().returncode, 0)
        self.assertEqual(before, self.git('rev-parse', 'HEAD'))

    def test_unrelated_staged_changes_are_rejected(self):
        (self.repo / 'README.md').write_text('unrelated change\n')
        self.git('add', 'README.md')
        self.write_citations()
        before = self.git('rev-parse', 'HEAD')
        self.assertNotEqual(self.run_script().returncode, 0)
        self.assertEqual(before, self.git('rev-parse', 'HEAD'))


if __name__ == '__main__':
    unittest.main()
