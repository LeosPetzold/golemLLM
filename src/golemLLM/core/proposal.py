# Proposing function
# Operators will be questioned about parameters tagged with '# ?'.

import re
from golemLLM.core.types import bounded, Millimetres, Degrees, Waveform, sfloat
from dataclasses import dataclass, field, fields
from enum import Enum, Flag
from functools import partial
from typing import ClassVar, Optional

import shlex
from golemLLM.core.parsing import GolemSHOT
from typing import get_type_hints, get_args

# syntax from http://golem.fjfi.cvut.cz/shotdir/54395/Operation/Discharge/Styles/index.html
# execute via Dirigent.sh --discharge <args>  (http://golem.fjfi.cvut.cz/shotdir/54599/Dirigent.sh)

_SAFE_TEXT = re.compile(r"[A-Za-z0-9 _.,:=()\#+/-]{1,2000}")

# immutable, validated at construction
frozen = partial(dataclass, frozen=True, kw_only=True)


#region Enums
class DischargeStyle(Enum):
    STANDARD                       = 'standard'
    STANDARD_WITH_STABILIZATION    = 'standard-ws'  # from Dirigent.sh -d shortcuts
    STANDARD_WITHOUT_STABILIZATION = 'standard-wos'
    REMOTE    = 'remote'  # ?
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

# moved to golemLLM.core.types

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
    # Upon further investigation of latest documented Dirigent.sh usage I have found
    # that OperationHigherPower parameters are a part of the operation.discharge section,
    # thus the parameters are mirrored here, manually.  # ?
    voice:                Optional[Toggle] = None
    wg_voice:             Optional[Toggle] = None
    RawDataAcquiring:     Optional[Toggle] = None
    analysis:             Optional[Toggle] = None
    diagnostics_onstage:  Optional[Toggle] = None
    diagnostics_offstage: Optional[Toggle] = None
    infrastructure:       Optional[Toggle] = None


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
    S_mode: Optional[str] = None
    U_cd:   int = bounded(0, 900)  # V
    U_Bt:   int = bounded(0, 1200)  # V
    t_Bt:   int = bounded(0, 10000)  # us
    t_cd:   int = bounded(0, 10000)  # us
    O_Bt:   AngularDirection
    O_cd:   AngularDirection
    Cht_bt: Optional[int] = None
    Cht_cd: Optional[int] = None


@frozen
class InfrastructurePreionization(Section):
    SECTION: ClassVar[str] = "infrastructure.preionization"
    S_device: Optional[PreionizationDevice] = None
    SW_main:  Optional[Toggle] = None
    U_heater: Optional[int] = None
    U_accel:  Optional[int] = None


# working gas to be one class per mode
@frozen
class WorkingGasRequest(Section):
    SECTION: ClassVar[str] = "infrastructure.workinggas"
    S_mode: str
    S_gas:  WorkingGas
    p_H:    Optional[float] = field(default=0)  # mPa
    U_v:    Optional[float] = field(default=0)  # V


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
    position:    Optional[Millimetres] = bounded(0, 100)  # mm


@frozen
class InfrastructureGasPuffing(Section):
    SECTION: ClassVar[str] = "infrastructure.gaspuffing"
    waveform: Waveform


@frozen
class InfrastructureCurrentStabilization(Section):
    SECTION: ClassVar[str] = "infrastructure.currentstabilization"
    main_switch: Optional[Toggle] = None
    waveform:    Optional[Waveform] = None


@frozen
class DiagnosticsRakeProbe(Section):
    SECTION: ClassVar[str] = "diagnostics.rakeprobe"
    r_First_Tip:     Optional[Millimetres] = bounded(hi=100, default=None)
    r_first_fip:     Optional[Millimetres] = bounded(hi=100, default=None)
    phi_First_Tip:   Optional[Degrees] = None
    X_mod:           Optional[PinMask] = None
    I_SilverBox:     Optional[float] = None
    r_manipulator:   Optional[Millimetres] = None
    phi_manipulator: Optional[Degrees] = None

