import json
from pathlib import Path

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionHashVariant, TransactionStatus
from gltest.utils import extract_contract_address


def ok(receipt):
    assert tx_execution_succeeded(receipt)
    assert receipt.get("status_name") == TransactionStatus.FINALIZED.value
    assert receipt.get("result_name") in (None, "AGREE", "MAJORITY_AGREE")
    assert receipt.get("tx_execution_result_name") in (None, "FINISHED_WITH_RETURN")
    return receipt


@pytest.mark.integration
def test_studionet_practice_assessment(
    default_account, secondary_account, tertiary_account
):
    factory = get_contract_factory(
        contract_file_path=Path(__file__).resolve().parents[2]
        / "contracts"
        / "practice_streak.py"
    )
    deployed = ok(
        factory.deploy_contract_tx(
            args=[
                "Community Sketch Practice",
                "A session qualifies when its log explicitly describes at least twenty minutes of observation sketching and names one visual element practiced; shorter but relevant work is partial.",
            ],
            account=default_account,
            wait_transaction_status=TransactionStatus.FINALIZED,
        )
    )
    address = extract_contract_address(deployed)
    coach = factory.build_contract(address, account=default_account)
    member_one = factory.build_contract(address, account=secondary_account)
    member_two = factory.build_contract(address, account=tertiary_account)
    ok(
        coach.enroll_member(
            args=["m1", secondary_account.address, "Ari"]
        ).transact(wait_transaction_status=TransactionStatus.FINALIZED)
    )
    ok(
        coach.enroll_member(
            args=["m2", tertiary_account.address, "Bea"]
        ).transact(wait_transaction_status=TransactionStatus.FINALIZED)
    )
    ok(
        coach.finish_enrollment(args=[]).transact(
            wait_transaction_status=TransactionStatus.FINALIZED
        )
    )
    ok(
        coach.open_round(
            args=[
                "Round One",
                "Practice observing a household object and recording its proportions, edges, or shadows.",
            ]
        ).transact(wait_transaction_status=TransactionStatus.FINALIZED)
    )
    ok(
        member_one.log_practice(
            args=[
                "m1",
                "I spent twenty-five minutes sketching a desk lamp from observation and focused on the proportion between its shade, arm, and base.",
            ]
        ).transact(wait_transaction_status=TransactionStatus.FINALIZED)
    )
    ok(
        member_two.log_practice(
            args=[
                "m2",
                "I spent twenty-two minutes drawing a ceramic mug from observation and practiced the curved rim, handle edges, and cast shadow.",
            ]
        ).transact(wait_transaction_status=TransactionStatus.FINALIZED)
    )
    ok(
        coach.close_session_logging(args=[]).transact(
            wait_transaction_status=TransactionStatus.FINALIZED
        )
    )
    intelligent = ok(
        coach.assess_session(args=["m1"]).transact(
            wait_transaction_status=TransactionStatus.FINALIZED
        )
    )
    session = coach.get_session(args=[1, "m1"]).call(transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)
    assert session["result"] in ("QUALIFIES", "PARTIAL", "REJECTED")
    assert 3 <= len(session["focus_label"]) <= 160
    observed = {
        "result": session["result"],
        "focus_label": session["focus_label"],
    }
    print(
        "STUDIONET_RECORD="
        + json.dumps(
            {
                "address": address,
                "deploy_tx": deployed["hash"],
                "intelligent_tx": intelligent["hash"],
                "observed": observed,
            },
            sort_keys=True,
        )
    )
