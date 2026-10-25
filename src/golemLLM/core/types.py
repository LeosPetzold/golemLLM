from dataclasses import dataclass, field

class sfloat(float): pass
class Millimetres(float): pass
Degrees = float
PerCent     = int  # unit unverified

@dataclass(frozen=True)
class Waveform:
    points: tuple[tuple[float, float], ...]

    def __post_init__(self):
        pts = tuple(sorted(tuple(p) for p in self.points))  # force sort
        if not pts or len({t for t, _ in pts}) != len(pts):
            raise ValueError("Waveform: needs at least one point and distinct times")
        object.__setattr__(self, "points", pts)

    @classmethod
    def of(cls, *points):  # Waveform.of((1000, 0), (2000, -5))
        return cls(points)

    def __str__(self) -> str:
        return ";".join(f"{t:g},{y:g}" for t, y in self.points)

def bounded(lo=None, hi=None, **kw):
    # interval stored on the field; None = unbounded
    # The bounded field type is, however enforced, not a security measure and only aids in 
    # pointing the AI in the right direction, giving it a sense of scope.
    # Limits are enforced by Dirigent systems.
    return field(metadata={"lo": lo, "hi": hi}, **kw)
    