// View class StockForm (UC15 Manage Inventory). Controller: ProductController, /api/staff/stock.
import { api } from "../api.js";
import { html, mount, vnd, stockBadge, loading, failure, toast } from "../ui.js";

export class StockForm {
  constructor(app) {
    this.app = app;
    this.controller = "/api/staff/stock";
  }

  async showStock() {
    const nav = this.app.nav;
    mount(this.app.view, loading());
    let rows;
    try { rows = await api("GET", this.controller); } catch (err) { return this.app.current(nav) && mount(this.app.view, failure(err)); }
    if (!this.app.current(nav)) return;   // a newer navigation owns the page
    const low = rows.filter((r) => r.stockState !== "IN").length;
    mount(this.app.view, html`
      <div class="page-head"><div><p class="eyebrow">Warehouse staff · UC15</p><h1 class="two-tone">Inventory. <span class="muted">${low} product${low === 1 ? "" : "s"} low or out of stock.</span></h1></div></div>
      <table class="orders-table" data-trace="StockForm.showStock ← GET /api/staff/stock · ProductController.stock · CatalogService.stockList · ProductDAO.listForStock · product">
        <thead><tr><th></th><th>Product</th><th>Category</th><th>State</th><th style="text-align:right">Stock</th><th></th></tr></thead>
        <tbody>${rows.map((r) => html`<tr class="${r.stockState === "OUT" ? "out" : r.stockState === "LOW" ? "low" : ""}">
          <td style="width:56px">${r.image ? html`<img src="${r.image}" alt="" style="width:44px;height:44px;object-fit:contain;mix-blend-mode:multiply">` : ""}</td>
          <td><b>${r.name}</b><br><span class="code small">${r.sku}</span></td>
          <td>${r.category}</td><td>${stockBadge(r.stockState, r.stock)}</td>
          <td style="text-align:right"><input class="stock-input" type="number" min="0" value="${r.stock}" data-id="${r.id}" aria-label="Stock of ${r.name}"></td>
          <td><button class="btn small ghost" data-save="${r.id}" data-trace="StockForm.submitStock → PUT /api/staff/stock/{id} · ProductController.updateStock · CatalogService.updateStock · Product.updateStock (BR12) · ProductDAO.updateStock">Save</button></td>
        </tr>`)}</tbody>
      </table>`);
    this.app.view.querySelectorAll("[data-save]").forEach((b) => b.addEventListener("click", () => {
      const input = this.app.view.querySelector(`.stock-input[data-id="${b.dataset.save}"]`);
      this.submitStock(Number(b.dataset.save), input.value === "" ? null : Number(input.value));
    }));
  }

  async submitStock(productId, quantity) {
    try {
      const row = await api("PUT", `${this.controller}/${productId}`, { quantity });
      toast(`${row.name}: stock set to ${row.stock}`);
      this.showStock();
    } catch (err) {
      toast(err.message, "error");
    }
  }
}
