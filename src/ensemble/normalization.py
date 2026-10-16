"""Direction-align detector scores for later ensemble use.

These functions preserve the existing bounded scale. They do not calibrate
scores or estimate probabilities.
"""

from numbers import Real


def _validate_score(score: Real) -> float:
    """Return a finite real score in [0, 1], rejecting booleans and arrays."""
    if isinstance(score, bool) or not isinstance(score, Real):
        raise ValueError("score must be a finite numeric value in [0, 1]")

    value = float(score)
    if not 0.0 <= value <= 1.0:
        raise ValueError("score must be a finite numeric value in [0, 1]")
    return value


def normalize_chi_square(score: Real) -> float:
    """Keep the Chi-square p-value score direction unchanged."""
    return _validate_score(score)


def normalize_rs(score: Real) -> float:
    """Invert the bounded RS score so higher values mean more suspicious."""
    return 1.0 - _validate_score(score)
