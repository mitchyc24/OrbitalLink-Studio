import unittest

from orbital_link.excel_io import export_scenario_to_excel, import_terminals_from_excel
from orbital_link.models import Satellite, Scenario, UserTerminal


class ExcelRoundTripTests(unittest.TestCase):
    def test_export_then_import_preserves_terminal_rows(self) -> None:
        scenario = Scenario(
            id=1,
            name="roundtrip",
            target_satellite=Satellite(id=1, name="LEO-A"),
            terminals=[
                UserTerminal(
                    id=10,
                    profile_id=101,
                    lat=34.001,
                    long=-118.22,
                    is_obfuscated=True,
                    priority_level=3,
                    elevation_angle_deg=45.0,
                    allocated_bandwidth_hz=2_500_000.0,
                    nominal_beam_diameter_km=30.0,
                ),
                UserTerminal(
                    id=11,
                    profile_id=102,
                    lat=40.7128,
                    long=-74.006,
                    is_obfuscated=False,
                    priority_level=1,
                    elevation_angle_deg=35.0,
                    allocated_bandwidth_hz=1_000_000.0,
                    nominal_beam_diameter_km=20.0,
                ),
            ],
        )
        xlsx_content = export_scenario_to_excel(scenario)
        terminals = import_terminals_from_excel(xlsx_content)

        self.assertEqual(len(terminals), 2)
        self.assertEqual(terminals[0].id, 10)
        self.assertTrue(terminals[0].is_obfuscated)
        self.assertEqual(terminals[1].priority_level, 1)


if __name__ == "__main__":
    unittest.main()
