// Screenshots of the product page of one product of each kind (BookDetail, LaptopDetail, PhoneDetail, ApparelDetail):
// the same page shows the attributes of the subclass that the category's detail kind selects (table per subclass).
// The server must run on http://localhost:8080 (or BASE). Writes docs/evidence/e2e/kind_<kind>.png.
// usage: node shot_product_kinds.mjs
import { chromium } from "playwright";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const BASE = process.env.BASE || "http://localhost:8080";
const OUT = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "docs", "evidence", "e2e");
const browser = await chromium.launch({ channel: "msedge", headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 860 }, deviceScaleFactor: 1 });
const products = await (await fetch(`${BASE}/api/products`)).json();
let failed = 0;
for (const kind of ["BOOK", "LAPTOP", "PHONE", "APPAREL"]) {
  const p = products.find((x) => x.detailKind === kind && x.stockState !== "OUT");
  if (!p) { console.log("FAIL no product of kind", kind); failed += 1; continue; }
  await page.goto(`${BASE}/#/p/${p.id}`);
  await page.waitForLoadState("networkidle");
  await page.waitForSelector("#add");
  await page.waitForTimeout(300);
  const file = join(OUT, `kind_${kind.toLowerCase()}.png`);
  await page.screenshot({ path: file });
  console.log("PASS", kind, p.id, p.name, "->", file);
}
await browser.close();
process.exit(failed);
