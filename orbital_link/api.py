"""FastAPI application for link simulation services."""

from dataclasses import asdict
from io import BytesIO

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from orbital_link.excel_io import export_scenario_to_excel, import_terminals_from_excel
from orbital_link.link_budget import LinkBudgetInput, calculate_link_budget
from orbital_link.modcod import MODCOD_TABLE
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


def _web_ui_html() -> str:
    modcod_options = "".join(
        f'<option value="{modcod.name}">{modcod.name}</option>' for modcod in MODCOD_TABLE
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>OrbitalLink Studio</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; }}
    section {{ border: 1px solid #ddd; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }}
    form {{ display: grid; gap: 0.75rem; }}
    label {{ display: grid; gap: 0.25rem; font-size: 0.95rem; }}
    button {{ width: fit-content; padding: 0.5rem 0.8rem; }}
    pre {{ background: #f7f7f7; padding: 0.75rem; border-radius: 6px; overflow: auto; }}
    textarea {{ min-height: 140px; width: 100%; }}
  </style>
</head>
<body>
  <h1>OrbitalLink Studio Web UI</h1>
  <section>
    <h2>Link Budget Calculator</h2>
    <form id="linkBudgetForm">
      <label>EIRP (dBW)<input type="number" step="any" name="eirp_dbw" value="60" required /></label>
      <label>Slant Range (km)<input type="number" step="any" name="slant_range_km" value="1600" required /></label>
      <label>Frequency (GHz)<input type="number" step="any" name="frequency_ghz" value="19.5" required /></label>
      <label>Atmospheric Loss (dB)<input type="number" step="any" name="atmospheric_loss_db" value="2" required /></label>
      <label>G/T (dB/K)<input type="number" step="any" name="g_over_t_db_k" value="15" required /></label>
      <label>Allocated Bandwidth (Hz)<input type="number" step="any" name="allocated_bandwidth_hz" value="2000000" required /></label>
      <label>MODCOD
        <select name="modcod_name">{modcod_options}</select>
      </label>
      <label>Priority Level<input type="number" min="1" max="10" name="priority_level" value="1" required /></label>
      <label><input type="checkbox" name="is_obfuscated" /> Obfuscated</label>
      <label>Nominal Beam Diameter (km)<input type="number" step="any" name="nominal_beam_diameter_km" value="30" required /></label>
      <button type="submit">Run Link Budget</button>
    </form>
    <pre id="linkBudgetResult"></pre>
  </section>
  <section>
    <h2>Scenario Export</h2>
    <form id="exportForm">
      <label>Scenario JSON
        <textarea id="scenarioJson">{{"id":1,"name":"demo","target_satellite":{{"id":1,"name":"LEO-A"}},"terminals":[]}}</textarea>
      </label>
      <button type="submit">Download Excel</button>
    </form>
  </section>
  <section>
    <h2>Scenario Import</h2>
    <form id="importForm">
      <label>Excel file<input type="file" id="scenarioFile" accept=".xlsx" required /></label>
      <button type="submit">Import Scenario</button>
    </form>
    <pre id="importResult"></pre>
  </section>
  <script>
    const asPayload = (form) => {{
      const data = new FormData(form);
      return {{
        eirp_dbw: Number(data.get("eirp_dbw")),
        slant_range_km: Number(data.get("slant_range_km")),
        frequency_ghz: Number(data.get("frequency_ghz")),
        atmospheric_loss_db: Number(data.get("atmospheric_loss_db")),
        g_over_t_db_k: Number(data.get("g_over_t_db_k")),
        allocated_bandwidth_hz: Number(data.get("allocated_bandwidth_hz")),
        modcod_name: String(data.get("modcod_name")),
        priority_level: Number(data.get("priority_level")),
        is_obfuscated: data.get("is_obfuscated") === "on",
        nominal_beam_diameter_km: Number(data.get("nominal_beam_diameter_km")),
      }};
    }};

    document.getElementById("linkBudgetForm").addEventListener("submit", async (event) => {{
      event.preventDefault();
      const resultNode = document.getElementById("linkBudgetResult");
      resultNode.textContent = "Running...";
      const response = await fetch("/link-budget", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify(asPayload(event.target)),
      }});
      const payload = await response.json();
      resultNode.textContent = JSON.stringify(payload, null, 2);
    }});

    document.getElementById("exportForm").addEventListener("submit", async (event) => {{
      event.preventDefault();
      const source = document.getElementById("scenarioJson").value;
      const response = await fetch("/scenarios/export", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: source,
      }});
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "scenario.xlsx";
      link.click();
      URL.revokeObjectURL(url);
    }});

    document.getElementById("importForm").addEventListener("submit", async (event) => {{
      event.preventDefault();
      const fileInput = document.getElementById("scenarioFile");
      const file = fileInput.files[0];
      if (!file) return;
      const body = new FormData();
      body.append("file", file);
      const response = await fetch("/scenarios/import", {{ method: "POST", body }});
      const payload = await response.json();
      document.getElementById("importResult").textContent = JSON.stringify(payload, null, 2);
    }});
  </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def web_ui() -> str:
    return _web_ui_html()


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
