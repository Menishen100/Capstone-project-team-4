# Chi-square and RS Diagnostics

## Chi-square detector

- `score`: the detector's current suspiciousness score; it is the Chi-square
  p-value and is bounded from 0 to 1.
- `chi_square`: the Chi-square goodness-of-fit statistic computed across the
  populated adjacent pixel-value pairs.
- `p_value`: the probability value produced by the Chi-square test.
- `value_pairs_analyzed`: the number of populated `(0,1)` through `(254,255)`
  pixel-value pairs included in the test.
- `samples_analyzed`: the total number of input samples used to form the
  histogram.

## RS detector

- `score`: the absolute RS statistic, clipped to the range 0 to 1.
- `regular_groups`: groups whose local discrimination increases after all LSBs
  are toggled.
- `singular_groups`: groups whose local discrimination decreases after all
  LSBs are toggled.
- `unchanged_groups`: groups with the same discrimination before and after the
  LSB toggle.
- `groups_analyzed`: the number of complete, non-overlapping four-sample
  groups classified by RS analysis. It always equals regular plus singular plus
  unchanged groups.
- `rs_statistic`: `(regular_groups - singular_groups) / (regular_groups +
  singular_groups)`, or `0.0` when there are no regular or singular groups.
- `channels_analyzed`: one for grayscale input and three for RGB input.
- `samples_analyzed`: the number of samples in complete four-sample groups;
  trailing samples that do not form a complete group are excluded.
