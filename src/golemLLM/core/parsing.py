# Data parsing

from ..helper import find_between
from decimal import Decimal

class GolemSHOT:
    def __init__(self, shotID, client):
        if (shotID == 0):
                    result = client.getShotFile(shotID, "shot_no")
                    shotID = int(result.decode('utf-8').strip())
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
    def simUTF8d(self, path): return Decimal(self.simUTF8(path))

    def simTableGen1f2f(self, path):
        data = self.simUTF8s(path)
        lines = [line for line in data.splitlines()]
        for line in lines:
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
        _, _, result = self.simUTF8s("Production/Parameters/FullCommandLine") .partition(
            "Classical command line form:\n========================\n\n")
        if not result:
            raise ValueError("Could not find the classical form shot command in the FullCommandLine file.")
        return result.strip()

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

    # Toroidal magnetic field (Bt) bank

    @property
    def U_bt_request_V(self) -> float:
        """Requested Bt capacitor charging voltage [V]"""
        return self.simUTF8f("Operation/Discharge/U_bt_discharge_request")
    @property
    def U_bt_meas_dcd_V_FALLBACK(self) -> float:
        """Measured Bt capacitor voltage during discharge [V]"""
        #return self.simUTF8f("Operation/Discharge/U_bt_discharge_meas_dcd")
        result = find_between(self.simUTF8s("index.html"), "\\(U\\sub{C_{PTC}}\\sup{dcd}\\)=", " V")
        if result: return float(result)
        else:
            raise ValueError("Could not find the measured Bt capacitor voltage in the index.html file.")
    @property
    def t_bt_request_us(self) -> int:
        """Requested Bt discharge time [µs]"""
        return self.simUTF8f("Operation/Discharge/t_bt_discharge_request")

    # Current drive (CD) bank

    @property
    def U_cd_request_V(self) -> float:
        """Requested CD capacitor charging voltage [V]"""
        return self.simUTF8f("Operation/Discharge/U_cd_discharge_request")
    @property
    def U_cd_meas_dcd_V_FALLBACK(self) -> float:
        """Measured CD capacitor voltage during discharge [V]"""
        #return self.simUTF8f("Operation/Discharge/U_cd_discharge_meas_dcd")
        result = find_between(self.simUTF8s("index.html"), "\\(U\\sub{C_{TFC}}\\sup{launch}\\)=", " V")
        if result: return float(result)
        else:
            raise ValueError("Could not find the measured CD capacitor voltage in the index.html file.")
    @property
    def t_cd_request_us(self) -> int:
        """Requested CD discharge time [µs]"""
        return self.simUTF8f("Operation/Discharge/t_cd_discharge_request")

    #endregion
    #region Plasma

    @property
    def bool_plasma(self) -> bool:
        """Plasma?"""
        return self.simUTF8f("Diagnostics/PlasmaDetection/Results/b_plasma") == 1.0
    @property
    def t_plasma_duration_ms(self) -> float:
        """Plasma duration [ms], -1.0 without plasma"""
        return self.simUTF8f("Diagnostics/PlasmaDetection/Results/t_plasma_duration")
    @property
    def t_plasma_start_ms(self) -> float:
        """Plasma start time [ms], -1.0 without plasma"""
        return self.simUTF8f("Diagnostics/PlasmaDetection/Results/t_plasma_start")
    @property
    def t_plasma_end_ms(self) -> float:
        """Plasma end time [ms], -1.0 without plasma"""
        return self.simUTF8f("Diagnostics/PlasmaDetection/Results/t_plasma_end")
    @property
    def t_plasma_flattop_duration_ms(self) -> float:
        """Plasma flattop duration [ms], -1.0 without plasma"""
        return self.simUTF8f("Diagnostics/PlasmaDetection/Results/t_plasma_qs_duration")
    @property
    def t_plasma_flattop_start_ms(self) -> float:
        """Plasma flattop start time [ms], -1.0 without plasma"""
        return self.simUTF8f("Diagnostics/PlasmaDetection/Results/t_plasma_qs_start")
    @property
    def t_plasma_flattop_end_ms(self) -> float:
        """Plasma flattop end time [ms], -1.0 without plasma"""
        return self.simUTF8f("Diagnostics/PlasmaDetection/Results/t_plasma_qs_end")

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
        return self.simUTF8f(
            "Diagnostics/BasicDiagnostics/Results/U_loop_breakdown") if client.shotProbeHEAD(
                "Diagnostics/BasicDiagnostics/Results/U_loop_breakdown"
            ) else float('nan'); # Usually not available

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
    def tabgen_Xt_YIp_s_I(self) -> map:
        """Map generator of x: time (t) [ms] to y: plasma current (Ip) [kA]"""
        return self.simTableGen1f2f("Diagnostics/BasicDiagnostics/Results/Ip.csv")
    @property
    def tabgen_Xt_YIch_s_I(self) -> map:
        """Map generator of x: time (t) [ms] to y: chamber current (Ich) [kA]"""
        return self.simTableGen1f2f("Diagnostics/BasicDiagnostics/Results/Ich.csv")

    #endregion


    



# Testing

from golemLLM.core.client import GolemCLIENThttp, GolemCLIENTlocal

client = GolemCLIENThttp(cache=True, verbose=True)
#client = GolemCLIENTlocal("/media/user/flashdisk/shots/", cache=True, verbose=True)
shot = GolemSHOT(53202, client)
