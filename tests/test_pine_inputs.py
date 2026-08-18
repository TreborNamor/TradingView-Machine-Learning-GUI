from __future__ import annotations

import unittest
import sys
import types

sys.modules.setdefault("talib", types.ModuleType("talib"))

from hyperview.pine.inputs import extract_pine_inputs, resolve_search_dimensions

_PINE = """
htfTf = input.timeframe("60", "HTF")
entryMode = input.string("both", "Entry Mode", options=["retest_ob", "aggressive", "both"])
sweepLookback = input.int(6, "HTF Sweep Lookback", minval=2)
slBufferAtr = input.float(0.25, "SL Buffer ATR", minval=0.0, step=0.05)
sessionFilter = input.bool(true, "Session Filter")
sessionA = input.session("0700-1700", "Session A")
longSignal = entryMode == "both" and sessionFilter and sweepLookback > 0
plotshape(longSignal)
"""

class PineInputParserTests(unittest.TestCase):
    def test_extract_and_map_expected_inputs(self) -> None:
        specs = extract_pine_inputs(_PINE)
        by_name = {spec.name: spec for spec in specs}
        self.assertIn("entryMode", by_name)
        self.assertIn("sweepLookback", by_name)
        self.assertIn("sessionA", by_name)
        self.assertEqual(by_name["entryMode"].options, ["retest_ob", "aggressive", "both"])
        self.assertEqual(by_name["sweepLookback"].minval, 2)
        self.assertEqual(by_name["slBufferAtr"].step, 0.05)

    def test_resolve_search_dimensions(self) -> None:
        specs = extract_pine_inputs(_PINE)
        dims, warnings = resolve_search_dimensions(specs)
        names = {dim.name for dim in dims}
        self.assertIn("entryMode", names)
        self.assertIn("sweepLookback", names)
        self.assertNotIn("sessionA", names)
        self.assertTrue(any("htfTf" in warning for warning in warnings))
        self.assertTrue(any("sessionA" in warning for warning in warnings))

if __name__ == "__main__":
    unittest.main()