@frozen
class DiagnosticsDoubleRakeProbe(Section):
    SECTION: ClassVar[str] = "diagnostics.doublerakeprobe"
    r_first_tip: Optional[Millimetres] = bounded(hi=160, default=None)  # wall at ~160 mm ?
    X_mod:       Optional[PinMask] = None
    I_SilverBox: Optional[float] = bounded(hi=12, default=None)  # A


@frozen
class DiagnosticsDoubleLangballPenProbe(Section):
    SECTION: ClassVar[str] = "diagnostics.doublelangballpenprobe"
    r_lp_tip:    Optional[Millimetres] = bounded(hi=160, default=None)  # wall at ~160 mm ?


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

#region Proposal class
@frozen
class GolemPROPOSAL:
    # to order, None means argument not in command

    # Operation
    discharge:              OperationDischarge
    higherpower:            Optional[OperationHigherPower] = None

    bt_ecd:                 InfrastructureBtEcd
    preionization:          Optional[InfrastructurePreionization] = None
    workinggas:             WorkingGasRequest
    positionstabilization:  Optional[InfrastructurePositionStabilization] = None
    #biasingelectrode:       Optional[InfrastructureBiasingElectrode] = None
    #gasspuffing:            Optional[InfrastructureGasPuffing] = None
    doublelangballpenprobe: Optional[DiagnosticsDoubleLangballPenProbe] = None
    currentstabilization:   Optional[InfrastructureCurrentStabilization] = None

    doublerakeprobe:        Optional[DiagnosticsDoubleRakeProbe] = None
    rakeprobe:              Optional[DiagnosticsRakeProbe] = None
    limitermirnovcoils:     Optional[DiagnosticsLimiterMirnovCoils] = None
    scintillationprobes:    Optional[DiagnosticsScintillationProbes] = None
    stripdetector:          Optional[DiagnosticsStripDetector] = None
    
    ScanDefinition:         Optional[str] = None  # ?
    comment:                str

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
        return "./Dirigent.sh " + " ".join(a if a.startswith("--") else f'"{a}"' for a in self.to_argv())

    def flat(self) -> dict[str, object]:
        out = {f"{s.SECTION}.{k}": _plain(v) for s in self.sections() for k, v in s.items()}
        out["comment"] = self.comment
        if self.ScanDefinition is not None:
            out["ScanDefinition"] = self.ScanDefinition
        return out

    def diff(self, other: "GolemPROPOSAL") -> list[dict]:
        a, b = self.flat(), other.flat()
        keys = list(a) + [k for k in b if k not in a]
        return [{"param": k, "previous": b.get(k), "proposed": a.get(k)}
                for k in keys if a.get(k) != b.get(k)]
#endregion

