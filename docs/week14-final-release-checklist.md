# Week 14 Final Release Checklist

Audit target: fetched `origin/main` at `03ec6cb` (Week 13 integration). This
checklist is a release gate; unchecked items require Week 14 work or team action.

- [x] Full source code present
- [x] Requirements install successfully in a fresh virtual environment
- [x] Full test suite passes (see [Arthur's QA report](week14-arthur-final-qa.md))
- [x] Dataset and generation workflow present
- [x] CLI runs
- [x] README instructions and examples reviewed and verified
- [x] Clean example works
- [x] Suspicious example works
- [x] Documentation links work
- [x] No held-out recalibration occurred
- [ ] Final repository reviewed and approved by the team
- [ ] `v1.0-final` tag created and verified on GitHub

## Additional release gates

- [ ] Complete a manual GUI selection, analysis, and displayed-result walkthrough
- [ ] Exzavier updates the stale README sentence that lists optional GUI support
  as a future improvement; the GUI is already present in `src/gui.py`
- [ ] Merge the Arthur and Exzavier Week 14 contributions into `main`
- [ ] Menishen completes the final audit on the fully merged `main`
- [ ] Confirm all three members have meaningful Week 14 commits
- [ ] Create and push `v1.0-final` only after the merged-main audit passes

The tag remains intentionally uncreated while these release gates are open.
