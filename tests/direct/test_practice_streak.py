from pathlib import Path
import json

CONTRACT = Path(__file__).resolve().parents[2] / "contracts" / "practice_streak.py"
SDK = "v0.2.16"
PROMPT = "Assess one self-reported practice session"
RULE = "A session qualifies when the log names the exercise, records at least twenty focused minutes, and identifies one concrete observation. Partial means meaningful practice with one missing requirement."


def address(account):
    return "0x" + account.hex()


def deploy(vm, direct_deploy, coach):
    vm.sender = coach
    return direct_deploy(str(CONTRACT), "Community Sketch Practice", RULE, sdk_version=SDK)


def prepare(contract, vm, coach, first, second):
    contract.enroll_member("m1", address(first), "Blair")
    contract.enroll_member("m2", address(second), "Casey")
    contract.finish_enrollment()
    contract.open_round("Round One", "Practice drawing simple household objects using contour lines and record one observation about proportion.")
    vm.sender = first
    contract.log_practice("m1", "I spent 25 focused minutes drawing a mug and a lamp with contour lines. I noticed the mug handle was narrower than I first estimated.")
    vm.sender = second
    contract.log_practice("m2", "I spent 22 focused minutes drawing a kettle and a box with contour lines. I noticed the kettle body was wider relative to its handle.")
    vm.sender = coach
    contract.close_session_logging()


def test_round_scores_points_and_streaks(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    prepare(contract, direct_vm, direct_alice, direct_bob, direct_charlie)
    direct_vm.mock_llm(PROMPT, json.dumps({"result": "QUALIFIES", "focus_label": "Contour proportion"}))
    contract.assess_session("m1")
    leader = direct_vm._captured_validators[-1][0]
    direct_vm.clear_mocks()
    direct_vm.mock_llm(PROMPT, json.dumps({"result": "QUALIFIES", "focus_label": "Observed object proportions"}))
    assert direct_vm.run_validator(leader_result=leader) is True
    direct_vm.clear_mocks()
    direct_vm.mock_llm(PROMPT, json.dumps({"result": "REJECTED", "focus_label": "Unrelated activity"}))
    assert direct_vm.run_validator(leader_result=leader) is False
    direct_vm.clear_mocks()
    direct_vm.mock_llm(PROMPT, json.dumps({"result": "QUALIFIES", "focus_label": "Contour proportion"}))
    contract.assess_session("m2")
    contract.finalize_round()
    assert contract.get_member("m1")["total_points"] == 2
    assert contract.get_member("m1")["current_streak"] == 1


def test_named_member_and_single_log_are_enforced(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    contract.enroll_member("m1", address(direct_bob), "Blair")
    contract.enroll_member("m2", address(direct_charlie), "Casey")
    contract.finish_enrollment()
    contract.open_round("Round One", "Practice contour drawing for a focused interval and record one concrete observation about proportion.")
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("only_named_member"):
        contract.log_practice("m2", "This address cannot log a practice session on behalf of the other enrolled member in the active round.")
    contract.log_practice("m1", "I practiced contour lines for 25 minutes and observed that the handle was narrower than the cup body.")
    with direct_vm.expect_revert("session_already_logged"):
        contract.log_practice("m1", "A second session log from the same member must not replace the frozen first entry for this round.")


def test_peer_challenge_and_bad_result_fail_closed(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    prepare(contract, direct_vm, direct_alice, direct_bob, direct_charlie)
    direct_vm.mock_llm(PROMPT, json.dumps({"result": "PARTIAL", "focus_label": "Contour exercise"}))
    contract.assess_session("m1")
    direct_vm.sender = direct_charlie
    contract.challenge_session("m1", "The log explicitly states both 25 focused minutes and a concrete proportion observation, so both requirements are present.")
    direct_vm.clear_mocks()
    direct_vm.mock_llm(PROMPT, json.dumps({"result": "PASS", "focus_label": "Contour exercise"}))
    with direct_vm.expect_revert("invalid_result"):
        contract.assess_session("m1")
    assert contract.get_session(1, "m1")["state"] == "CHALLENGED"
    assert contract.get_state()["assessed_count"] == 0
