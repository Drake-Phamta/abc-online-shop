// End-to-end run of the implemented use cases in the installed Microsoft Edge (Playwright, channel "msedge").
// The server must run on http://localhost:8080 with a fresh database (java -jar target/abc-online-shop-1.0.0.jar --abc.db.reset=true).
// Every step is checked on the page and, where a use case changes data, through the API; a screenshot of each step
// goes to docs/evidence/e2e/. Exit code = number of failed checks.
import { chromium } from "playwright";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const BASE = process.env.BASE || "http://localhost:8080";
const OUT = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "docs", "evidence", "e2e");
mkdirSync(OUT, { recursive: true });

const results = [];
let shot = 0;
function check(name, ok, detail = "") {
  results.push({ name, ok: !!ok, detail });
  console.log(`${ok ? "PASS" : "FAIL"} ${name}${detail ? "  (" + detail + ")" : ""}`);
}

const browser = await chromium.launch({ channel: "msedge", headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
const page = await context.newPage();
const consoleErrors = [];
// the browser logs every refused request (e.g. 409 for BR12) as "Failed to load resource"; those are expected answers
page.on("console", (m) => { if (m.type() === "error" && !m.text().startsWith("Failed to load resource")) consoleErrors.push(m.text()); });
page.on("pageerror", (e) => consoleErrors.push(e.message));

async function snap(name, fullPage = false, keepToast = false) {
  shot += 1;
  if (!keepToast) await clearToast();   // a toast left from an earlier step would hide part of the page
  const file = `${String(shot).padStart(2, "0")}_${name}.png`;
  await page.waitForTimeout(250);   // let the toast and transitions settle
  await page.screenshot({ path: join(OUT, file), fullPage });
  return file;
}
async function go(hash, ready) {
  // first visit loads the page; later moves change the hash like the app's own links (same document)
  if (!page.url().startsWith(BASE)) await page.goto(`${BASE}/#/${hash}`);
  else await page.evaluate((h) => { location.hash = "#/" + h; }, hash);
  await page.waitForLoadState("networkidle");
  if (ready) await page.waitForSelector(ready);   // views render after their fetch, wait for the content
}
async function clearToast() {
  await page.evaluate(() => document.querySelectorAll(".toast").forEach((t) => t.remove()));
}
async function apiGet(path) {
  return page.evaluate(async (p) => { const r = await fetch(p, { credentials: "same-origin" }); return { status: r.status, body: await r.json().catch(() => null) }; }, path);
}
async function login(email) {
  await go("login", "#email");
  await page.fill("#email", email);
  await page.fill("#password", "demo1234");
  await page.click("#login-form button[type=submit]");
  await page.waitForFunction(() => !location.hash.startsWith("#/login"));
  await page.waitForLoadState("networkidle");
}
async function logout() {
  await clearToast();
  await page.click("#logout");
  await page.waitForSelector("#account a[href='#/login']");
  await page.waitForFunction(() => location.hash === "#/" || location.hash === "");   // the app goes home after logout
  await page.waitForSelector("#view a.dept");   // home rendered: no late render can replace the next page
  await page.waitForLoadState("networkidle");
}
async function toastText() {
  const t = page.locator(".toast");
  await t.waitFor({ state: "visible", timeout: 5000 }).catch(() => {});
  return (await t.textContent().catch(() => "")) || "";
}

try {
  // UC04 browse and search as a guest
  await go("");
  check("UC04 home page lists departments and products", await page.locator("a.card").count() > 0);
  await snap("home");
  await go("c/all", "a.card");
  const all = await page.locator("a.card").count();
  check("UC04 catalogue shows products", all > 0, `${all} cards`);
  await snap("catalogue");
  await page.fill("#search input[name=q]", "laptop");
  await Promise.all([
    page.waitForResponse((r) => r.url().includes("/api/search") && r.url().includes("q=laptop")),
    page.press("#search input[name=q]", "Enter"),
  ]);
  await page.waitForSelector("a.card.found");
  const hits = await page.locator("a.card").count();
  check("UC04 search 'laptop' returns matches", hits > 0, `${hits} results`);
  await snap("search_laptop");

  // UC05 product details with the detail table of its category (a product that can be bought: no "Out of stock" badge)
  await page.locator("a.card:not(:has(.badge.danger))").first().click();
  await page.waitForSelector("#add");
  const productId = Number((await page.evaluate(() => location.hash)).split("/")[2]);
  check("UC05 product page opens with Add to cart", productId > 0, `product ${productId}`);
  await snap("product");

  // BR08: a guest who adds to the cart is sent to the login page
  await page.click("#add");
  await page.waitForFunction(() => location.hash.startsWith("#/login"));
  check("BR08 guest is asked to log in before using the cart", true);
  await snap("login_required");

  // UC02 login
  await page.fill("#email", "an.nguyen@example.com");
  await page.fill("#password", "demo1234");
  await page.click("#login-form button[type=submit]");
  await page.waitForFunction(() => !location.hash.startsWith("#/login"));
  await page.waitForLoadState("networkidle");
  const me = await apiGet("/api/auth/me");
  check("UC02 customer logged in", me.body?.loggedIn && me.body.role === "CUSTOMER", me.body?.name);

  // UC06 add to cart (quantity 2)
  await go(`p/${productId}`, "#add");
  await page.fill("#qty", "2");
  await clearToast();
  await page.click("#add");
  const added = await toastText();
  const cart1 = await apiGet("/api/cart");
  const line = cart1.body?.lines?.find((l) => l.productId === productId);
  check("UC06 product added to the cart in the database", line && line.quantity >= 2, added.trim());
  await snap("added_to_cart", false, true);

  await go("cart", "[data-remove]");
  check("UC06 cart page shows the line", await page.locator("[data-remove]").count() > 0);
  await page.locator("button[data-step='1']").first().click();
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(400);
  const cart2 = await apiGet("/api/cart");
  const line2 = cart2.body?.lines?.find((l) => l.productId === productId);
  check("UC06 quantity changed and saved", line2 && line2.quantity === line.quantity + 1, `${line.quantity} -> ${line2?.quantity}`);
  await snap("cart");

  // UC07 checkout (UC21 validates the cart) and place the order, card payment
  await go("checkout", "#place");
  check("UC07/UC21 checkout page with totals, no blocking issue", await page.locator("#place").isEnabled());
  await snap("checkout");
  await page.check("input[name=method][value=CARD]");
  await page.click("#place");
  await page.waitForFunction(() => location.hash.startsWith("#/pay/"));
  await page.waitForSelector("#pay");
  const orderId = Number((await page.evaluate(() => location.hash)).split("/")[2]);
  const placed = await apiGet(`/api/orders/${orderId}`);
  check("UC07 order placed and waiting for the card payment", placed.body?.status === "PENDING_PAYMENT", placed.body?.code);
  const cartAfter = await apiGet("/api/cart");
  check("UC07 cart emptied after the order", (cartAfter.body?.lines || []).length === 0);
  await snap("payment_form");

  // UC08 make payment: declined card first (A1), then an approved one
  async function pay(number) {
    await clearToast();
    await page.fill("#holder", "NGUYEN VAN AN");
    await page.fill("#number", number);
    await page.fill("#expiry", "08/28");
    await page.fill("#cvv", "123");
    await page.click("#pay button[type=submit]");
    await page.waitForLoadState("networkidle");
  }
  await pay("4000 0000 0000 0002");
  const declined = await toastText();
  await page.waitForSelector("#pay");
  const afterDecline = await apiGet(`/api/orders/${orderId}`);
  check("UC08 A1 declined card keeps the order waiting", afterDecline.body?.status === "PENDING_PAYMENT", declined.trim());
  await snap("payment_declined", false, true);
  await pay("4242 4242 4242 4242");
  await page.waitForFunction(() => location.hash.startsWith("#/orders/"));
  await page.waitForLoadState("networkidle");
  const paid = await apiGet(`/api/orders/${orderId}`);
  check("UC08 approved card marks the order PAID (BR07)", paid.body?.status === "PAID");
  await snap("order_paid");

  // UC09 track order: list and details
  await go("orders", `tr[data-id='${orderId}']`);
  check("UC09 my orders lists the new order", (await page.content()).includes(placed.body?.code || "#"));
  await snap("my_orders");
  await logout();

  // UC14 process orders as sales staff: process, ship, deliver
  await login("sales@example.com");
  await go("staff/orders", `[data-act=process][data-id='${orderId}']`);
  await snap("order_board");
  await clearToast();
  await page.click(`[data-act=process][data-id='${orderId}']`);
  await page.waitForSelector(`[data-act=ship][data-id='${orderId}']`);
  check("UC14 order moves to PROCESSING", (await apiGet(`/api/orders/${orderId}`)).body?.status === "PROCESSING");
  await page.click(`[data-act=ship][data-id='${orderId}']`);
  await page.waitForSelector("dialog[open] select[name=carrier]");
  await page.fill("dialog[open] input[name=tracking]", "GHN-E2E-0001");
  await snap("ship_dialog");
  await page.click("dialog[open] button[value=ok]");
  await page.waitForSelector(`[data-act=deliver][data-id='${orderId}']`);
  check("UC14 order SHIPPED with tracking (BR10)", (await apiGet(`/api/orders/${orderId}`)).body?.status === "SHIPPED");
  await clearToast();
  await page.click(`[data-act=deliver][data-id='${orderId}']`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(400);
  check("UC14 order DELIVERED", (await apiGet(`/api/orders/${orderId}`)).body?.status === "DELIVERED");
  await snap("board_after_delivery");
  await logout();

  // UC09 the customer sees the timeline and the tracking number
  await login("an.nguyen@example.com");
  await go(`orders/${orderId}`, "#view");
  await page.waitForFunction(() => document.getElementById("view").textContent.includes("GHN-E2E-0001"), null, { timeout: 8000 }).catch(() => {});
  const detail = await page.content();
  check("UC09 tracking shows the carrier's tracking number", detail.includes("GHN-E2E-0001"));
  await snap("order_tracking", true);

  // Trace lens (Alt+L): every screen names its view class, controller and DAO
  await go("cart", "#view");
  await page.keyboard.press("Alt+L");
  await page.waitForTimeout(300);
  check("Trace lens switches on", await page.evaluate(() => document.body.classList.contains("lens")));
  await go(`orders/${orderId}`, "#view [data-trace]");
  await snap("trace_lens");
  await page.keyboard.press("Alt+L");
  await logout();

  // UC15 manage inventory as warehouse staff; BR12 refuses a negative stock
  await login("warehouse@example.com");
  await go("staff/stock", ".stock-input");
  const sid = await page.locator(".stock-input").first().getAttribute("data-id");
  const input = () => page.locator(`.stock-input[data-id='${sid}']`);   // the list is re-sorted after a save
  await input().fill("37");
  await clearToast();
  await page.click(`[data-save='${sid}']`);
  await toastText();
  const stock = await apiGet("/api/staff/stock");
  const row = stock.body?.find((r) => String(r.id) === sid);
  check("UC15 stock saved in the database", row && row.stock === 37, `product ${sid}`);
  await snap("stock");
  await page.waitForFunction((id) => document.querySelector(`.stock-input[data-id="${id}"]`)?.value === "37", sid);
  await input().fill("-5");
  await clearToast();
  await page.click(`[data-save='${sid}']`);
  const refused = await toastText();
  check("BR12 the refusal is shown to the user", /negative|BR12|at least|0/i.test(refused) && !refused.includes("stock set to"), refused.trim());
  const row2 = (await apiGet("/api/staff/stock")).body?.find((r) => String(r.id) === sid);
  check("BR12 negative stock refused, value unchanged", row2 && row2.stock === 37, refused.trim());
  await snap("stock_refused", false, true);
  await logout();

  // BR13: a customer cannot open staff pages
  await login("an.nguyen@example.com");
  await go("staff/orders", "#view .empty");
  check("BR13 customer cannot open the order board", (await page.content()).includes("cannot open this page"));

  // AI search (docs/SPEC.md section 6), at the end so that the earlier screenshot numbers stay the same
  const firstName = () => page.locator("a.card.found .name").first().textContent();
  await page.fill("#search input[name=q]", "red sneakers under 3 million");
  await page.press("#search input[name=q]", "Enter");
  await page.waitForFunction(() => document.querySelector("h1")?.textContent.includes("red sneakers"));
  await page.waitForSelector("a.card.found");
  const understood = await page.locator(".understood").textContent();
  check("AT11 AI search: red sneakers under 3 million finds the red Converse first", /Converse/.test(await firstName()), (await firstName()).trim());
  check("AI02/AI03 the page shows how the query was understood", understood.includes("sneaker → shoe") && understood.includes("at most 3.000.000"), understood.replace(/\s+/g, " ").trim());
  await snap("search_ai_text");
  await go("search?q=macbok%20air", "a.card.found");
  check("AT12 spelling corrected: macbok → macbook", (await page.locator(".chip.fix").textContent()).includes("macbok → macbook") && /MacBook/.test(await firstName()));
  await page.setInputFiles("#photo", join(dirname(fileURLToPath(import.meta.url)), "..", "search", "photos", "FA-SHO-002_background.jpg"));
  await page.waitForSelector(".photo-query");
  await page.waitForSelector("a.card.found");
  check("AT15 photo search: a photo of the Nike Air Max 90 finds it first", /Nike Air Max 90/.test(await firstName()), (await firstName()).trim());
  await snap("search_photo");
  await page.click("#voice");
  await page.waitForSelector(".voice-card");
  await page.fill("#voice-text", "blue jeans");
  await snap("search_voice_dialog");
  await page.click("#voice-go");
  await page.waitForFunction(() => document.querySelector("h1")?.textContent.includes("blue jeans"));
  await page.waitForSelector("a.card.found");
  check("FR-S4 voice dialog: the (corrected) text is searched", /Levi's 501/.test(await firstName()), (await firstName()).trim());
} catch (e) {
  const at = (e.stack || "").split("\n").find((l) => l.includes("run_e2e.mjs")) || "";
  check("run finished without an exception", false, `${e.message.split("\n")[0]} at ${at.trim()} on ${page.url()}`);
  await snap("failure").catch(() => {});
}

check("no JavaScript errors in the console", consoleErrors.length === 0, consoleErrors.slice(0, 3).join(" | "));
await browser.close();
const failed = results.filter((r) => !r.ok).length;
const lines = results.map((r) => `${r.ok ? "PASS" : "FAIL"} ${r.name}${r.detail ? "  (" + r.detail + ")" : ""}`);
writeFileSync(join(OUT, "e2e_result.txt"), `E2E run ${new Date().toISOString()} on ${BASE}, Microsoft Edge (Playwright)\n${lines.join("\n")}\n${results.length - failed}/${results.length} checks passed\n`);
console.log(`${results.length - failed}/${results.length} checks passed`);
process.exit(failed);
