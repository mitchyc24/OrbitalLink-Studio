"""Excel import/export for scenario round-trip editing."""

from io import BytesIO

import pandas as pd

from orbital_link.models import Scenario, UserTerminal


TERMINAL_COLUMNS = [
    "id",
    "profile_id",
    "lat",
    "long",
    "is_obfuscated",
    "priority_level",
    "elevation_angle_deg",
    "allocated_bandwidth_hz",
    "nominal_beam_diameter_km",
]


def export_scenario_to_excel(scenario: Scenario) -> bytes:
    terminals_df = pd.DataFrame(
        [
            {
                "id": terminal.id,
                "profile_id": terminal.profile_id,
                "lat": terminal.lat,
                "long": terminal.long,
                "is_obfuscated": terminal.is_obfuscated,
                "priority_level": terminal.priority_level,
                "elevation_angle_deg": terminal.elevation_angle_deg,
                "allocated_bandwidth_hz": terminal.allocated_bandwidth_hz,
                "nominal_beam_diameter_km": terminal.nominal_beam_diameter_km,
            }
            for terminal in scenario.terminals
        ]
    )

    summary_df = pd.DataFrame(
        [
            {
                "scenario_id": scenario.id,
                "scenario_name": scenario.name,
                "satellite_id": scenario.target_satellite.id,
                "satellite_name": scenario.target_satellite.name,
                "timestamp": scenario.timestamp.isoformat(),
            }
        ]
    )

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary_df.to_excel(writer, index=False, sheet_name="Scenario")
        terminals_df.to_excel(writer, index=False, sheet_name="Terminals")
    return output.getvalue()


def import_terminals_from_excel(content: bytes) -> list[UserTerminal]:
    workbook = pd.read_excel(BytesIO(content), sheet_name="Terminals")

    missing_cols = [column for column in TERMINAL_COLUMNS if column not in workbook.columns]
    if missing_cols:
        raise ValueError(f"Missing required terminal columns: {', '.join(missing_cols)}")

    terminals: list[UserTerminal] = []
    for record in workbook[TERMINAL_COLUMNS].to_dict(orient="records"):
        terminals.append(
            UserTerminal(
                id=int(record["id"]),
                profile_id=int(record["profile_id"]),
                lat=float(record["lat"]),
                long=float(record["long"]),
                is_obfuscated=bool(record["is_obfuscated"]),
                priority_level=int(record["priority_level"]),
                elevation_angle_deg=float(record["elevation_angle_deg"]),
                allocated_bandwidth_hz=float(record["allocated_bandwidth_hz"]),
                nominal_beam_diameter_km=float(record["nominal_beam_diameter_km"]),
            )
        )
    return terminals