#region Parsing from files to proposal
class GolemPROPOSALparser:
    def __init__(self, client):
        self.client = client

    def parse(self, shot: GolemSHOT) -> GolemPROPOSAL:

        discharge = OperationDischarge(
            style=shot.discharge_style,
            voice=shot.higherpower_voice,
            wg_voice=shot.higherpower_wg_voice,
            RawDataAcquiring=shot.higherpower_rawdataacquiring,
            analysis=shot.higherpower_analysis,
            diagnostics_onstage=shot.higherpower_diagnostics_onstage,
            diagnostics_offstage=shot.higherpower_diagnostics_offstage,
            infrastructure=shot.higherpower_infrastructure,
        )
        higherpower = OperationHigherPower(
            voice=shot.higherpower_voice,
            wg_voice=shot.higherpower_wg_voice,
            RawDataAcquiring=shot.higherpower_rawdataacquiring,
            analysis=shot.higherpower_analysis,
            diagnostics_onstage=shot.higherpower_diagnostics_onstage,
            diagnostics_offstage=shot.higherpower_diagnostics_offstage,
            infrastructure=shot.higherpower_infrastructure,
        )

        bt_ecd = InfrastructureBtEcd(
            S_mode = shot.X_BtEcd_mode_X,
            U_cd = shot.U_cd_request_V,
            U_Bt = shot.U_bt_request_V,
            t_cd = shot.t_cd_request_us,
            t_Bt = shot.t_bt_request_us,
            O_Cd = AngularDirection.CLOCKWISE if shot.O_cd_request_clockwise_b else AngularDirection.COUNTERCLOCKWISE,
            O_Bt = AngularDirection.CLOCKWISE if shot.O_bt_request_clockwise_b else AngularDirection.COUNTERCLOCKWISE,
        )
        preionization = InfrastructurePreionization(
            S_device = shot.device_preionization_X,
            SW_main  = Toggle.ON if shot.switch_preionization_main_b else Toggle.OFF,
            U_heater = shot.U_preionization_heater_V,
            U_accel  = shot.U_preionization_accel_V,
        )
        workinggas = WorkingGasRequest(
            S_mode = shot.mode_workinggas_X,
            S_gas  = shot.X_workinggas_X,
            p_H    = WorkingGas(shot.p_workinggas_mPa),
            U_v    = shot.U_workinggas_valve_V,
        )
        positionstabilization = InfrastructurePositionStabilization(
            main_switch = Toggle.ON if shot.switch_positionstabilization_main_b else Toggle.OFF,
            radial_switch = Toggle.ON if shot.switch_positionstabilization_radial_b else Toggle.OFF,
            radial_waveform = shot.waveform_positionstabilization_radial_us_V,
            vertical_switch = Toggle.ON if shot.switch_positionstabilization_vertical_b else Toggle.OFF,
            vertical_waveform = shot.waveform_positionstabilization_vertical_us_V
        )
        currentstabilization = InfrastructureCurrentStabilization(

            main_switch = Toggle.ON if shot.switch_currentstabilization_main_b else Toggle.OFF,
            waveform = shot.waveform_currentstabilization_us_V
        )

        doublelangballpenprobe = DiagnosticsDoubleLangballPenProbe(
            r_lp_tip = shot.r_doublelangballpenprobe_tip_mm
        )
        limitermirnovcoils = DiagnosticsLimiterMirnovCoils(
            vacuum_shot = shot.shot_limitermirnovcoils_vacuum_ID
        )
        rakeprobe = DiagnosticsRakeProbe(
            r_first_tip = shot.r_rakeprobe_first_pin_mm
        )

        # TODO:

        #discharge:              OperationDischarge
        #higherpower:            Optional[OperationHigherPower] = None
    
        #bt_ecd:                 InfrastructureBtEcd
        #preionization:          Optional[InfrastructurePreionization] = None
        #workinggas:             WorkingGasRequest
        #positionstabilization:  Optional[InfrastructurePositionStabilization] = None
        #currentstabilization:   Optional[InfrastructureCurrentStabilization] = None

        #doublelangballpenprobe: Optional[DiagnosticsDoubleLangballPenProbe] = None
        #doublerakeprobe:        Optional[DiagnosticsDoubleRakeProbe] = None
        #rakeprobe:              Optional[DiagnosticsRakeProbe] = None
        #limitermirnovcoils:     Optional[DiagnosticsLimiterMirnovCoils] = None
        #scintillationprobes:    Optional[DiagnosticsScintillationProbes] = None
        #stripdetector:          Optional[DiagnosticsStripDetector] = None

        #ScanDefinition:         Optional[str] = None  # ?
        #comment:                str
        
#endregion

