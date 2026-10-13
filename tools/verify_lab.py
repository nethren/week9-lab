"""Run local artifact checks and the lab's deliberate regressions.

This script uses the installed runtime dependencies for a macOS package.
GitHub Actions builds the Linux/Python 3.13 release package separately.
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from importlib.metadata import distribution
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
PYTHON = sys.executable


def run(label, args, **kwargs):
    result = subprocess.run(args, check=False, capture_output=True, text=True, **kwargs)
    (EVIDENCE / f"{label}.txt").write_text(result.stdout + result.stderr)
    return result.returncode


def build(directory, app_text, omit_duck=False):
    for name in ("Flask", "apig-wsgi", "blinker", "click", "itsdangerous",
                 "Jinja2", "MarkupSafe", "Werkzeug"):
        dist = distribution(name)
        for relative in dist.files:
            if ".." in relative.parts or "__pycache__" in relative.parts:
                continue
            source = dist.locate_file(relative)
            if source.is_file() and relative.suffix != ".pyc":
                dest = directory / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
    (directory / "app.py").write_text(app_text)
    shutil.copy2(ROOT / "lambda_function.py", directory / "lambda_function.py")
    if not omit_duck:
        shutil.copy2(ROOT / "duckfine.py", directory / "duckfine.py")


def artifact_checks(label, directory, browser=True):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", BASE_URL=base)
    env.pop("PYTHONPATH", None)
    with (EVIDENCE / f"{label}-app.txt").open("w") as log:
        proc = subprocess.Popen(
            [PYTHON, "-B", "-m", "flask", "--app", "app", "run",
             "--host", "127.0.0.1", "--port", str(port)],
            cwd=directory, env=env, stdout=log, stderr=log,
        )
        try:
            ready = False
            for _ in range(100):
                if proc.poll() is not None:
                    break
                try:
                    with urllib.request.urlopen(base + "/health", timeout=0.2) as response:
                        ready = json.load(response) == {"status": "ok"}
                    if ready:
                        break
                except (OSError, ValueError):
                    time.sleep(0.1)
            if not ready:
                return {"app_start": False, "smoke": "blocked", "e2e": "blocked"}
            smoke = run(f"{label}-smoke", ["bash", str(ROOT / "smoke.sh"), base], cwd=directory, env=env)
            e2e = run(f"{label}-e2e", [PYTHON, "-B", "-m", "unittest", "discover", "-s", str(ROOT / "e2e"), "-v"], cwd=directory, env=env) if browser else None
            if label == "healthy":
                with urllib.request.urlopen(base + "/fine?days=5&deluxe=1") as response:
                    (EVIDENCE / "sample-response.json").write_text(json.dumps(json.load(response), indent=2) + "\n")
                from playwright.sync_api import sync_playwright
                with sync_playwright() as pw:
                    chromium = pw.chromium.launch()
                    try:
                        page = chromium.new_page(viewport={"width": 960, "height": 540})
                        page.goto(base)
                        page.get_by_label("Days late").fill("5")
                        page.get_by_label("Deluxe duck").check()
                        page.get_by_role("button", name="Check fine").click()
                        page.get_by_role("status").wait_for()
                        page.screenshot(path=str(EVIDENCE / "fine-checker.png"))
                    finally:
                        chromium.close()
            return {"app_start": True, "smoke_exit": smoke, "e2e_exit": e2e}
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


def main():
    os.chdir(ROOT)
    EVIDENCE.mkdir(exist_ok=True)
    app = (ROOT / "app.py").read_text()
    results = {"source_tests_exit": run("final-tests", [PYTHON, "-B", "-m", "unittest", "discover", "-v"])}
    for label, text, omit in [
        ("healthy", app, False),
        ("checkbox-mutation", app.replace('type="checkbox" value="1"', 'type="checkbox"'), False),
        ("packaging-mutation", app, True),
    ]:
        with tempfile.TemporaryDirectory(prefix=f"quackloan-{label}-") as temp:
            directory = Path(temp)
            build(directory, text, omit)
            # Tests run with the mutant web layer but the real fee calculation.
            if label == "checkbox-mutation":
                for test in ("test_duckfine.py", "test_app.py"):
                    shutil.copy2(ROOT / test, directory / test)
                results["checkbox_source_tests_exit"] = run("checkbox-mutation-source-tests", [PYTHON, "-B", "-m", "unittest", "discover", "-v"], cwd=directory)
            results[label] = artifact_checks(label, directory)
            if label == "healthy":
                with ZipFile(ROOT / "quackloan-local.zip", "w", ZIP_DEFLATED) as archive:
                    for file in directory.rglob("*"):
                        if file.is_file():
                            archive.write(file, file.relative_to(directory))
    (EVIDENCE / "local-results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))
    assert results["source_tests_exit"] == 0
    assert results["healthy"] == {"app_start": True, "smoke_exit": 0, "e2e_exit": 0}
    assert results["checkbox_source_tests_exit"] == 0
    assert results["checkbox-mutation"]["smoke_exit"] == 0
    assert results["checkbox-mutation"]["e2e_exit"] != 0
    assert results["packaging-mutation"]["app_start"] is False


if __name__ == "__main__":
    main()
