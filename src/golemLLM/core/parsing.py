# Data parsing

from golemLLM.core.types import Waveform
from ..helper import find_between
from decimal import Decimal

def summaryGET(str) -> tuple[str, str]:
    """Returns a (key, value) tuple from a summary.
    E.g.: S_device='HotCathode',SW_main='on',U_heater=100,U_accel=100
    is turned to ("S_device", "HotCathode"), ..."""
    return [p.split("=", 1) for p in str.split(",")]

class GolemSHOT:
    def __init__(self, shotID, client):
        if (shotID == 0):
            shotID = client.getLatestShotID()
        elif (not client.shotProbeHEAD(shotID)):
            raise ValueError(f"Shot ID {shotID} does not exist in the shot database.")
        self._shotID = shotID

        self.client = client
        self.verbose = client.verbose

    # Concrete shot functionality

    #region Helpers

    def   simUTF8(self, path): # Simple UTF-8 file value processing
        return self.client.getShotFileCached(self._shotID, path).decode('utf-8').strip()
    def simUTF8nl(self, path): # Simple UTF-8 file value processing with newline replacement
        return self.simUTF8s(path).replace('\\n', '\n')

    def simUTF8s(self, path): return str(self.simUTF8(path))
    def simUTF8i(self, path): return int(self.simUTF8(path))
    def simUTF8f(self, path): return float(self.simUTF8(path))

    def simTableGen1f2f(self, path):
        data = self.simUTF8s(path)
        lines = [line for line in data.splitlines()]
        for line in lines:
            line = line.strip()
            if not line: continue
            if line.startswith('#'): continue

            a_str, b_str = line.split(",")
            yield Decimal(a_str), Decimal(b_str)

    #endregion
    #region Basic information

    @property
    def ID(self):
        """Shot No (shot 0 as true shot number)"""
        return self._shotID # Integer
    @property
    def timestamp(self):
        """Shot timestamp"""
        return self.simUTF8("shot_date") + " " + self.simUTF8("shot_time")
    @property
    def comment(self):
        """Shot comment"""
        return self.simUTF8("comment")
    @property
    def setup(self):
        """Shot whole.setup information"""
        return self.simUTF8nl("whole.setup")
    @property
    def command_arranged(self):
        """Well-arranged form shot command"""
        result = find_between(self.simUTF8s("Production/Parameters/FullCommandLine"),
            "Well-arranged command line form:\n========================\n\n",
            "\n\nClassical command line form:\n========================")
        if not result:
            raise ValueError("Could not find the well-arranged form shot command in the FullCommandLine file.")
        return result.strip()
    @property
    def command_classical(self):
        """Classical form shot command"""
        return self.simUTF8s("Production/Parameters/CommandLine")
    #    _, _, result = self.simUTF8s("Production/Parameters/FullCommandLine") .partition(
    #        "Classical command line form:\n========================\n\n")
    #    if not result:
    #        raise ValueError("Could not find the classical form shot command in the FullCommandLine file.")
    #    return result.strip()

    #endregion
    #region Other & Request parameters

    # Discharge basics

    def discharge_style(self) -> str:
        """Discharge parameter: style"""
        return self.simUTF8s("Operation/Discharge/Parameters/style")

    # HigherPower settings

    def higherpower_voice(self) -> bool:
        """Papouch voice configuration"""
        return self.simUTF8s("Operation/HigherPower/Parameters/voice") == "on"
    def higherpower_wg_voice(self) -> bool:
        """Papuch working gas [?] voice configuration"""
        return self.simUTF8s("Operation/HigherPower/Parameters/wg_voice") == "on"
    def higherpower_rawdataacquiring(self) -> bool:
        """Raw data acquiring configuration"""
        return self.simUTF8s("Operation/HigherPower/Parameters/rawdataacquiring") == "on"
    def higherpower_analysis(self) -> bool:
        """Analysis configuration"""
        return self.simUTF8s("Operation/HigherPower/Parameters/analysis") == "on"
    def higherpower_diagnostics_onstage(self) -> bool:
        """On-stage diagnostics configuration"""
        return self.simUTF8s("Operation/HigherPower/Parameters/diagnostics_onstage") == "on"
    def higherpower_diagnostics_offstage(self) -> bool:
        """Off-stage diagnostics configuration"""
        return self.simUTF8s("Operation/HigherPower/Parameters/diagnostics_offstage") == "on"
    def higherpower_infrastructure(self) -> bool:
        """Infrastructure configuration"""
        return self.simUTF8s("Operation/HigherPower/Parameters/infrastructure") == "on"
    
    #endregion
    #region Technological parameters

    @property
    def p_chamber_before_discharge_mPa(self) -> float:
        """Chamber pressure before discharge"""
        return self.simUTF8f("Operation/Discharge/p_chamber_pressure_before_discharge")
    @property
    def p_chamber_predischarge_mPa(self) -> float:
        """Chamber pressure pre-discharge (just before)"""
        return self.simUTF8f("Operation/Discharge/p_chamber_pressure_predischarge")
    @property
    def p_working_gas_discharge_request_mPa(self) -> float:
        """Requested working gas pressure"""
        return self.simUTF8f("Operation/Discharge/p_working_gas_discharge_request")
    @property
    def X_working_gas_discharge_request(self) -> str:
        """Requested working gas type"""
        return self.simUTF8s("Operation/Discharge/X_working_gas_discharge_request")

    @property
    def X_BtEcd_mode_X(self) -> str:
        """Mode for Bt_Ecd"""
        return self.simUTF8s("Infrastructure/Bt_Ecd/Parameters/s_mode")

    # Toroidal magnetic field (Bt) bank

    @property
    def U_bt_request_V(self) -> float:
        """Requested Bt capacitor charging voltage [V]"""
        return self.simUTF8f
    @property
    def O_bt_request_clockwise_b(self) -> bool:
        """Requested Bt discharge direction, CW=True"""
        return summaryGET(self.simUTF8f("Production/Parameters/infrastructure.bt_ecd"))["O_Bt"] == "CW"
    @property
    def t_bt_request_us(self) -> float:
        """Requested Bt discharge time [µs]"""
        return float(summaryGET(self.simUTF8f("Production/Parameters/infrastructure.bt_ecd"))["t_Bt"])
    def t_bt_charging_s(self) -> float:
        """Bt charging time [s]"""
        return self.simUTF8f("Infrastructure/Bt_Ecd/Parameters/cht_bt") or None

    # Current drive (CD) bank

    @property
    def U_cd_request_V(self) -> float:
        """Requested CD capacitor charging voltage [V]"""
        return float(summaryGET(self.simUTF8f("Production/Parameters/infrastructure.bt_ecd"))["U_cd"])
    @property
    def O_cd_request_clockwise_b(self) -> bool:
        """Requested CD discharge direction, CW=True"""
        return summaryGET(self.simUTF8f("Production/Parameters/infrastructure.bt_ecd"))["O_cd"] == "CW"
    @property
    def t_cd_request_us(self) -> float:
        """Requested CD discharge time [µs]"""
        return float(summaryGET(self.simUTF8f("Production/Parameters/infrastructure.bt_ecd"))["t_cd"])
    @property
    def t_cd_charging_s(self) -> float:
        """CD charging time [s]"""
        return self.simUTF8f("Infrastructure/Bt_Ecd/Parameters/cht_cd") or None

    #endregion
    #region Plasma

    @property
    def bool_plasma(self) -> bool:
        """Plasma?"""
        return self.simUTF8f("Diagnostics/PlasmaDetection/Results/b_plasma") == 1.0
    @property
    def t_plasma_duration_ms(self) -> float:
        """Plasma duration [ms], NaN without plasma"""
        return self.simUTF8f("Diagnostics/PlasmaDetection/Results/t_plasma_duration"
                             ) if self.bool_plasma else float('nan')

    @property
    def t_plasma_start_ms(self) -> float:
        """Plasma start time [ms], NaN without plasma"""
        return self.simUTF8f("Diagnostics/PlasmaDetection/Results/t_plasma_start"
                             ) if self.bool_plasma else float('nan')

    @property
    def t_plasma_end_ms(self) -> float:
        """Plasma end time [ms], NaN without plasma"""
        return self.simUTF8f("Diagnostics/PlasmaDetection/Results/t_plasma_end"
                             ) if self.bool_plasma else float('nan')

    @property
    def t_plasma_flattop_duration_ms(self) -> float:
        """Plasma flattop duration [ms], NaN without plasma"""
        return self.simUTF8f("Diagnostics/PlasmaDetection/Results/t_plasma_qs_duration"
                             ) if self.bool_plasma else float('nan')

    @property
    def t_plasma_flattop_start_ms(self) -> float:
        """Plasma flattop start time [ms], NaN without plasma"""
        return self.simUTF8f("Diagnostics/PlasmaDetection/Results/t_plasma_qs_start"
                             ) if self.bool_plasma else float('nan')

    @property
    def t_plasma_flattop_end_ms(self) -> float:
        """Plasma flattop end time [ms], NaN without plasma"""
        return self.simUTF8f("Diagnostics/PlasmaDetection/Results/t_plasma_qs_end"
                             ) if self.bool_plasma else float('nan')

    #endregion
    #region Plasma parameters

    @property
    def U_plasma_loop_mean_V(self) -> float:
        """Plasma loop voltage [V], regardless of plasma"""
        return self.simUTF8f("Diagnostics/BasicDiagnostics/Results/U_loop_mean")
    @property
    def U_plasma_loop_max_V(self) -> float:
        """Plasma loop voltage max [V], regardless of plasma"""
        return self.simUTF8f("Diagnostics/BasicDiagnostics/Results/U_loop_max")
    @property
    def U_plasma_loop_breakdown_V(self) -> float:
        """Plasma loop voltage breakdown [V], regardless of plasma"""
        try: return self.simUTF8f("Diagnostics/BasicDiagnostics/Results/U_loop_breakdown")
        except FileNotFoundError: return float('nan') # Usually not available

    #endregion
    #region On stage diagnostics

    @property
    def tabgen_Xt_YUloop_ms_V(self) -> map:
        """Map generator of x: time (t) [ms] to y: plasma loop voltage (Uloop) [V]"""
        return self.simTableGen1f2f("Diagnostics/BasicDiagnostics/Results/U_loop.csv")
    @property
    def tabgen_Xt_YBt_ms_T(self) -> map:
        """Map generator of x: time (t) [ms] to y: toroidal magnetic field (Bt) [T]"""
        return self.simTableGen1f2f("Diagnostics/BasicDiagnostics/Results/Bt.csv")
    @property
    def tabgen_Xt_YIp_ms_I(self) -> map:
        """Map generator of x: time (t) [ms] to y: plasma current (Ip) [kA]"""
        return self.simTableGen1f2f("Diagnostics/BasicDiagnostics/Results/Ip.csv")
    @property
    def tabgen_Xt_YIch_ms_I(self) -> map:
        """Map generator of x: time (t) [ms] to y: chamber current (Ich) [kA]"""
        return self.simTableGen1f2f("Diagnostics/BasicDiagnostics/Results/Ich.csv")

    #endregion
    #region Preionization

    @property
    def device_preionization_X(self) -> str:
        """Preionization device"""
        return summaryGET(self.simUTF8s("Production/Parameters/infrastructure.preionization"))["S_device"]
    @property
    def switch_preionization_main_b(self) -> bool:
        """Preionization main switch, on=True"""
        return summaryGET(self.simUTF8s("Production/Parameters/infrastructure.preionization"))["SW_main"] == "on"
    @property
    def U_preionization_heater_V(self) -> float:
        """Preionization U_heater"""
        return float(summaryGET(self.simUTF8s("Production/Parameters/infrastructure.preionization"))["U_heater"])
    @property
    def U_preionization_accel_V(self) -> float:
        """Preionization U_accel"""
        return float(summaryGET(self.simUTF8s("Production/Parameters/infrastructure.preionization"))["U_accel"])

    #endregion
    #region Working gas

    @property
    def mode_workinggas_X(self) -> str:
        """Working gas mode"""
        return summaryGET(self.simUTF8s("Production/Parameters/infrastructure.working_gas"))["S_mode"]
    @property
    def X_workinggas_X(self) -> str:
        """Working gas type"""
        return summaryGET(self.simUTF8s("Production/Parameters/infrastructure.working_gas"))["S_gas"]
    @property
    def p_workinggas_mPa(self) -> float:
        """Working gas pressure"""
        return float(summaryGET(self.simUTF8s("Production/Parameters/infrastructure.working_gas"))["p_H"])
    @property
    def U_workinggas_valve_V(self) -> float:
        """Working gas valve voltage"""
        return float(summaryGET(self.simUTF8s("Production/Parameters/infrastructure.working_gas"))["U_v"])

    #endregion
    #region Position stabilization, current stabilization

    @property
    def switch_positionstabilization_main_b(self) -> bool:
        """Position stabilization main switch, on=True"""
        return summaryGET(self.simUTF8s("Production/Parameters/infrastructure.positionstabilization"))["main_switch"] == "on"
    @property
    def switch_positionstabilization_radial_b(self) -> bool:
        """Position stabilization radial switch, on=True"""
        return summaryGET(self.simUTF8s("Production/Parameters/infrastructure.positionstabilization"))["radial_switch"] == "on"
    @property
    def waveform_positionstabilization_radial_us_V(self) -> Waveform:
        """Position stabilization radial waveform, time [µs], voltage [V]."""
        return Waveform.of(*(tuple(map(float, p.split(","))) for p in summaryGET(
            self.simUTF8s("Production/Parameters/infrastructure.positionstabilization"))["radial_waveform"].split(";")))
    @property
    def switch_positionstabilization_vertical_b(self) -> bool:
        """Position stabilization vertical switch, on=True"""
        return summaryGET(self.simUTF8s("Production/Parameters/infrastructure.positionstabilization"))["vertical_switch"] == "on"
    @property
    def waveform_positionstabilization_vertical_us_V(self) -> Waveform:
        """Position stabilization vertical waveform, time [µs], voltage [V]."""
        return Waveform.of(*(tuple(map(float, p.split(","))) for p in summaryGET(
            self.simUTF8s("Production/Parameters/infrastructure.positionstabilization"))["vertical_waveform"].split(";")))

    @property
    def switch_currentstabilization_main_b(self) -> bool:
        """Current stabilization main switch, on=True"""
        return summaryGET(self.simUTF8s("Production/Parameters/infrastructure.currentstabilization"))["main_switch"] == "on"
    @property
    def waveform_currentstabilization_us_V(self) -> Waveform:
        """Current stabilization waveform, time [µs], voltage [V]."""
        return Waveform.of(*(tuple(map(float, p.split(","))) for p in summaryGET(
            self.simUTF8s("Production/Parameters/infrastructure.currentstabilization"))["waveform"].split(";")))
    
    #endregion
    #region Diagnostics: Probes

    @property
    def r_doublelangballpenprobe_tip_mm(self) -> float:
        """Double Langball Pen Probe tip distance from poloidal center [mm]"""
        return summaryGET(self.simUTF8f("Production/Parameters/infrastructure.doublelangballpenprobe"))["r_lp_tip"]

    @property
    def shot_limitermirnovcoils_vacuum_ID(self) -> int:
        """Limiter Mirnov Coils vacuum shot ID"""
        return summaryGET(self.simUTF8f("Production/Parameters/diagnostics.limitermirnovcoils"))["vacuum_shot"]

    @property
    def r_rakeprobe_first_pin_mm(self) -> float:
        """Rake Probe first pin distance from poloidal center[mm]"""
        return summaryGET(self.simUTF8f("Production/Parameters/diagnostics.rakeprobe"))["r_first_fip"]
    #endregion