import unittest

from orbital_link.api import LinkBudgetRequest, run_link_budget, web_ui


class ApiUiTests(unittest.TestCase):
    def test_root_serves_web_ui(self) -> None:
        response = web_ui()

        self.assertIn("OrbitalLink Studio Web UI", response)
        self.assertIn("linkBudgetForm", response)

    def test_link_budget_endpoint_still_available(self) -> None:
        response = run_link_budget(
            LinkBudgetRequest(
                eirp_dbw=60.0,
                slant_range_km=1600.0,
                frequency_ghz=19.5,
                atmospheric_loss_db=2.0,
                g_over_t_db_k=15.0,
                allocated_bandwidth_hz=2_000_000.0,
                modcod_name="QPSK_1_2",
            )
        )

        self.assertIn("throughput_bps", response)
        self.assertIn("link_margin_db", response)


if __name__ == "__main__":
    unittest.main()
