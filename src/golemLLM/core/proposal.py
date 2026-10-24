# Proposing function

import re
from dataclasses import dataclass, field, fields
from enum import Enum, Flag
from functools import partial
from typing import ClassVar, Optional

# syntax from http://golem.fjfi.cvut.cz/shotdir/54395/Operation/Discharge/Styles/index.html
# execute via Dirigent.sh --discharge <args>  (http://golem.fjfi.cvut.cz/shotdir/54599/Dirigent.sh)

_SAFE_TEXT = re.compile(r"[A-Za-z0-9 _.,:()+/-]{1,200}")

# immutable, validated at construction
frozen = partial(dataclass, frozen=True, kw_only=True)


#region Enums
class DischargeStyle(Enum):
    STANDARD                       = 'standard'
    STANDARD_WITH_STABILIZATION    = 'standard-ws'  # from Dirigent.sh -d shortcuts
    STANDARD_WITHOUT_STABILIZATION = 'standard-wos'
    MODEST    = 'modest'
    HIGH_BT   = 'highBt'
    FULLSTEAM = 'fullsteam'
    VACUUM    = 'vacuum'
    DUMMY     = 'dummy'
    SUJB      = 'sujb'

class Toggle(Enum):
    ON  = 'on'
    OFF = 'off'

class AngularDirection(Enum):
    CLOCKWISE        = 'CW'
    COUNTERCLOCKWISE = 'CCW'

class PreionizationDevice(Enum):
    HOT_CATHODE = 'HotCathode'

class WorkingGas(Enum):
    HYDROGEN = 'H'
    HELIUM   = 'He'

class PressureMode(Enum):  # S_mode with pressure request
    LINEAR_CALIBRATION_FROM_ZERO_PRESSURE       = 'p_wg'
    LINEAR_CALIBRATION_FROM_ZERO_PRESSURE_ALIAS = 'p_wg-zc'
    LINEAR_CALIBRATION_FROM_NONZERO_PRESSURE    = 'p_wg-nzc'
    PID_REGULATOR = 'p_pid'

class StripDetectorMode(Enum):
    MODE_0 = 0  # only value found

class PinMask(Flag):  # any combination of 12 pins; other values are rejected by Flag itself
    P1 = 1 << 0;  P2 = 1 << 1;  P3 = 1 << 2;   P4 = 1 << 3
    P5 = 1 << 4;  P6 = 1 << 5;  P7 = 1 << 6;   P8 = 1 << 7
    P9 = 1 << 8;  P10 = 1 << 9; P11 = 1 << 10; P12 = 1 << 11

    def __str__(self) -> str:
        return format(self.value, "012b")[::-1]  # formats as binary with P1 being leftmost
#endregion


#region Value types
Millimetres = float
Degrees     = float
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
    return field(metadata={"lo": lo, "hi": hi}, **kw)
#endregion


#region Sections
@frozen
class Section:
    SECTION: ClassVar[str]

    def __post_init__(self):  # value € interval check
        for f in fields(self):
            v, lo, hi = getattr(self, f.name), f.metadata.get("lo"), f.metadata.get("hi")
            if v is not None and ((lo is not None and v < lo) or (hi is not None and v > hi)):
                raise ValueError(f"{self.SECTION}.{f.name}={v} outside {lo}..{hi}")

    def items(self) -> list[tuple[str, object]]:
        return [(f.name, getattr(self, f.name)) for f in fields(self)
                if getattr(self, f.name) is not None]


@frozen
class OperationDischarge(Section):
    SECTION: ClassVar[str] = "operation.discharge"
    style:       DischargeStyle
    vacuum_shot: Optional[int] = None


@frozen
class OperationHigherPower(Section):
    SECTION: ClassVar[str] = "operation.higherpower"
    voice:                Optional[Toggle] = None
    wg_voice:             Optional[Toggle] = None
    RawDataAcquiring:     Optional[Toggle] = None
    analysis:             Optional[Toggle] = None
    diagnostics_onstage:  Optional[Toggle] = None
    diagnostics_offstage: Optional[Toggle] = None
    infrastructure:       Optional[Toggle] = None


