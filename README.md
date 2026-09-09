# Downlink Wake-Up Signals (DL-WUS) — 6G Pilot Project

This repository gathers key technical and implementation-facing information about **Downlink Wake-Up Signals (DL-WUS)** for a 6G pilot context.

## 1) What DL-WUS is

DL-WUS is a very low-power downlink trigger that allows a User Equipment (UE) to keep its main radio chain asleep most of the time.  
When a valid wake-up indication is detected, the UE enables the main receiver/transmitter chain to process paging, scheduling, and traffic.  
If no valid DL-WUS is detected, the main radio remains in deep sleep to save energy.

## 2) Why DL-WUS matters in 6G

6G targets include extreme energy efficiency, long battery life, massive device density, and always-available connectivity. DL-WUS helps by:

- Reducing idle/listening power in UE
- Extending battery life for IoT, wearables, sensors, and low-duty-cycle devices
- Lowering unnecessary paging/synchronization monitoring overhead
- Enabling greener network operation with lower aggregate device energy usage

## 3) Core operating concept

1. **Sleep phase:** UE main radio is off or in ultra-low-power state.  
2. **WUS monitoring phase:** A dedicated low-power wake-up receiver periodically monitors DL-WUS resources.  
3. **Wake decision:** If detection confidence crosses threshold, UE wakes the main radio.  
4. **Main channel processing:** UE receives control/data/paging in configured follow-up resources.  
5. **Return-to-sleep policy:** If no relevant payload follows, UE quickly re-enters sleep.

## 4) DL-WUS signal design dimensions

- **Waveform design:** Robust under low SNR and fading while keeping receiver complexity low
- **Time-frequency resource mapping:** Sparse, periodic, and interference-aware placement
- **Addressing/grouping:** UE-specific or group-based wake-up IDs/signatures
- **Repetition strategy:** Repeated WUS bursts to improve detection reliability
- **Coding/spreading:** Lightweight coding/spreading for false-alarm/miss-detection control
- **Synchronization tolerance:** Operation with relaxed timing/frequency assumptions for low-power receivers
- **Multi-cell robustness:** Interference handling and reuse planning in dense deployments

## 5) Receiver and detection considerations

- **Low-power wake-up receiver (WuRx):** Always-on or duty-cycled front-end with minimal power draw
- **Two-stage detection:** Coarse detection then confirmation to reduce false wake-ups
- **Threshold adaptation:** Dynamic thresholding vs channel/load/interference conditions
- **False Alarm (FA) vs Miss Detection (MD):** Key trade-off driving both energy and latency
- **Security hardening:** Signature/randomization concepts to avoid spoofed wake-ups

## 6) 6G pilot use-case candidates

- Massive IoT metering and sensing
- Industrial monitoring with infrequent but critical updates
- Wearables and health-adjacent edge devices with strict battery constraints
- Smart-city devices with long idle cycles
- Asset tracking and telemetry with bursty uplink/downlink patterns

## 7) Evaluation KPIs for pilot validation

- UE idle power reduction (%)
- Battery lifetime improvement (days/months/years)
- Wake-up detection probability
- False alarm rate
- Miss detection rate
- Wake-up-to-decode latency
- Throughput impact after wake-up
- Control overhead and spectral efficiency impact
- Multi-user scalability and collision/interference performance

## 8) Typical trade-offs

- More repetitions improve detection but increase overhead
- Lower thresholds reduce misses but increase false wake-ups
- Short monitoring cycles improve latency but consume more power
- Group wake-up improves scale but can wake non-target UEs

## 9) Pilot architecture building blocks

- gNB DL-WUS generator/scheduler
- WUS resource planner (periodicity, mapping, reuse)
- UE low-power WuRx model
- UE wake-up state machine
- Follow-up control channel mapping and timing
- KPI logger for energy/latency/reliability metrics

## 10) Suggested phased pilot roadmap

### Phase A — Baseline
- Implement no-WUS baseline (legacy idle monitoring behavior)
- Measure baseline UE idle energy and paging latency

### Phase B — Basic DL-WUS
- Add single-cell DL-WUS and UE wake-up state machine
- Tune detection threshold/repetition under static channel assumptions

### Phase C — Realistic Conditions
- Evaluate mobility, fading, and inter-cell interference
- Stress-test FA/MD behavior and wake-up latency tails

### Phase D — Optimization
- Adaptive thresholds and periodicity
- UE grouping/addressing optimization
- Final parameter set for deployment recommendation

## 11) Risks and mitigation

- **High false wake-ups:** Improve signature design and threshold adaptation
- **Missed wake-ups:** Increase repetition diversity and refine detection windows
- **Interference sensitivity:** Better resource planning, coordination, and filtering
- **Implementation complexity:** Modular architecture with staged feature enabling

## 12) Deliverables expected from this pilot

- Reference DL-WUS system design
- Reproducible simulation/field-test methodology
- KPI results vs baseline
- Recommended operating points (threshold, periodicity, repetitions, mapping)
- Gaps/open items for further 6G standardization and productization

---

## Quick glossary

- **DL-WUS:** Downlink Wake-Up Signal
- **UE:** User Equipment
- **gNB:** Next-generation NodeB (base station)
- **WuRx:** Wake-Up Receiver (ultra-low-power receiver path)
- **FA:** False Alarm
- **MD:** Miss Detection
