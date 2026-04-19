"""Core domain models for scenarios and link simulation."""

from dataclasses import dataclass, field
from datetime import UTC, datetime


LEO_ALTITUDE_KM = 1400.0
OBFUSCATED_BEAM_DIAMETER_KM = 100.0


@dataclass(frozen=True)
class Satellite:
    id: int
    name: str
    altitude_km: float = LEO_ALTITUDE_KM
    uplink_freq_ghz: float = 29.5
    downlink_freq_ghz: float = 19.45
    eirp_dbw: float = 60.0


@dataclass(frozen=True)
class Beam:
    id: int
    satellite_id: int
    beam_width_km: float
    peak_gain_dbi: float
    boresight_lat: float
    boresight_long: float


@dataclass(frozen=True)
class TerminalProfile:
    id: int
    model_name: str
    antenna_gain_dbi: float
    g_over_t_db_k: float
    noise_temp_k: float


@dataclass(frozen=True)
class UserTerminal:
    id: int
    profile_id: int
    lat: float
    long: float
    is_obfuscated: bool
    priority_level: int
    elevation_angle_deg: float
    allocated_bandwidth_hz: float
    nominal_beam_diameter_km: float


@dataclass
class Scenario:
    id: int
    name: str
    target_satellite: Satellite
    terminals: list[UserTerminal] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
