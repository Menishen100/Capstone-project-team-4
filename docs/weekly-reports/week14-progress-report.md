# Team 4 Week 14 Progress Report

## Multi-Feature Steganalysis Toolkit

**Team:** Afriyie Menishen (Team Leader), Arthur Coleman, and Exzavier Pickering  
**Reporting period:** Week 14  
**Planned milestone:** Final integration, code/documentation QA, release audit,
and submission-ready packaging.

## 1. Milestone achieved

The team completed the Week 14 release audit. Arthur's final regression QA and
Exzavier's documentation/reproducibility review were merged before Menishen's
final integration work began. The complete project now has a verified CLI,
optional GUI, reproducible setup instructions, final QA evidence, and a
release checklist ready for final tagging.

## 2. Completed work

- **Arthur:** Completed final detector, CLI, configuration, and GUI-callback
  regression QA. His final checks preserved the existing detector behavior and
  locked ensemble values.
- **Exzavier:** Completed the README and reproducibility review, verified user
  commands and dataset workflow, and added the missing `reportlab` dependency
  required by the PDF export script.
- **Menishen:** Performed the final merged-main audit. A fresh environment
  installed all declared requirements with no broken packages; the full test
  inventory passed **281 tests**. CLI help and the documented clean/stego
  examples passed, and the optional GUI was visibly verified after launch.

## 3. Release safeguards

The release retains the validation-selected configuration: Chi-square `0.00`,
RS `0.70`, DH `0.30`, and threshold `0.70`. The official Week 11 metrics
remain accuracy `0.6250`, precision `0.6923`, recall `0.4500`, and F1
`0.5455`, with TP `9`, TN `16`, FP `4`, and FN `11`.

Week 14 made no detector, normalization, voting, threshold, or held-out
evaluation changes. The final `v1.0-final` tag is reserved as the last action
after Menishen's audit record is merged into `main`.

## 4. Contributions of each team member

| Team member | Week 14 contribution |
| --- | --- |
| **Afriyie Menishen — Team Leader** | Completed final integration, fresh-environment installation audit, end-to-end CLI/GUI release checks, release checklist, and packaging preparation. |
| **Arthur Coleman — Member A** | Completed independent full-suite QA, detector/CLI regression review, GUI callback coverage, and final QA documentation. |
| **Exzavier Pickering — Member B** | Completed final README and reproducibility review, dataset/user-workflow validation, documentation cleanup, and dependency audit. |

## 5. Supporting evidence

- [Final release checklist](../week14-final-release-checklist.md)
- [Menishen final release audit](../week14-menishen-final-release-audit.md)
- [Arthur final QA](../week14-arthur-final-qa.md)
- [Exzavier reproducibility review](../week14-reproducibility-review.md)
- [Week 14 meeting minutes](../../minutes/week14_meeting_minutes.md)
