"""Probe preview transitions via Web Audio gain levels + playback time."""

from __future__ import annotations

import json
import sys

from playwright.sync_api import sync_playwright


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--autoplay-policy=no-user-gesture-required"],
        )
        page = browser.new_page()
        page.goto("http://127.0.0.1:8765/", wait_until="domcontentloaded")
        page.wait_for_function(
            """() => {
              const el = document.getElementById('coverIndex');
              return el && /\\d+\\/\\d+/.test(el.textContent || '') && !el.textContent.startsWith('0/');
            }""",
            timeout=60000,
        )

        page.evaluate(
            """() => {
              window.__fadeProbe = [];
              window.__samplePreview = () => {
                const probe = window.__previewProbe;
                if (!probe) {
                  const row = { t: performance.now(), effective: 0, ready: false };
                  window.__fadeProbe.push(row);
                  return row;
                }
                const gains = probe.gains();
                const players = probe.players();
                let effective = 0;
                const parts = [];
                for (let i = 0; i < players.length; i++) {
                  const p = players[i];
                  const g = gains[i] || 0;
                  const live = !p.paused && !p.ended && p.rs >= 2;
                  // Treat as audible contribution only when clock is advancing past decoder priming.
                  const contrib = live && p.t > 0.05 ? g : live ? g * 0.15 : 0;
                  effective += contrib;
                  parts.push({ g: Number(g.toFixed(3)), t: Number(p.t.toFixed(3)), live, src: p.src.slice(0, 40) });
                }
                const row = {
                  t: performance.now(),
                  effective: Number(effective.toFixed(3)),
                  ready: true,
                  active: probe.active(),
                  parts,
                };
                window.__fadeProbe.push(row);
                return row;
              };
            }"""
        )

        page.evaluate("setSelectedIndex(0)")
        page.wait_for_function("() => window.__previewProbe", timeout=10000)
        page.wait_for_timeout(3500)

        for i in range(1, 5):
            page.evaluate(
                "window.__fadeProbe.push({ mark: 'before-switch', i: %d, t: performance.now() })" % i
            )
            for _ in range(6):
                page.evaluate("window.__samplePreview()")
                page.wait_for_timeout(40)
            page.evaluate("setSelectedIndex(%d)" % i)
            for _ in range(70):
                page.evaluate("window.__samplePreview()")
                page.wait_for_timeout(25)
            page.wait_for_timeout(900)

        probe = page.evaluate("window.__fadeProbe")
        browser.close()

    marks = [i for i, row in enumerate(probe) if isinstance(row, dict) and row.get("mark") == "before-switch"]
    report = []
    for mi, start in enumerate(marks):
        end = marks[mi + 1] if mi + 1 < len(marks) else len(probe)
        window = [r for r in probe[start:end] if isinstance(r, dict) and "effective" in r]
        if len(window) < 10:
            continue
        baseline = [r for r in window[:6] if r.get("ready")]
        after = [r for r in window[6:55] if r.get("ready")]
        if not after:
            continue
        base_avg = sum(r["effective"] for r in baseline) / len(baseline) if baseline else 1
        min_e = min(r["effective"] for r in after)
        threshold = max(0.2, base_avg * 0.35)
        dips = [r for r in after if r["effective"] < threshold]
        report.append(
            {
                "switch": mi + 1,
                "baseline": round(base_avg, 3),
                "min_effective": min_e,
                "threshold": round(threshold, 3),
                "dip_samples": len(dips),
                "worst": min(after, key=lambda r: r["effective"]),
            }
        )

    print(json.dumps({"switches": report}, indent=2))
    bad = [r for r in report if r["min_effective"] < r["threshold"] and r["dip_samples"] >= 3]
    if not report:
        print("RESULT: NO DATA", file=sys.stderr)
        return 2
    if bad:
        print("RESULT: CUT DETECTED", file=sys.stderr)
        return 1
    print("RESULT: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