@frozen
class InfrastructureBtEcd(Section):
    SECTION: ClassVar[str] = "infrastructure.bt_ecd"
    U_Bt: int = bounded(0, 1200)  # V
    t_Bt: int
    O_Bt: AngularDirection
    U_cd: int = bounded(0, 900)  # V
    t_cd: int = bounded(0, 10000)  # us
    O_cd: AngularDirection


@frozen
class InfrastructurePreionization(Section):
    SECTION: ClassVar[str] = "infrastructure.preionization"
    S_device: Optional[PreionizationDevice] = None
    SW_main:  Optional[Toggle] = None
    U_heater: Optional[int] = None
    U_accel:  Optional[int] = None


# working gas to be one class per mode
@frozen
class WorkingGasVacuum(Section):
    SECTION: ClassVar[str] = "infrastructure.workinggas"
    S_mode: str = field(default="vacuum", init=False)
    S_gas:  WorkingGas
    p_H:    float = field(default=0, init=False)
    U_v:    float = field(default=0, init=False)
@frozen
class WorkingGasPressure(Section):
    SECTION: ClassVar[str] = "infrastructure.workinggas"
    S_mode: PressureMode
    S_gas:  WorkingGas
    p_H:    float = bounded(0, 40)  # mPa
@frozen
class WorkingGasValveVoltage(Section):
    SECTION: ClassVar[str] = "infrastructure.workinggas"
    S_mode: str = field(default="U_v", init=False)
    S_gas:  WorkingGas
    U_v:    float

WorkingGasRequest = WorkingGasVacuum | WorkingGasPressure | WorkingGasValveVoltage


@frozen
class InfrastructurePositionStabilization(Section):
    SECTION: ClassVar[str] = "infrastructure.positionstabilization"
    main_switch:       Optional[Toggle] = None
    radial_switch:     Optional[Toggle] = None
    radial_waveform:   Optional[Waveform] = None
    vertical_switch:   Optional[Toggle] = None
    vertical_waveform: Optional[Waveform] = None


@frozen
class InfrastructureBiasingElectrode(Section):
    SECTION: ClassVar[str] = "infrastructure.biasingelectrode"
    main_switch: Optional[Toggle] = None
    waveform:    Optional[Waveform] = None
    position:    Optional[PerCent] = None


@frozen
class InfrastructureGasPuffing(Section):
    SECTION: ClassVar[str] = "infrastructure.gasspuffing"
    waveform: Waveform


@frozen
class InfrastructureCurrentStabilization(Section):
    SECTION: ClassVar[str] = "infrastructure.currentstabilization"
    main_switch: Optional[Toggle] = None
    waveform:    Optional[Waveform] = None


@frozen
class DiagnosticsDoubleRakeProbe(Section):
    SECTION: ClassVar[str] = "diagnostics.doublerakeprobe"
    r_First_Tip: Optional[Millimetres] = bounded(hi=100, default=None)  # wall at ~100 mm
    X_mod:       Optional[PinMask] = None
    I_SilverBox: Optional[float] = None


@frozen
class DiagnosticsRakeProbe(Section):
    SECTION: ClassVar[str] = "diagnostics.rakeprobe"
    r_First_Tip:     Optional[Millimetres] = bounded(hi=100, default=None)  # %
    phi_First_Tip:   Optional[Degrees] = None
    X_mod:           Optional[PinMask] = None
    I_SilverBox:     Optional[float] = None
    r_manipulator:   Optional[Millimetres] = None
    phi_manipulator: Optional[Degrees] = None


@frozen
class DiagnosticsLimiterMirnovCoils(Section):
    SECTION: ClassVar[str] = "diagnostics.limitermirnovcoils"
    vacuum_shot: Optional[int] = None