#region OBSOLETE Parsing from command to proposal
class GolemPROPOSALparserOBSOLETE:
    def __init__(self, client): 
        self.client = client

    # Utility logic

    def _unwrap(self, tp):  # Optional[X] -> X; X -> X  # fix: `type` shadowed the builtin
        return next((a for a in get_args(tp) if a is not type(None)), tp)

    def _parse(self, tp, raw):  # parse string into type  # fix: same rename
        raw = raw.strip("'")  # remove quotes for string-like sub-arguments
        if tp is PinMask:
            return PinMask(int(raw[::-1], 2)) # reverse string to match P1 leftmost  # fix: parentheses
        if tp is Waveform:
            return Waveform(tuple(tuple(map(float, p.split(","))) for p in raw.split(";")))
        if issubclass(tp, Enum):
            return tp(type(next(iter(tp)).value)(raw))
        return tp(raw)  # int, float, string
    
    # Section logic

    _PAIR_REGEX_C = re.compile(r"(\w+)=('[^']*'|[^,]*)")  # key=value; commas inside '...' (waveforms) are kept

    _EXCLUSION = {}  # _EXCLUSION items need special handling
    _EXCLUSION_OVERRIDES = {}  # str : function(self, pairs)
    _SECTIONS = {cl.SECTION: cl for cl in Section.__subclasses__()}

    def _section(self, section: str, body: str):
        pairs = dict(self._PAIR_REGEX_C.findall(body))

        if section in self._EXCLUSION:
            return self._EXCLUSION_OVERRIDES[section](self, pairs)
        elif section in self._SECTIONS:
            cls = self._SECTIONS[section]  # `cls` means class
        else:
            raise ValueError(f"Unknown section: {section}")
        
        hints = get_type_hints(cls)

        kwargs = {}  # keyword arguments
        for f in fields(cls):
            if f.name not in pairs: continue  # field not in command?
            value = self._parse(self._unwrap(hints[f.name]), pairs.pop(f.name))  # parse into real type
            if f.init:
                kwargs[f.name] = value
            elif value != f.default:
                raise ValueError(f"Field {f.name} is not init=True but has non-default value {value}")
        if pairs:  # recognized fields are popped, remains are unknown
            leftover = ", ".join(f"{k}={v}" for k, v in pairs.items())
            raise ValueError(f"Unknown fields for {cls.SECTION}: {leftover}")

        return cls(**kwargs)

    # Overhead logic

    def parse(self, command_classical: str) -> GolemPROPOSAL:
        text = command_classical
        command = re.sub(r"\\[ \t]*\n", " ", text)  # Remove line continuations

        argv = shlex.split(command)
        argv = argv[argv.index("--discharge") + 1:]  # skip leading ./Dirigent.sh & --discharge
        if len(argv) % 2:
            raise ValueError(f"Option {argv[-1]} has no value (trailing option in command).")

        kwargs = {}  # keyword arguments

        NON_SECTION_ARGUMENTS = {"comment", "ScanDefinition"}

        # Handle data
        for flag, value in zip(argv[::2], argv[1::2]):
            name = flag.removeprefix("--")
            if name in NON_SECTION_ARGUMENTS:
                kwargs[name] = value
            else:
                kwargs[name.split(".")[-1]] = self._section(name, value)

        # Handle non-optional data (extra)
        for required in { "discharge", "bt_ecd", "workinggas", "comment"}:
            if required not in kwargs:  # fix: a missing key raised KeyError, never reached the ValueError
                raise ValueError(f"Required parameter {required} not found in command to parse to proposal object.")
            #kwargs[required] = kwargs[required] if kwargs[required] else raise ValueError("")
        #kwargs["comment"] = kwargs["comment"] if kwargs["comment"] is not None else "/NO COMMENT/"  # fix: kwags -> kwargs
        
        return GolemPROPOSAL(**kwargs)
#endregion

#region Rulesets, helpers
def _fmt(v) -> str:
    if isinstance(v, Millimetres):
        return f"'{v:g}'"
    if isinstance(v, (Waveform, PinMask)):
        return f"'{v}'"
    if isinstance(v, Enum):
        return f"'{v.value}'" if isinstance(v.value, str) else str(v.value)
    if isinstance(v, str):
        return f"'{v}'"
    if isinstance(v, sfloat):
        return f"'{v:g}'"
    if isinstance(v, float):
        return f"{v:g}"
    metadata = getattr(v, "metadata", None)
    if metadata is not None and (metadata.lo is not None or metadata.hi is not None):
        return f"{v:g}"
    return str(v)

def _plain(v):
    if isinstance(v, (Waveform, PinMask)):
        return str(v)
    if isinstance(v, Enum):
        return v.value
    return v
#endregion
