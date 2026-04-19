"""DVB-S2X MODCOD lookup utilities."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModCod:
    name: str
    spectral_efficiency_bps_hz: float
    required_esn0_db: float


MODCOD_TABLE: tuple[ModCod, ...] = (
    ModCod(name="QPSK_1_4", spectral_efficiency_bps_hz=0.49, required_esn0_db=-2.35),
    ModCod(name="QPSK_1_2", spectral_efficiency_bps_hz=0.99, required_esn0_db=1.10),
    ModCod(name="8PSK_3_5", spectral_efficiency_bps_hz=1.78, required_esn0_db=4.90),
    ModCod(name="8PSK_2_3", spectral_efficiency_bps_hz=1.98, required_esn0_db=6.20),
    ModCod(name="16APSK_3_4", spectral_efficiency_bps_hz=2.96, required_esn0_db=8.80),
    ModCod(name="32APSK_4_5", spectral_efficiency_bps_hz=3.96, required_esn0_db=13.40),
)


def get_modcod(name: str) -> ModCod:
    for modcod in MODCOD_TABLE:
        if modcod.name == name:
            return modcod
    raise ValueError(f"Unknown DVB-S2X MODCOD '{name}'.")
