"""Exercise preview/build orchestration without Docker or network access."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import time
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCKER = r'''#!/usr/bin/env python3
import io, json, os, pathlib, sys, tarfile, time, uuid, fcntl
args = sys.argv[1:]
with open(os.environ["DOCKER_LOG"], "a") as log:
    log.write(json.dumps(args) + "\n")
state_path = pathlib.Path(os.environ["DOCKER_STATE"])
lock = open(str(state_path) + ".lock", "w")
fcntl.flock(lock, fcntl.LOCK_EX)
state = json.loads(state_path.read_text()) if state_path.exists() else {}
def save():
    temporary = state_path.with_suffix(".new")
    temporary.write_text(json.dumps(state))
    temporary.replace(state_path)
def target(key):
    return next((c for c in state.values() if c["id"] == key), None)
if args[0] == "container":
    action = args[1]
    if action == "ls":
        name = args[-1].removeprefix("name=^/").removesuffix("$")
        if name in state:
            print(state[name]["id"])
    elif action == "inspect":
        c = target(args[-1])
        if c is None:
            sys.exit(1)
        if "--format" in args:
            fmt = args[args.index("--format") + 1]
            if fmt == "{{.State.Status}}":
                print(c["status"])
            else:
                print("|".join(c["labels"].get("io.al-folio.preview." + k, "") for k in ("purpose", "repo", "port")))
        else:
            print(json.dumps(c))
    elif action == "unpause":
        c = target(args[-1])
        if c is None:
            sys.exit(1)
        c["status"] = "running"
        save()
    elif action in ("stop", "rm"):
        c = target(args[-1])
        if c is None:
            sys.exit(1)
        del state[c["name"]]
        save()
    sys.exit(0)
if args[0] == "create":
    name = args[args.index("--name") + 1]
    if name in state:
        sys.exit(1)
    labels = dict(args[i+1].split("=", 1) for i, a in enumerate(args) if a == "--label")
    c = dict(id=uuid.uuid4().hex, name=name, labels=labels, status="created")
    if os.environ.get("CREATE_RACE"):
        c["status"] = os.environ["CREATE_RACE"]
        state[name] = c
        save()
        sys.exit(1)
    if os.environ.get("FAIL_CREATE"):
        sys.exit(1)
    state[name] = c
    save()
    print(c["id"])
    sys.exit(0)
if args[0] == "start":
    c = target(args[-1])
    if c is None:
        sys.exit(1)
    if os.environ.get("FAIL_START"):
        print("Bind for 0.0.0.0:8086 failed: port is already allocated", file=sys.stderr)
        sys.exit(125)
    c["status"] = "running"
    save()
    fcntl.flock(lock, fcntl.LOCK_UN)
    if os.environ.get("HOLD_PREVIEW"):
        while any(x["id"] == c["id"] for x in json.loads(state_path.read_text()).values()):
            time.sleep(0.02)
    sys.exit(0)
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
                        DOCKER_LOG=str(self.log), SNAPSHOT_LOG=str(self.snapshot),
                        DOCKER_STATE=str(self.root / "state.json"))
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
                run = next(call for call in reversed(self.calls()) if call[0] == "create")
                self.assertIn(f"0.0.0.0:{8086 if port is None else 8087}:8080", run)
                self.assertIn("--watch", run[-1])
                self.assertIn("--force_polling", run[-1])
                self.assertNotIn("--no-watch", run[-1])
                self.assertNotIn("--baseurl", run[-1])

    def test_invalid_arguments_do_not_touch_docker(self):
        for args in (("0",), ("65536",), ("abc",), ("--rebuild", "8086"), ("8086", "extra"),
                     ("--help", "8086"), ("--stop", "abc"), ("--restart", "0"), ("--unknown",)):
            with self.subTest(args=args):
                result = self.run_preview(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("--help", result.stderr)
                self.assertFalse(result.stdout)
        self.assertFalse(self.log.exists())

    def state(self):
        path = Path(self.env["DOCKER_STATE"])
        return json.loads(path.read_text()) if path.exists() else {}

    def seed(self, port=8086, status="running", repo=None, foreign=False):
        repo = str(repo or self.repo.resolve())
        identity = hashlib.sha256(f"{repo}\0{port}".encode()).hexdigest()
        name = "al-folio-preview-" + identity
        c = dict(id=identity, name=name, status=status, labels={
            "io.al-folio.preview.purpose": "foreign" if foreign else "preview",
            "io.al-folio.preview.repo": repo,
            "io.al-folio.preview.port": str(port)})
        state = self.state()
        state[name] = c
        Path(self.env["DOCKER_STATE"]).write_text(json.dumps(state))
        return c

    def launch(self, *args):
        env = dict(self.env, HOLD_PREVIEW="1")
        proc = subprocess.Popen(["bash", str(self.repo / "bin/preview"), *args],
                                env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, start_new_session=True)
        def cleanup():
            if proc.poll() is None:
                proc.send_signal(signal.SIGTERM)
            proc.communicate(timeout=5)
        self.addCleanup(cleanup)
        return proc

    def await_running(self, old_id=None):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            try:
                matches = [c for c in self.state().values()
                           if c["status"] == "running" and c["id"] != old_id]
                if matches:
                    return matches[0]
            except json.JSONDecodeError:
                pass
            time.sleep(0.02)
        self.fail("Preview did not start")

    def test_help_without_docker(self):
        # Supply just Bash's startup dependencies, with no Docker executable.
        help_bin = self.root / "help-bin"
        help_bin.mkdir()
        for command in ("dirname", "cat"):
            (help_bin / command).symlink_to(shutil.which(command))
        outputs = []
        for flag in ("-h", "--help"):
            result = subprocess.run([shutil.which("bash"), str(self.repo / "bin/preview"), flag],
                                    env=dict(self.env, PATH=str(help_bin)), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            for text in ("--restart", "--stop", "--rebuild", "8086", "Examples:", "Ctrl+C"):
                self.assertIn(text, result.stdout)
            outputs.append(result.stdout)
        self.assertEqual(*outputs)
        self.assertFalse(self.log.exists())

    def test_repeated_start_reuses_foreground_instance(self):
        first = self.launch()
        self.await_running()
        result = self.run_preview()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("initial build", result.stdout)
        self.assertEqual(len([x for x in self.calls() if x[0] == "create"]), 1)
        self.assertIsNone(first.poll())
        os.killpg(first.pid, signal.SIGINT)
        first.communicate(timeout=5)
        self.assertEqual(first.returncode, 130)
        self.assertFalse(self.state())

    def test_restart_and_old_terminal_cleanup(self):
        first = self.launch()
        old = self.await_running()
        second = self.launch("--restart")
        new = self.await_running(old["id"])
        first.communicate(timeout=5)
        self.assertIn(new["name"], self.state())
        stopped = self.run_preview("--stop")
        self.assertEqual(stopped.returncode, 0, stopped.stderr)
        second.communicate(timeout=5)
        self.assertFalse(self.state())
        self.assertEqual(self.run_preview("--stop").returncode, 0)

    def test_instance_isolation_and_ownership(self):
        own = self.seed()
        self.seed(8087)
        other_repo = self.seed(repo=self.root / "other")
        self.assertEqual(self.run_preview("--stop", "08087").returncode, 0)
        self.assertEqual(set(self.state()), {own["name"], other_repo["name"]})
        foreign = self.seed(foreign=True)
        for args in ((), ("--restart",), ("--stop",)):
            self.assertNotEqual(self.run_preview(*args).returncode, 0)
        self.assertEqual(self.state()[foreign["name"]], foreign)

    def test_recovery_and_missing_restart(self):
        for status in ("exited", "dead"):
            self.seed(status=status)
            result = self.run_preview()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(self.state())
        self.assertEqual(self.run_preview("--restart", "8087").returncode, 0)
        self.seed(status="created")
        result = self.run_preview()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--restart", result.stderr)
        self.assertEqual(self.run_preview("--restart").returncode, 0)
        self.seed(status="paused")
        self.assertEqual(self.run_preview("--restart").returncode, 0)
        self.assertTrue(any(x[:2] == ["container", "unpause"] for x in self.calls()))

    def test_create_race_only_reuses_running_owner(self):
        self.env["CREATE_RACE"] = "running"
        self.assertEqual(self.run_preview().returncode, 0)
        self.assertFalse(any(x[:2] == ["container", "stop"] for x in self.calls()))
        self.run_preview("--stop")
        self.env["CREATE_RACE"] = "created"
        result = self.run_preview()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("startup may be in progress", result.stderr)

    def test_failures_clean_only_created_instance(self):
        other = self.seed(8087)
        self.env["FAIL_START"] = "1"
        result = self.run_preview()
        self.assertEqual(result.returncode, 125)
        self.assertIn("port is already allocated", result.stderr)
        self.assertIn("different port", result.stderr)
        self.assertEqual(set(self.state()), {other["name"]})
        self.env["FAIL_CREATE"] = "1"
        self.assertNotEqual(self.run_preview().returncode, 0)
        self.assertEqual(set(self.state()), {other["name"]})

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
