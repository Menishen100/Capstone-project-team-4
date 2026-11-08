# Team 4 Week 11 Meeting Minutes

> **Editing rule:** Only the team leader may edit this file.

## Meeting 15

- **Dates:** October 27 and October 29, 2026
- **Time:** 8:30 PM to 9:30 PM EST
- **Location / format:** Fayetteville / Phone
- **Attendees:** Arthur Coleman, Exzavier Pickering, Afriyie Menishen

### Agenda and planned tasks

| Task | Owner | Due date | Status |
| --- | --- | --- | --- |
| Run the official held-out evaluation with the locked Week 10 configuration | Afriyie Menishen | October 29, 2026 | Completed |
| Independently verify official held-out scores, metrics, and confusion counts | Arthur Coleman | October 29, 2026 | Completed |
| Produce held-out ROC/AUC and confusion-matrix plots without retuning | Exzavier Pickering | October 29, 2026 | Completed |
| Confirm the held-out split is paired, complete, and not used for retuning | All team members | October 29, 2026 | Completed |

### Results and decisions

- Menishen completed the official held-out evaluation on 40 images: 20 clean
  and 20 matched LSB-stego images from 20 `held_out_test` source pairs.
- The team preserved the locked Week 10 configuration: Chi-square `0.00`, RS
  `0.70`, DH `0.30`, and decision threshold `0.70`. No weights, threshold,
  preprocessing, score direction, or detector behavior was changed after the
  held-out outcomes were recorded.
- The final held-out metrics are accuracy `0.6250`, precision `0.6923`, recall
  `0.4500`, and F1 `0.5455`. The confusion matrix is TP `9`, TN `16`, FP `4`,
  and FN `11`.
- Arthur independently recalculated and verified the configuration, normalized
  scores, ensemble predictions, metric values, and confusion counts against
  the official prediction CSV and metrics JSON.
- Exzavier produced the held-out ensemble ROC curve, detector-versus-ensemble
  ROC comparison, and final confusion-matrix plot. The recorded AUC values are
  Chi-square `0.5475`, RS `0.6850`, DH `0.5875`, and ensemble `0.6675`.
- The team agreed that the observed false negatives and lower recall are
  evaluation findings for Week 12 error analysis; they are not a basis for
  altering the locked Week 10 configuration.
- The team confirmed that source-pair separation was maintained and that every
  official prediction row belongs only to `held_out_test`.

### Next meeting

- **Date and time:** November 3 and November 5, 2026, 8:30 PM to 9:30 PM EST
- **Focus:** Begin Week 12 error-case analysis and robustness checks across
  payload rates; document false positives and false negatives and add
  regression tests without retroactively changing the Week 11 held-out result.
- **Data safeguard:** Retain the Week 11 evaluation artifacts as the official
  locked result. Any later investigation must clearly distinguish diagnostic
  analysis from retuning or replacing the reported held-out metrics.
