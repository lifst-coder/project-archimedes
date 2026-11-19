#!/usr/bin/env python3
"""Unit tests for the ARCHIMEDES prototype. Run: python prototype/test_prototype.py"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import archimedes_prototype as ap  # noqa: E402


class DataTests(unittest.TestCase):
    def test_shape_and_determinism(self):
        a, truth = ap.generate_synthetic_growth_data(seed=7)
        b, _ = ap.generate_synthetic_growth_data(seed=7)
        self.assertEqual(len(a), 5 * 4 * 48)
        self.assertEqual(len(truth), 20)
        self.assertEqual(ap.data_hash(a), ap.data_hash(b))

    def test_different_seed_changes_data(self):
        a, _ = ap.generate_synthetic_growth_data(seed=1)
        b, _ = ap.generate_synthetic_growth_data(seed=2)
        self.assertNotEqual(ap.data_hash(a), ap.data_hash(b))

    def test_od_is_positive(self):
        curves, _ = ap.generate_synthetic_growth_data()
        self.assertGreater(curves["od600"].min(), 0)


class AnalystTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.curves, cls.truth = ap.generate_synthetic_growth_data()
        cls.fits = ap.Analyst().fit_curves(cls.curves)

    def test_fit_recovers_planted_parameters(self):
        merged = self.fits.merge(self.truth, on=["condition", "replicate"], suffixes=("_fit", "_true"))
        merged = merged[merged["plateau"]]
        for param, tol in (("K", 0.05), ("r", 0.15)):
            rel = ((merged[f"{param}_fit"] - merged[f"{param}_true"]).abs() / merged[f"{param}_true"]).median()
            self.assertLess(rel, tol, param)

    def test_fits_are_good(self):
        self.assertGreater(self.fits["r2"].median(), 0.98)

    def test_holm_matches_hand_calculation(self):
        for got, want in zip(ap.holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06]):
            self.assertAlmostEqual(got, want)

    def test_holm_is_capped_and_monotone(self):
        adjusted = ap.holm([0.5, 0.9, 0.2])
        self.assertTrue(all(p <= 1 for p in adjusted))
        for got, want in zip(adjusted, [1.0, 1.0, 0.6]):
            self.assertAlmostEqual(got, want)


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = ap.Orchestrator().run()
        cls.by_id = {h["id"]: h for h in cls.result["hypotheses"]}

    def test_planted_effects_are_supported(self):
        for hid in ("H1", "H2", "H4"):
            self.assertEqual(self.by_id[hid]["verdict"], "supported", hid)

    def test_unfinished_curves_block_a_verdict(self):
        h3 = self.by_id["H3"]
        self.assertEqual(h3["verdict"], "inconclusive")
        self.assertIn("plateau", " ".join(h3["objections"]))

    def test_longer_denser_run_resolves_the_lag_hypothesis(self):
        result = ap.Orchestrator(hours=48, n_timepoints=96).run()
        h3 = next(h for h in result["hypotheses"] if h["id"] == "H3")
        self.assertEqual(h3["verdict"], "supported")

    def test_negative_control_is_refuted(self):
        self.assertEqual(self.by_id["H5"]["verdict"], "refuted")

    def test_critic_always_flags_synthetic_and_small_n(self):
        for h in self.result["hypotheses"]:
            text = " ".join(h["objections"])
            self.assertIn("synthetic", text)
            self.assertIn("replicates", text)

    def test_result_is_json_serialisable_and_reproducible(self):
        again = ap.Orchestrator().run()
        self.assertEqual(json.dumps(self.result, sort_keys=True), json.dumps(again, sort_keys=True))

    def test_committed_result_matches_a_fresh_run(self):
        committed = Path(__file__).with_name("run_result.json")
        self.assertEqual(json.loads(committed.read_text(encoding="utf-8")), self.result)

    def test_poor_fits_make_the_verdict_inconclusive(self):
        fits = ap.Analyst().fit_curves(ap.generate_synthetic_growth_data()[0])
        fits["r2"] = 0.5
        hyps = ap.HypothesisGenerator().generate(ap.KnowledgeAgent())
        verdicts = ap.Critic().review(hyps, ap.Analyst().test(hyps, fits), fits)
        self.assertTrue(all(v.verdict == "inconclusive" for v in verdicts))


if __name__ == "__main__":
    unittest.main(verbosity=2)
