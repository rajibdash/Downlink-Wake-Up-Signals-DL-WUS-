# Downlink-Wake-Up-Signals-DL-WUS-
DL-WUS acts as an ultra-low-power pre-signal sent by the base station (gNB). If the UE detects a valid DL-WUS, it activates its Main Radio (MR) to process subsequent scheduling grants or paging blocks. If no DL-WUS is sent or detected, the main transceiver remains in a deep sleep state, cutting power consumption drastically.

## Implemented DL-WUS design package

Repository now includes a minimal executable design in `dl_wus.py` with:

1. **DL-WUS trigger mechanism inventory** (paging, DL data, UL grant, HARQ retransmission, CSI report, SI update).
2. **3GPP alignment anchors** captured per trigger (TS 38.304, 38.331, 38.321, 38.213, 38.214).
3. **DL/UL scheduler and radio checks** via `evaluate_scheduler(...)`.
4. **L2/L1 signal handling and ON/OFF keying** via `run_dlwus_flow(...)`.
5. **Complete L3→L2/UPC→L1→Radio→UE flow** emitted as pipeline steps.
6. **Energy-efficiency agent structure** via `EnergyOptimizationAgent`.

### End-to-end flow

`L3 (RRC trigger check) -> L2/UPC (scheduler decision) -> L1 (ON/OFF keying generation/suppress) -> Radio (DL-WUS TX/no-TX) -> UE (wake/sleep decision)`

### Run tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```
