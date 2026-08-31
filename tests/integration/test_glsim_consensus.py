from __future__ import annotations
import json
from pathlib import Path
from gltest import get_contract_factory, get_validator_factory
from gltest.accounts import create_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address

PROMPT = "Assess one self-reported practice session"


def context():
    validators = get_validator_factory().batch_create_mock_validators(5, mock_llm_response={"nondet_exec_prompt": {PROMPT: json.dumps({"evidence_mask": "1111", "focus_label": "Contour proportion"})}})
    return {"validators": [validator.to_dict() for validator in validators]}


def ok(receipt):
    assert tx_execution_succeeded(receipt)


def test_five_validator_practice_round():
    coach_account, first_account, second_account = create_accounts(3)
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "practice_streak.py")
    deployed = factory.deploy_contract_tx(args=["Community Sketch Practice", "A session qualifies when the log names the exercise, records at least twenty focused minutes, and gives one concrete observation. Partial means one requirement is missing."], account=coach_account, wait_transaction_status=TransactionStatus.FINALIZED)
    ok(deployed)
    contract_address = extract_contract_address(deployed)
    coach = factory.build_contract(contract_address, account=coach_account)
    first = factory.build_contract(contract_address, account=first_account)
    second = factory.build_contract(contract_address, account=second_account)
    ok(coach.enroll_member(args=["m1", first_account.address, "Blair"]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(coach.enroll_member(args=["m2", second_account.address, "Casey"]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(coach.finish_enrollment(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(coach.open_round(args=["Round One", "Practice household-object contour lines and record one observation about proportion."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(first.log_practice(args=["m1", "I spent 25 focused minutes drawing a mug and lamp with contour lines and noticed the handle was narrower than expected."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(second.log_practice(args=["m2", "I spent 22 focused minutes drawing a kettle and box with contour lines and noticed the kettle body was wider than its handle."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(coach.close_session_logging(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(coach.assess_session(args=["m1"]).transact(transaction_context=context(), wait_transaction_status=TransactionStatus.FINALIZED))
    ok(coach.assess_session(args=["m2"]).transact(transaction_context=context(), wait_transaction_status=TransactionStatus.FINALIZED))
    ok(coach.finalize_round(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    assert coach.get_member(args=["m1"]).call()["current_streak"] == 1
