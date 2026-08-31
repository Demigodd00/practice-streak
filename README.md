# Practice Streak

Runs sequential low-stakes practice rounds where members submit their own session logs, semantic assessment awards fixed points, and streak arithmetic stays on-chain.

## Why it is an Intelligent Contract

Validators independently bind a four-part evidence mask for objective alignment, exercise identification, duration or effort, and a concrete observation. The contract stores that intermediate evidence record, derives QUALIFIES, PARTIAL, or REJECTED, and computes points and streaks deterministically. A peer challenge provides a bounded reassessment loop without adding new evidence.

## Reusable deployment model

Deploy once per practice group. A deployment supports ten enrolled members and twenty-four rounds; reuse the source for a different hobby or practice rule.

One completed deployment is an auditable record and is not reset or silently repurposed. Reuse means deploying the same reviewed source with new constructor data.

## Roles and workflow

A coach enrolls addresses and opens/closes rounds; each named member logs their own session; another enrolled peer may challenge one assessment.

State path: `ENROLLING → READY_FOR_ROUND → LOGGING_SESSIONS → ASSESSING_SESSIONS → READY_FOR_ROUND or COMPLETE`

## Evidence boundary

Program rule, round label/objective, member self-report, and an optional peer challenge.

The only evidence is the stored practice rule, round objective, self-report, and peer challenge. No wearable, camera, school, employer, or identity data is collected.

## Core invariants

- Only the enrolled address can submit its member ID's log.
- A member cannot challenge their own session assessment.
- The model never supplies a result or points; both are derived from the agreed evidence mask.

## Public interface

Write methods: `assess_session, challenge_session, close_program, close_session_logging, enroll_member, finalize_round, finish_enrollment, log_practice, open_round`

View methods: `get_member, get_policy, get_session, get_state`

`get_policy` exposes the machine-readable operating boundary and confirms that this contract never custodies funds.

## Verification

Pinned GenVM runner: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`

```powershell
python -m pip install -r requirements.txt
genvm-lint check contracts/practice_streak.py
genvm-lint typecheck contracts/practice_streak.py
pytest tests/direct -q
python tests/run_glsim.py --port 4000 --validators 5 --no-browser
gltest tests/integration/test_glsim_consensus.py --network localnet -q
```

The StudioNet smoke test is opt-in and requires three disposable owner-specific test accounts. It reads state using `LATEST_FINAL` and asserts successful finalized execution.

## Previous StudioNet deployment (superseded)

These links and the recorded source hash refer to the earlier category-only implementation. Redeploy the evidence-mask version and replace this section before submission.

- Contract: https://explorer-studio.genlayer.com/address/0x019291B60089737Ef73B12aD3E30C553c7BF8cDD
- Studio import: https://studio.genlayer.com/?import-contract=0x019291B60089737Ef73B12aD3E30C553c7BF8cDD
- Deployment transaction: https://explorer-studio.genlayer.com/tx/0xc481b49c4d0c88ec4ac1fb815e096656560f8f587ee433c1b9e2b08361466f7a
- Intelligent transaction: https://explorer-studio.genlayer.com/tx/0x4e386f3b11058bf8a24ce7ecc53eb6f8b741e93d87f7d86911f9f0b9aa7d3bb6
- Observed legacy final-state sample: `{"focus_label": "Observational sketching of object proportions", "result": "QUALIFIES"}`
- Audited source SHA-256: `d1f1c53ab65a4ef44874bdbceda8e6aa314502789e7c9f7aceff84c0c2b594fe`

## Limitations

- Session logs are self-reported and are not proof that an activity occurred.
- Every member must log before the coach can advance a round.
- The contract must not be used for health, employment, school admission, or other high-stakes evaluation.

## Repository map

- `contracts/practice_streak.py` — Intelligent Contract source
- `tests/direct` — fast leader/validator and lifecycle tests
- `tests/integration/test_glsim_consensus.py` — five-validator simulator flow
- `tests/integration/test_studionet_smoke.py` — live opt-in proof
- `deployments/studionet.json` — source-bound public deployment evidence
- `ARCHITECTURE.md`, `SOURCE_POLICY.md`, `SECURITY.md`, `AUDIT.md` — review material

License: MIT.