@frozen
class DiagnosticsScintillationProbes(Section):
    SECTION: ClassVar[str] = "diagnostics.scintillationprobes"
    U_NIM_A1: Optional[int] = None
    U_NIM_A2: Optional[int] = None
    U_NIM_A3: Optional[int] = None
    U_NIM_A4: Optional[int] = None


@frozen
class DiagnosticsStripDetector(Section):
    SECTION: ClassVar[str] = "diagnostics.stripdetector"
    r_sensor:  Optional[float] = None
    acq_time:  Optional[float] = None
    acq_delay: Optional[float] = None
    acq_mode:  Optional[StripDetectorMode] = None
#endregion


#region Proposal
@frozen
class GolemPROPOSAL:
    # required
    discharge:  OperationDischarge
    bt_ecd:     InfrastructureBtEcd
    workinggas: WorkingGasRequest
    comment:    str

    # optional, None means argument not in command
    higherpower:           Optional[OperationHigherPower] = None
    preionization:         Optional[InfrastructurePreionization] = None
    positionstabilization: Optional[InfrastructurePositionStabilization] = None
    biasingelectrode:      Optional[InfrastructureBiasingElectrode] = None
    gasspuffing:           Optional[InfrastructureGasPuffing] = None
    currentstabilization:  Optional[InfrastructureCurrentStabilization] = None
    doublerakeprobe:       Optional[DiagnosticsDoubleRakeProbe] = None
    rakeprobe:             Optional[DiagnosticsRakeProbe] = None
    limitermirnovcoils:    Optional[DiagnosticsLimiterMirnovCoils] = None
    scintillationprobes:   Optional[DiagnosticsScintillationProbes] = None
    stripdetector:         Optional[DiagnosticsStripDetector] = None
    ScanDefinition:        Optional[str] = None

    def __post_init__(self):  # safe valid characters?
        texts = [self.comment] + ([] if self.ScanDefinition is None else [self.ScanDefinition])
        if not all(_SAFE_TEXT.fullmatch(t) for t in texts):
            raise ValueError("comment/ScanDefinition: empty or contains characters not allowed")

    def sections(self) -> list[Section]:  # field order same as example commands for clarity
        return [v for f in fields(self) if isinstance(v := getattr(self, f.name), Section)]

    def to_argv(self) -> list[str]:
        argv = ["--discharge"]
        for s in self.sections():
            argv += [f"--{s.SECTION}", ",".join(f"{k}={_fmt(v)}" for k, v in s.items())]
        argv += ["--comment", self.comment]
        if self.ScanDefinition is not None:
            argv += ["--ScanDefinition", self.ScanDefinition]
        return argv

    def to_command(self) -> str:
        return " ".join(a if a.startswith("--") else f'"{a}"' for a in self.to_argv())

    def flat(self) -> dict[str, object]:
        out = {f"{s.SECTION}.{k}": _plain(v) for s in self.sections() for k, v in s.items()}
        out["comment"] = self.comment
        if self.ScanDefinition is not None:
            out["ScanDefinition"] = self.ScanDefinition
        return out

    def diff(self, other: "GOLEMproposal") -> list[dict]:
        a, b = self.flat(), other.flat()
        keys = list(a) + [k for k in b if k not in a]
        return [{"param": k, "previous": b.get(k), "proposed": a.get(k)}
                for k in keys if a.get(k) != b.get(k)]
#endregion


def _fmt(v) -> str:
    if isinstance(v, (Waveform, PinMask)):
        return f"'{v}'"
    if isinstance(v, Enum):
        return f"'{v.value}'" if isinstance(v.value, str) else str(v.value)
    if isinstance(v, str):
        return f"'{v}'"
    if isinstance(v, float):
        return f"{v:g}"
    return str(v)

def _plain(v):
    if isinstance(v, (Waveform, PinMask)):
        return str(v)
    if isinstance(v, Enum):
        return v.value
    return v