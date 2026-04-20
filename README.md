# OrbitalLink-Studio

Minimal backend implementation of a LEO (~1400 km) satellite communication link simulator with:

- DVB-S2X MODCOD lookup and link budget math (`C/N0`, `Es/N0`, margin, throughput)
- Position obfuscation penalty using a forced 100 km privacy beam
- Terminal priority-based bandwidth weighting
- Scenario and terminal domain models aligned with the requested schema
- FastAPI endpoints for link analysis and Excel scenario import/export
- Excel round-trip support for terminal bulk updates
- Built-in Web UI for link budget analysis and scenario import/export

## Run locally

```bash
pip install -e .
uvicorn orbital_link.api:app --reload
```

Then open http://127.0.0.1:8000/ in your browser.

## Run tests

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
