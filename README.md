# QuackLoan - IS212 Week 9 Lab

A small Flask fine checker with integration tests, an artifact smoke test, a Playwright browser journey, and a gated release pipeline.

## Run locally

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -v
python -m flask --app app run
```

Open `http://localhost:5000/`. Five days late costs $1.50 for a standard duck and $3.00 for a Deluxe duck. The first two days are free; each additional day costs $0.50, doubled for Deluxe, with a $5 cap per fine. Fines accumulate per member in `DuckFine`; the web endpoint calculates a fresh quote.

```sh
bash smoke.sh http://localhost:5000
python -m pip install playwright
python -m playwright install chromium
python -m unittest discover -s e2e -v
```

The E2E folder deliberately has no `__init__.py`; the unit/integration job does not discover browser tests.

## Pipeline and release evidence

`lint`, `test`, and `audit` run in parallel. Once all pass, `package` builds `quackloan.zip` once and generates an SPDX SBOM. `smoke` and `e2e` run that downloaded package. A push to protected `main` advances to `staging`; `production` waits for the GitHub environment's required reviewer (`nethren`). Pull requests never deploy.

The active staging and production jobs are explicit placeholders because AWS Academy Learner Lab access was unavailable. Their success does not mean a cloud application was deployed. `pipeline-with-aws-deploy.yml.txt` contains the inactive real-deployment version; replace the active workflow with it after configuration.

`test`, `lint`, `audit`, `smoke`, and `e2e` are required checks on `main` after the E2E change is integrated. Requiring PRs and enforcing the rule for administrators makes red checks a merge gate.

## Real AWS deployment, when access is available

1. Start the Learner Lab in `us-east-1`.
2. Create `quackloan-staging` and `quackloan-prod`: Python 3.13, x86_64, existing `LabRole`, function URL with auth `NONE`, handler `lambda_function.lambda_handler`.
3. For each matching GitHub environment, set `FUNCTION_NAME` and `FUNCTION_URL` variables. Set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN` as environment secrets using that session's temporary credentials.
4. Replace `.github/workflows/pipeline.yml` with `pipeline-with-aws-deploy.yml.txt` through a passing PR.
5. Inspect staging's smoke result, the staging page, and the checks before personally approving production. Compare the two deploy logs' `CodeSha256`: equal values show that the same zip was promoted.
6. End the Learner Lab when finished. Refresh environment credentials next session.

No credentials are included in this repository. Environment configuration and human approval are GitHub settings, not settings that YAML can create by itself.

## Repeat the local experiments

```sh
python -m pip install playwright
python -m playwright install chromium
python tools/verify_lab.py
```

The script uses fresh temporary artifact directories and reports actual results in `evidence/`. The local zip uses macOS dependencies and is for local verification. Download the Linux/Python 3.13 `quackloan-deployment-package` artifact from Actions for Lambda. Local checks use Python 3.14; CI checks use the course's Python 3.13.

The lab's missing-error-handler experiment is also recorded in `evidence/missing-error-handler.txt`; that temporary change was reverted.

## Sources and authorship

Prepared with Codex assistance on 13 October 2026. App, adapter, smoke script, pipeline and browser test are based on the instructor-provided `week9-lab-reference.zip` and the Week 9 lab appendices. The expanded fee tests derive their expected values from the Week 6 brief's fee rules. The integration tests exercise the real app and DuckFine; no part of the code under test is mocked.

Official references: *Week 9 Lab - From a Green Build to a Gated Release*, pp. 1-6 and Appendices A-D; *Week 6 Lab - From Generated Tests to a CI Gate*, p. 1. Course source documents are not distributed here. Review the code and test evidence and be able to explain each gate; green checks do not establish real-user validation or prove the absence of defects.

See `LAB_OUTPUT.md` for results, experiment evidence, and the remaining manual approval/AWS steps.
