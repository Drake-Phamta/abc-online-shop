// Screenshots of showcase/index.html in Edge (desktop and phone width) for a visual check.
// usage: node shot_showcase.mjs <out dir>
import { chromium } from "playwright";
import { join, dirname } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const out = process.argv[2] || ".";
const page = pathToFileURL(join(dirname(fileURLToPath(import.meta.url)), "..", "..", "showcase", "index.html")).href;
const browser = await chromium.launch({ channel: "msedge", headless: true });
for (const [name, width, height] of [["desktop", 1440, 900], ["phone", 390, 844]]) {
  const p = await browser.newPage({ viewport: { width, height } });
  const errors = [];
  p.on("pageerror", (e) => errors.push(e.message));
  p.on("requestfailed", (r) => errors.push("failed " + r.url()));
  await p.goto(page);
  await p.waitForLoadState("networkidle");
  await p.evaluate(() => document.querySelectorAll("img[loading=lazy]").forEach((i) => { i.loading = "eager"; }));
  await p.waitForTimeout(800);
  await p.screenshot({ path: join(out, `showcase_${name}.png`), fullPage: true });
  const overflow = await p.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  console.log(name, "horizontal overflow:", overflow, "errors:", errors.length ? errors.join(" | ") : "none");
  await p.close();
}
await browser.close();
