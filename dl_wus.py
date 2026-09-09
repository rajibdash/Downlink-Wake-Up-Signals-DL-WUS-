from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Sequence


class SignalState(str, Enum):
    ON = "ON"
    OFF = "OFF"


@dataclass(frozen=True)
class TriggerMechanism:
    name: str
    layer: str
    condition: str
    spec_anchor: str


TRIGGER_MECHANISMS: Sequence[TriggerMechanism] = (
    TriggerMechanism(
        name="paging_indication",
        layer="L3/RRC",
        condition="UE has paging occasion and pending paging record",
        spec_anchor="3GPP TS 38.304, TS 38.331",
    ),
    TriggerMechanism(
        name="dl_data_pending",
        layer="L2/MAC",
        condition="gNB DL buffer has user/control data for sleeping UE",
        spec_anchor="3GPP TS 38.321",
    ),
    TriggerMechanism(
        name="ul_grant_required",
        layer="L2/MAC",
        condition="UL scheduling grant must be delivered after wake-up",
        spec_anchor="3GPP TS 38.213, TS 38.321",
    ),
    TriggerMechanism(
        name="harq_retransmission",
        layer="L1/L2",
        condition="HARQ feedback requires retransmission scheduling",
        spec_anchor="3GPP TS 38.214",
    ),
    TriggerMechanism(
        name="csi_reporting",
        layer="L1",
        condition="Configured CSI report opportunity requires UE activity",
        spec_anchor="3GPP TS 38.214",
    ),
    TriggerMechanism(
        name="system_information_update",
        layer="L3/RRC",
        condition="Broadcast/system information update for UE context",
        spec_anchor="3GPP TS 38.331",
    ),
)


@dataclass
class TriggerContext:
    ue_in_drx: bool = True
    paging_pending: bool = False
    dl_data_pending: bool = False
    ul_grant_required: bool = False
    harq_retransmission: bool = False
    csi_reporting: bool = False
    system_information_update: bool = False
    radio_link_ok: bool = True


@dataclass
class SchedulerChecks:
    dl_ok: bool
    ul_ok: bool
    failures: List[str] = field(default_factory=list)


@dataclass
class FlowStep:
    entity: str
    action: str


@dataclass
class FlowResult:
    signal_state: SignalState
    trigger_reasons: List[str]
    checks: SchedulerChecks
    l2_action: str
    l1_action: str
    radio_action: str
    ue_action: str
    steps: List[FlowStep]


@dataclass
class EnergyOptimizationAgent:
    inactivity_budget_ms: int = 80
    wake_guard_ms: int = 8

    def compute_sleep_mode(self, expected_activity_ms: int) -> str:
        if expected_activity_ms <= self.wake_guard_ms:
            return "active_guard"
        if expected_activity_ms <= self.inactivity_budget_ms:
            return "micro_sleep"
        return "deep_sleep"


def list_trigger_mechanisms() -> Sequence[TriggerMechanism]:
    return TRIGGER_MECHANISMS


def _collect_trigger_reasons(ctx: TriggerContext) -> List[str]:
    reasons: List[str] = []
    if ctx.paging_pending:
        reasons.append("paging_indication")
    if ctx.dl_data_pending:
        reasons.append("dl_data_pending")
    if ctx.ul_grant_required:
        reasons.append("ul_grant_required")
    if ctx.harq_retransmission:
        reasons.append("harq_retransmission")
    if ctx.csi_reporting:
        reasons.append("csi_reporting")
    if ctx.system_information_update:
        reasons.append("system_information_update")
    return reasons


def evaluate_scheduler(ctx: TriggerContext) -> SchedulerChecks:
    failures: List[str] = []
    dl_ok = not ctx.dl_data_pending or ctx.radio_link_ok
    if not dl_ok:
        failures.append("DL scheduling blocked due to radio link failure")

    ul_ok = not ctx.ul_grant_required or ctx.radio_link_ok
    if not ul_ok:
        failures.append("UL scheduling blocked due to radio link failure")

    return SchedulerChecks(dl_ok=dl_ok, ul_ok=ul_ok, failures=failures)


def decide_signal_state(ctx: TriggerContext, checks: SchedulerChecks) -> SignalState:
    if not ctx.ue_in_drx:
        return SignalState.OFF
    if _collect_trigger_reasons(ctx) and checks.dl_ok and checks.ul_ok:
        return SignalState.ON
    return SignalState.OFF


def run_dlwus_flow(ctx: TriggerContext, agent: EnergyOptimizationAgent | None = None) -> FlowResult:
    checks = evaluate_scheduler(ctx)
    reasons = _collect_trigger_reasons(ctx)
    signal_state = decide_signal_state(ctx, checks)

    if signal_state == SignalState.ON:
        l2_action = "schedule_control_and_data"
        l1_action = "generate_on_off_keying_preamble"
        radio_action = "transmit_dlwus"
        ue_action = "wake_main_radio"
    else:
        l2_action = "defer_scheduling"
        l1_action = "suppress_keying"
        radio_action = "no_dlwus_tx"
        ue_action = "remain_in_sleep"

    if agent:
        expected_activity_ms = 0 if signal_state == SignalState.ON else agent.inactivity_budget_ms + 1
        ue_action = f"{ue_action}:{agent.compute_sleep_mode(expected_activity_ms)}"

    steps = [
        FlowStep("L3", "check_rrc_context_and_paging"),
        FlowStep("L2/UPC", l2_action),
        FlowStep("L1", l1_action),
        FlowStep("Radio", radio_action),
        FlowStep("UE", ue_action),
    ]

    return FlowResult(
        signal_state=signal_state,
        trigger_reasons=reasons,
        checks=checks,
        l2_action=l2_action,
        l1_action=l1_action,
        radio_action=radio_action,
        ue_action=ue_action,
        steps=steps,
    )


def flow_to_dict(flow: FlowResult) -> Dict[str, object]:
    return {
        "signal_state": flow.signal_state.value,
        "trigger_reasons": flow.trigger_reasons,
        "scheduler": {
            "dl_ok": flow.checks.dl_ok,
            "ul_ok": flow.checks.ul_ok,
            "failures": flow.checks.failures,
        },
        "pipeline": [
            {"entity": step.entity, "action": step.action}
            for step in flow.steps
        ],
    }
