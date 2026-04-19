"""FastAPI application for link simulation services."""

from dataclasses import asdict
from io import BytesIO

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from orbital_link.excel_io import export_scenario_to_excel, import_terminals_from_excel
from orbital_link.link_budget import LinkBudgetInput, calculate_link_budget
from orbital_link.models import Satellite, Scenario, UserTerminal


app = FastAPI(title="OrbitalLink Studio API", version="0.1.0")


class LinkBudgetRequest(BaseModel):
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


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/link-budget")
def run_link_budget(payload: LinkBudgetRequest) -> dict[str, float]:
    result = calculate_link_budget(LinkBudgetInput(**payload.model_dump()))
    return asdict(result)


@app.post("/scenarios/export")
def export_scenario(payload: dict) -> StreamingResponse:
    satellite_payload = payload["target_satellite"]
    terminals_payload = payload.get("terminals", [])

    scenario = Scenario(
        id=int(payload["id"]),
        name=payload["name"],
        target_satellite=Satellite(**satellite_payload),
        terminals=[UserTerminal(**terminal) for terminal in terminals_payload],
    )
    xlsx_data = export_scenario_to_excel(scenario)
    return StreamingResponse(
        BytesIO(xlsx_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="scenario.xlsx"'},
    )


@app.post("/scenarios/import")
async def import_scenario(file: UploadFile = File(...)) -> dict[str, object]:
    content = await file.read()
    terminals = import_terminals_from_excel(content)
    return {"terminal_count": len(terminals), "terminals": [asdict(terminal) for terminal in terminals]}
