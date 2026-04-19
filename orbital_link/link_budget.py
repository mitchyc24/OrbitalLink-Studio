"""Link budget calculations with DVB-S2X support."""

from dataclasses import dataclass
from math import log10

from orbital_link.modcod import get_modcod
from orbital_link.models import OBFUSCATED_BEAM_DIAMETER_KM


BOLTZMANN_DBW_HZ = -228.6


@dataclass(frozen=True)
class LinkBudgetInput:
    eirp_dbw: float
    slant_range_km: float
    frequency_ghz: float
    atmospheric_loss_db: float
    g_over_t_db_k: float
    allocated_bandwidth_hz: float
    modcod_name: str
    priority_level: int = 1
    is_obfuscated: bool = False
    nominal_beam_diameter_km: float = 30.0


@dataclass(frozen=True)
class LinkBudgetResult:
    free_space_loss_db: float
    obfuscation_penalty_db: float
    c_over_n0_db_hz: float
    esn0_db: float
    link_margin_db: float
    throughput_bps: float
    spectral_efficiency_bps_hz: float


def free_space_path_loss_db(slant_range_km: float, frequency_ghz: float) -> float:
    return 92.45 + 20 * log10(slant_range_km) + 20 * log10(frequency_ghz)


def obfuscation_penalty_db(is_obfuscated: bool, nominal_beam_diameter_km: float) -> float:
    if not is_obfuscated:
        return 0.0
    if nominal_beam_diameter_km <= 0:
        raise ValueError("nominal_beam_diameter_km must be positive.")
    return 20 * log10(OBFUSCATED_BEAM_DIAMETER_KM / nominal_beam_diameter_km)


def _priority_weight(priority_level: int) -> float:
    return max(0.25, min(priority_level, 10))


def calculate_link_budget(data: LinkBudgetInput) -> LinkBudgetResult:
    modcod = get_modcod(data.modcod_name)
    fspl_db = free_space_path_loss_db(data.slant_range_km, data.frequency_ghz)
    penalty_db = obfuscation_penalty_db(data.is_obfuscated, data.nominal_beam_diameter_km)
    effective_eirp_dbw = data.eirp_dbw - penalty_db

    c_over_n0_db_hz = (
        effective_eirp_dbw
        - fspl_db
        - data.atmospheric_loss_db
        + data.g_over_t_db_k
        - BOLTZMANN_DBW_HZ
    )

    symbol_rate_hz = data.allocated_bandwidth_hz
    esn0_db = c_over_n0_db_hz - 10 * log10(symbol_rate_hz)
    link_margin_db = esn0_db - modcod.required_esn0_db

    weighted_bandwidth = data.allocated_bandwidth_hz * _priority_weight(data.priority_level)
    throughput_bps = weighted_bandwidth * modcod.spectral_efficiency_bps_hz

    return LinkBudgetResult(
        free_space_loss_db=fspl_db,
        obfuscation_penalty_db=penalty_db,
        c_over_n0_db_hz=c_over_n0_db_hz,
        esn0_db=esn0_db,
        link_margin_db=link_margin_db,
        throughput_bps=throughput_bps,
        spectral_efficiency_bps_hz=modcod.spectral_efficiency_bps_hz,
    )
