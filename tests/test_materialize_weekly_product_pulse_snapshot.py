from __future__ import annotations

import datetime as dt
import importlib.util
from pathlib import Path


MODULE_PATH = Path(
    "/docker/chummercomplete/chummer-design/scripts/ai/materialize_weekly_product_pulse_snapshot.py"
)
SPEC = importlib.util.spec_from_file_location(
    "materialize_weekly_product_pulse_snapshot", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
weekly = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(weekly)


def test_successor_dependency_posture_reports_open_dependencies(tmp_path: Path) -> None:
    registry = tmp_path / "NEXT_90_DAY_PRODUCT_ADVANCE_REGISTRY.yaml"
    registry.write_text(
        "\n".join(
            [
                "milestones:",
                "  - id: 101",
                "    status: complete",
                "  - id: 102",
                "    status: in_progress",
                "  - id: 106",
                "    dependencies: [101, 102]",
                "",
            ]
        ),
        encoding="utf-8",
    )

    posture = weekly._successor_dependency_posture(registry)

    assert posture["state"] == "blocked"
    assert posture["dependency_ids"] == [101, 102]
    assert posture["open_dependency_ids"] == [102]
    assert posture["summary"] == (
        "Successor launch dependencies remain open in the next-90-day registry: 102."
    )


def test_successor_dependency_posture_reports_open_work_tasks_on_complete_dependency(tmp_path: Path) -> None:
    registry = tmp_path / "NEXT_90_DAY_PRODUCT_ADVANCE_REGISTRY.yaml"
    registry.write_text(
        "\n".join(
            [
                "milestones:",
                "  - id: 101",
                "    status: complete",
                "    work_tasks:",
                "      - id: 101.4",
                "        status: in_progress",
                "  - id: 106",
                "    dependencies: [101]",
                "",
            ]
        ),
        encoding="utf-8",
    )

    posture = weekly._successor_dependency_posture(registry)

    assert posture["state"] == "blocked"
    assert posture["open_dependency_ids"] == [101]
    assert posture["open_dependency_work_task_ids"] == ["101.4"]
    assert posture["summary"] == (
        "Successor launch dependency work tasks remain open in the next-90-day registry: "
        "101.4."
    )


def test_launch_readiness_summary_holds_on_open_successor_dependencies() -> None:
    summary = weekly._launch_readiness_summary(
        journey_gate_health={"blocked_count": 0},
        blocked_journeys=False,
        local_release_proof={"status": "passed"},
        flagship_readiness={"state": "ready"},
        provider_route_stewardship={"canary_status": "Canary green on all active lanes"},
        closure_health={"state": "clear"},
        successor_dependency_posture={"open_dependency_ids": [101, 102]},
        status_plane={"whole_product_final_claim_status": "pass"},
        active_wave_status="in_progress",
    )

    assert summary == (
        "Hold launch expansion until successor dependency milestone(s) 101, 102 "
        "close in the next-90-day registry."
    )


def test_launch_readiness_summary_holds_on_open_successor_dependency_work_tasks() -> None:
    summary = weekly._launch_readiness_summary(
        journey_gate_health={"blocked_count": 0},
        blocked_journeys=False,
        local_release_proof={"status": "passed"},
        flagship_readiness={"state": "ready"},
        provider_route_stewardship={"canary_status": "Canary green on all active lanes"},
        closure_health={"state": "clear"},
        successor_dependency_posture={
            "open_dependency_ids": [101],
            "open_dependency_work_task_ids": ["101.4", "102.2"],
        },
        status_plane={"whole_product_final_claim_status": "pass"},
        active_wave_status="in_progress",
    )

    assert summary == (
        "Hold launch expansion until successor dependency work task(s) 101.4, 102.2 "
        "close in the next-90-day registry."
    )


def test_launch_readiness_summary_holds_on_status_plane_final_claim() -> None:
    summary = weekly._launch_readiness_summary(
        journey_gate_health={"blocked_count": 0},
        blocked_journeys=False,
        local_release_proof={"status": "passed"},
        flagship_readiness={"state": "ready"},
        provider_route_stewardship={"canary_status": "Canary green on all active lanes"},
        closure_health={"state": "clear"},
        successor_dependency_posture={"open_dependency_ids": []},
        status_plane={"whole_product_final_claim_status": "warning"},
        active_wave_status="in_progress",
    )

    assert summary == (
        "Hold launch expansion until the whole-product final claim returns to pass "
        "(current: warning)."
    )


def test_launch_readiness_summary_holds_on_flagship_readiness_gap() -> None:
    summary = weekly._launch_readiness_summary(
        journey_gate_health={"blocked_count": 0},
        blocked_journeys=False,
        local_release_proof={"status": "passed"},
        flagship_readiness={"state": "watch"},
        provider_route_stewardship={"canary_status": "Canary green on all active lanes"},
        closure_health={"state": "clear"},
        successor_dependency_posture={"open_dependency_ids": []},
        status_plane={"whole_product_final_claim_status": "pass"},
        active_wave_status="in_progress",
    )

    assert summary == (
        "Hold launch expansion until published flagship readiness proof returns to ready posture."
    )


def test_governor_decisions_freeze_when_successor_dependencies_are_open() -> None:
    decisions = weekly._governor_decisions(
        dt.date(2026, 4, 20),
        {
            "overall_progress_percent": 91,
            "history_snapshot_count": 8,
            "phase_label": "Scale & stabilize",
        },
        "Campaign Breadth and Promotion",
        0,
        active_wave_status="in_progress",
        journey_gate_health={"state": "ready", "blocked_count": 0},
        closure_health={"state": "clear"},
        provider_route_stewardship={"canary_status": "Canary green on all active lanes"},
        local_release_proof={"status": "passed"},
        flagship_readiness={"state": "ready", "proof_status": "pass"},
        successor_dependency_posture={"state": "blocked", "open_dependency_ids": [101, 102]},
        status_plane={"whole_product_final_claim_status": "pass"},
        blocked_journeys=False,
        next20_closed=False,
        post_audit_closed=False,
    )

    launch_decision = decisions[1]
    assert launch_decision["action"] == "freeze_launch"
    assert launch_decision["reason"] == (
        "Freeze launch expansion until successor dependency milestone(s) 101, 102 "
        "close in the next-90-day registry."
    )
    assert "successor_dependency_state=blocked" in launch_decision["cited_signals"]
    assert "successor_open_dependency_ids=101,102" in launch_decision["cited_signals"]


def test_governor_decisions_freeze_when_successor_dependency_work_tasks_are_open() -> None:
    decisions = weekly._governor_decisions(
        dt.date(2026, 4, 20),
        {
            "overall_progress_percent": 91,
            "history_snapshot_count": 8,
            "phase_label": "Scale & stabilize",
        },
        "Campaign Breadth and Promotion",
        0,
        active_wave_status="in_progress",
        journey_gate_health={"state": "ready", "blocked_count": 0},
        closure_health={"state": "clear"},
        provider_route_stewardship={"canary_status": "Canary green on all active lanes"},
        local_release_proof={"status": "passed"},
        flagship_readiness={"state": "ready", "proof_status": "pass"},
        successor_dependency_posture={
            "state": "blocked",
            "open_dependency_ids": [101],
            "open_dependency_work_task_ids": ["101.4", "102.2"],
        },
        status_plane={"whole_product_final_claim_status": "pass"},
        blocked_journeys=False,
        next20_closed=False,
        post_audit_closed=False,
    )

    launch_decision = decisions[1]
    assert launch_decision["action"] == "freeze_launch"
    assert launch_decision["reason"] == (
        "Freeze launch expansion until successor dependency work task(s) 101.4, 102.2 "
        "close in the next-90-day registry."
    )
    assert (
        "successor_open_dependency_work_task_ids=101.4,102.2"
        in launch_decision["cited_signals"]
    )


def test_governor_decisions_freeze_when_flagship_readiness_is_not_ready() -> None:
    decisions = weekly._governor_decisions(
        dt.date(2026, 4, 20),
        {
            "overall_progress_percent": 91,
            "history_snapshot_count": 8,
            "phase_label": "Scale & stabilize",
        },
        "Campaign Breadth and Promotion",
        0,
        active_wave_status="in_progress",
        journey_gate_health={"state": "ready", "blocked_count": 0},
        closure_health={"state": "clear"},
        provider_route_stewardship={"canary_status": "Canary green on all active lanes"},
        local_release_proof={"status": "passed"},
        flagship_readiness={"state": "watch", "proof_status": "fail"},
        successor_dependency_posture={"state": "ready", "open_dependency_ids": []},
        status_plane={"whole_product_final_claim_status": "pass"},
        blocked_journeys=False,
        next20_closed=False,
        post_audit_closed=False,
    )

    launch_decision = decisions[1]
    assert launch_decision["action"] == "freeze_launch"
    assert launch_decision["reason"] == (
        "Freeze launch expansion until published flagship readiness proof returns to ready posture."
    )
    assert "flagship_readiness_state=watch" in launch_decision["cited_signals"]
    assert "flagship_readiness_proof_status=fail" in launch_decision["cited_signals"]


def test_flagship_readiness_signal_fails_closed_on_non_green_published_proof() -> None:
    signal = weekly._flagship_readiness_signal(
        {
            "status": "fail",
            "missing_keys": ["desktop_client"],
            "warning_keys": ["mobile_play_shell"],
            "readiness_plane_gap_keys": ["flagship_ready", "public_shelf_ready"],
        }
    )

    assert signal["state"] == "watch"
    assert signal["proof_status"] == "fail"
    assert signal["coverage_gap_keys"] == ["desktop_client", "mobile_play_shell"]
    assert signal["readiness_plane_gap_keys"] == [
        "flagship_ready",
        "public_shelf_ready",
    ]
    assert "Published flagship readiness proof is fail." in signal["reason"]
