# Team 4 Week 13 Meeting Minutes

> **Editing rule:** Only the team leader may edit this file.

## Meeting 17

- **Dates:** November 10 and November 12, 2026
- **Time:** 8:30 PM to 9:30 PM EST
- **Location / format:** Fayetteville / Phone
- **Attendees:** Arthur Coleman, Exzavier Pickering, Afriyie Menishen

### Agenda and planned tasks

| Task | Owner | Due date | Status |
| --- | --- | --- | --- |
| Build the release-candidate CLI using the existing locked ensemble | Afriyie Menishen | November 12, 2026 | Completed |
| Verify CLI detector parity, threshold behavior, supported modes, and user-error handling | Arthur Coleman | November 12, 2026 | Completed |
| Complete user documentation, workflow screenshots, and optional GUI after the CLI stabilized | Exzavier Pickering | November 12, 2026 | Completed |
| Confirm the release interface does not alter Week 11 official results | All team members | November 12, 2026 | Completed |

### Results and decisions

- Menishen completed `src/cli.py`. It analyzes one image through the existing
  preprocessing, Chi-square, RS, DH, normalization, and locked ensemble
  pipeline, then reports the detector scores, ensemble score, and final
  `Clean` or `Suspicious` classification.
- Arthur completed the CLI integration and regression review. His focused
  suite passed 9 tests covering detector/ensemble parity, the inclusive `0.70`
  threshold boundary, grayscale/RGB inputs, invocation forms, and graceful
  handling of missing, corrupt, unsupported, or detector-failure cases.
- Exzavier completed the updated README, detailed user guide, CLI help/clean/
  suspicious workflow screenshots, and the optional GUI that reuses the CLI
  analysis pipeline.
- The merged-main verification suite passed 72 tests across CLI, GUI,
  ensemble-voting, normalization, and held-out-configuration coverage.
- The team confirmed that no Week 13 work changed detector behavior,
  preprocessing, normalization, locked weights, threshold, or the official
  Week 11 metrics and predictions.

### Next meeting

- **Date and time:** November 17 and November 19, 2026, 8:30 PM to 9:30 PM EST
- **Focus:** Begin the Week 14 final-report draft: methodology, dataset,
  calibration, held-out results, Week 12 robustness findings, limitations,
  and reproducibility instructions.
- **Data safeguard:** Keep the Week 11 held-out predictions and metrics as the
  official final evaluation. Do not recalibrate the ensemble from Week 12 or
  Week 13 observations.
