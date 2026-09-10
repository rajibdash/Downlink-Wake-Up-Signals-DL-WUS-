import unittest

from dl_wus import (
    EnergyOptimizationAgent,
    SignalState,
    TriggerContext,
    flow_to_dict,
    list_trigger_mechanisms,
    run_dlwus_flow,
)


class DLWUSTest(unittest.TestCase):
    def test_trigger_mechanism_inventory(self):
        names = {m.name for m in list_trigger_mechanisms()}
        self.assertTrue(
            {
                "paging_indication",
                "dl_data_pending",
                "ul_grant_required",
                "harq_retransmission",
                "csi_reporting",
                "system_information_update",
            }.issubset(names)
        )

    def test_on_off_keying_turns_on_when_valid_trigger_and_radio_ok(self):
        flow = run_dlwus_flow(TriggerContext(dl_data_pending=True))

        self.assertEqual(flow.signal_state, SignalState.ON)
        self.assertEqual(flow.l1_action, "generate_on_off_keying_preamble")
        self.assertEqual(flow.radio_action, "transmit_dlwus")
        self.assertIn("dl_data_pending", flow.trigger_reasons)

    def test_signal_stays_off_without_trigger(self):
        flow = run_dlwus_flow(TriggerContext())

        self.assertEqual(flow.signal_state, SignalState.OFF)
        self.assertEqual(flow.ue_action, "remain_in_sleep")

    def test_dl_ul_checks_block_wakeup_on_radio_failure(self):
        flow = run_dlwus_flow(
            TriggerContext(dl_data_pending=True, ul_grant_required=True, radio_link_ok=False)
        )

        self.assertEqual(flow.signal_state, SignalState.OFF)
        self.assertFalse(flow.checks.dl_ok)
        self.assertFalse(flow.checks.ul_ok)
        self.assertEqual(len(flow.checks.failures), 2)

    def test_end_to_end_entity_order(self):
        flow = run_dlwus_flow(TriggerContext(paging_pending=True))
        entities = [step.entity for step in flow.steps]

        self.assertEqual(entities, ["L3", "L2/UPC", "L1", "Radio", "UE"])

    def test_energy_optimization_agent_mode(self):
        agent = EnergyOptimizationAgent(inactivity_budget_ms=80, wake_guard_ms=8)
        flow = run_dlwus_flow(TriggerContext(), agent=agent)
        dumped = flow_to_dict(flow)

        self.assertIn("deep_sleep", dumped["pipeline"][-1]["action"])


if __name__ == "__main__":
    unittest.main()
