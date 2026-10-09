"""T7 anonymous access reconnaissance; never opens a personal browser profile."""

import asyncio
import json
import os
from pathlib import Path

from pyppeteer import launch


HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("FOUNDRY_TRIAL_OUTPUT", HERE / "t7"))
STATE = HERE.parents[3] / ".local/portfolio-campaign/t7-browser"


async def main():
    OUT.mkdir(parents=True, exist_ok=False)
    STATE.mkdir(parents=True, exist_ok=False)
    browser = await launch(
        executablePath="/usr/bin/chromium", headless=True, userDataDir=str(STATE),
        args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-background-networking"],
    )
    observations = []
    try:
        for key, url in [
            ("liberty", "https://liberty-rider.com/fr/roadbooks"),
            ("68", "https://app68.studio/fr"),
            ("kurviger", "https://kurviger.com/en/plan"),
            ("myrouteapp", "https://www.myrouteapp.com/route/create"),
        ]:
            page = await browser.newPage()
            await page.setViewport({"width": 1440, "height": 960})
            record = {"key": key, "requested_url": url}
            try:
                response = await page.goto(url, {"waitUntil": "networkidle2", "timeout": 45000})
                record.update(url=page.url, status=response.status if response else None)
                record["body_excerpt"] = (await page.evaluate("document.body.innerText"))[:10000]
                record["controls"] = await page.evaluate("""() => Array.from(
                    document.querySelectorAll('input,button,[role=button],a')
                ).map(e => ({tag:e.tagName, text:e.innerText, title:e.title,
                    placeholder:e.placeholder, aria:e.getAttribute('aria-label'),
                    href:e.tagName==='A' ? e.href : undefined})).filter(e =>
                    e.text || e.placeholder || e.title || e.aria).slice(0,160)""")
                await page.screenshot({"path": str(OUT / f"{key}.png")})
            except Exception as error:
                record["error"] = f"{type(error).__name__}: {error}"
            observations.append(record)
            (OUT / "access.json").write_text(json.dumps(observations, indent=2) + "\n")
            print(json.dumps(record), flush=True)
            await page.close()
    finally:
        await browser.close()


asyncio.run(main())
