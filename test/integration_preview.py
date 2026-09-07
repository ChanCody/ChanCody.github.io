"""Exercise preview/build orchestration without Docker or network access."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCKER = r'''#!/usr/bin/env python3
import io, json, os, pathlib, sys, tarfile
args = sys.argv[1:]
with open(os.environ["DOCKER_LOG"], "a") as log:
    log.write(json.dumps(args) + "\n")
if args[0] == "run" and "-p" not in args:
    mount = args[args.index("-v") + 1].split(":")[0]
    with tarfile.open(pathlib.Path(mount) / "source.tar") as source:
        pathlib.Path(os.environ["SNAPSHOT_LOG"]).write_text(json.dumps(source.getnames()))
    if os.environ.get("FAIL_BUILD"):
        sys.exit(17)
    with tarfile.open(fileobj=sys.stdout.buffer, mode="w|") as output:
        data = b"fresh production output"
        entry = tarfile.TarInfo("index.html")
        entry.size = len(data)
        output.addfile(entry, io.BytesIO(data))
'''


class PreviewIntegration(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "site with spaces"
        (self.repo / "bin").mkdir(parents=True)
        for name in ("preview", "build-site", "build-production", "production.Dockerfile"):
            shutil.copy2(ROOT / "bin" / name, self.repo / "bin" / name)
        self.git("init", "-q")
        self.git("remote", "add", "origin", "git@github-alias:owner/site.git")
        (self.repo / "_config.yml").write_text("baseurl: ''\ngiscus:\n  repo: original\n")
        (self.repo / ".gitignore").write_text("_site/\nnode_modules/\n.jekyll-cache/\n")
        self.git("add", ".")
        (self.repo / "new page.md").write_text("uncommitted new page")
        (self.repo / "_site").mkdir()
        (self.repo / "_site" / "stale.html").write_text("old output")
        (self.repo / ".jekyll-cache").mkdir()
        (self.repo / ".jekyll-cache" / "old").write_text("cache")
        mock_bin = self.root / "mock-bin"
        mock_bin.mkdir()
        docker = mock_bin / "docker"
        docker.write_text(DOCKER)
        docker.chmod(0o755)
        self.log = self.root / "docker.jsonl"
        self.snapshot = self.root / "snapshot.json"
        self.env = dict(os.environ, PATH=f"{mock_bin}:{os.environ['PATH']}",
                        DOCKER_LOG=str(self.log), SNAPSHOT_LOG=str(self.snapshot))
        self.env.pop("GITHUB_REPOSITORY", None)

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)

    def run_preview(self, *args):
        return subprocess.run(["bash", str(self.repo / "bin/preview"), *args],
                              cwd=self.root, env=self.env, capture_output=True, text=True)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def test_preview_watches_and_preserves_port_interface(self):
        for port in (None, "08087"):
            with self.subTest(port=port):
                result = self.run_preview(*([] if port is None else [port]))
                self.assertEqual(result.returncode, 0, result.stderr)
                run = self.calls()[-1]
                self.assertIn(f"0.0.0.0:{8086 if port is None else 8087}:8080", run)
                self.assertIn("--watch", run[-1])
                self.assertIn("--force_polling", run[-1])
                self.assertNotIn("--no-watch", run[-1])
                self.assertNotIn("--baseurl", run[-1])

    def test_invalid_arguments_do_not_touch_docker(self):
        for args in (("0",), ("65536",), ("abc",), ("--rebuild", "8086"), ("8086", "extra")):
            with self.subTest(args=args):
                self.assertNotEqual(self.run_preview(*args).returncode, 0)
        self.assertFalse(self.log.exists())

    def test_rebuild_replaces_output_without_starting_server(self):
        original_config = (self.repo / "_config.yml").read_bytes()
        result = self.run_preview("--rebuild")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.repo / "_site/index.html").read_text(), "fresh production output")
        self.assertFalse((self.repo / "_site/stale.html").exists())
        self.assertEqual((self.repo / "_config.yml").read_bytes(), original_config)
        snapshot = json.loads(self.snapshot.read_text())
        self.assertIn("new page.md", snapshot)
        self.assertFalse(any(path.startswith(("_site/", ".jekyll-cache/")) for path in snapshot))
        calls = self.calls()
        build = next(call for call in calls if call[0] == "build")
        self.assertIn("--no-cache", build)
        self.assertIn("--pull", build)
        run = next(call for call in calls if call[0] == "run")
        self.assertIn("GITHUB_REPOSITORY=owner/site", run)
        self.assertNotIn("-p", run)
        self.assertFalse(any(call[0] in ("stop", "kill") for call in calls))

    def test_failed_build_keeps_previous_output(self):
        self.env["FAIL_BUILD"] = "1"
        result = self.run_preview("--rebuild")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.repo / "_site/stale.html").read_text(), "old output")
        self.assertNotIn("Production build complete", result.stdout)

    def test_ci_repository_overrides_origin(self):
        self.env["GITHUB_REPOSITORY"] = "fork/target"
        result = self.run_preview("--rebuild")
        self.assertEqual(result.returncode, 0, result.stderr)
        run = next(call for call in self.calls() if call[0] == "run")
        self.assertIn("GITHUB_REPOSITORY=fork/target", run)

    def test_deleted_files_are_absent_from_snapshot(self):
        (self.repo / "_config.yml").unlink()
        result = self.run_preview("--rebuild")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("_config.yml", json.loads(self.snapshot.read_text()))


if __name__ == "__main__":
    unittest.main()
