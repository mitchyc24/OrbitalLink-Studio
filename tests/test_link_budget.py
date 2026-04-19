import unittest

from orbital_link.link_budget import LinkBudgetInput, calculate_link_budget, obfuscation_penalty_db


class LinkBudgetTests(unittest.TestCase):
    def test_obfuscation_penalty_applied(self) -> None:
        unobfuscated = calculate_link_budget(
            LinkBudgetInput(
                eirp_dbw=60.0,
                slant_range_km=1600.0,
                frequency_ghz=19.5,
                atmospheric_loss_db=2.0,
                g_over_t_db_k=15.0,
                allocated_bandwidth_hz=2_000_000.0,
                modcod_name="QPSK_1_2",
                is_obfuscated=False,
                nominal_beam_diameter_km=30.0,
            )
        )
        obfuscated = calculate_link_budget(
            LinkBudgetInput(
                eirp_dbw=60.0,
                slant_range_km=1600.0,
                frequency_ghz=19.5,
                atmospheric_loss_db=2.0,
                g_over_t_db_k=15.0,
                allocated_bandwidth_hz=2_000_000.0,
                modcod_name="QPSK_1_2",
                is_obfuscated=True,
                nominal_beam_diameter_km=30.0,
            )
        )

        self.assertGreater(obfuscated.obfuscation_penalty_db, 0.0)
        self.assertLess(obfuscated.c_over_n0_db_hz, unobfuscated.c_over_n0_db_hz)
        self.assertAlmostEqual(obfuscation_penalty_db(True, 30.0), 10.4575749056, places=6)

    def test_priority_scales_throughput(self) -> None:
        low_priority = calculate_link_budget(
            LinkBudgetInput(
                eirp_dbw=60.0,
                slant_range_km=1600.0,
                frequency_ghz=19.5,
                atmospheric_loss_db=2.0,
                g_over_t_db_k=15.0,
                allocated_bandwidth_hz=1_000_000.0,
                modcod_name="QPSK_1_2",
                priority_level=1,
            )
        )
        high_priority = calculate_link_budget(
            LinkBudgetInput(
                eirp_dbw=60.0,
                slant_range_km=1600.0,
                frequency_ghz=19.5,
                atmospheric_loss_db=2.0,
                g_over_t_db_k=15.0,
                allocated_bandwidth_hz=1_000_000.0,
                modcod_name="QPSK_1_2",
                priority_level=3,
            )
        )

        self.assertGreater(high_priority.throughput_bps, low_priority.throughput_bps)


if __name__ == "__main__":
    unittest.main()
