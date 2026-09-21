# Team 4 Week 5 Meeting Minutes

> **Editing rule:** Only the team leader may edit this file.

## Meeting 9

- **Dates:** September 15 and September 17, 2026
- **Time:** 8:30 PM to 9:30 PM EST
- **Location / format:** Fayetteville / Phone
- **Attendees:** Arthur Coleman, Exzavier Pickering, Afriyie Menishen

### Agenda and tasks

| Task | Owner | Due date | Status |
| --- | --- | --- | --- |
| Validate and prepare the clean-image collection and source inventory | Arthur Coleman | September 17, 2026 | In progress |
| Implement and test the LSB embedder | Exzavier Pickering | September 17, 2026 | Completed |
| Build the paired dataset-generation, metadata, and integrity-validation workflow | Afriyie Menishen | September 17, 2026 | Completed |
| Review the integrated Week 5 workflow and run the full test suite | All team members | September 17, 2026 | Completed |

### Results and decisions

- Arthur's clean-image validator and source rules were completed. The repository contains 100 clean PNG files, but the factual source/license inventory rows still need to be completed before the clean collection can pass validation.
- Exzavier's LSB embedder and its unit tests were completed and merged.
- Menishen's paired dataset generator, metadata schema, split validation, and reproducibility tests were completed and merged.
- The full repository test suite passed with 64 tests.
- The paired generator enforces one clean/stego mapping per source and the required 60 development, 20 validation, and 20 held-out test pair allocation.
- The team decided not to generate or claim the full 100-pair dataset until each clean image has a truthful source/license record. The current dataset therefore has 100 clean files, one stego sample, and a metadata schema awaiting generated rows.

### Next meeting

- **Time:** September 22 and September 24, 2026, 8:30 PM to 9:30 PM EST
- **Focus:** Complete the clean-image source inventory and generate the paired dataset, then begin the Week 6 work: add per-detector diagnostic output and run preliminary scores across the development split.
