// View class StaffOrderForm (UC14 Process Orders). Controllers: OrderController and ShippingController, /api/staff/orders.
import { api } from "../api.js";
import { html, mount, vnd, when, statusBadge, loading, failure, toast } from "../ui.js";
import { orderBody } from "./OrderForm.js";

const COLUMNS = [
  ["To process", ["PLACED", "PAID"]],
  ["Processing", ["PROCESSING"]],
  ["On the way", ["SHIPPED"]],
  ["Closed", ["DELIVERED", "CANCELLED", "PENDING_PAYMENT"]],
];
const CARRIERS = ["GHN", "Viettel Post", "GHTK", "J&T Express"];

export class StaffOrderForm {
  constructor(app) {
    this.app = app;
    this.controller = "/api/staff/orders";
  }

  async showBoard() {
    const nav = this.app.nav;
    mount(this.app.view, loading());
    let orders;
    try { orders = await api("GET", this.controller); } catch (err) { return this.app.current(nav) && mount(this.app.view, failure(err)); }
    if (!this.app.current(nav)) return;   // a newer navigation owns the page
    mount(this.app.view, html`
      <div class="page-head"><div><p class="eyebrow">Sales staff · UC14</p><h1 class="two-tone">Order board. <span class="muted">Move each order along its lifecycle.</span></h1></div></div>
      <div class="board" data-trace="StaffOrderForm.showBoard ← GET /api/staff/orders · OrderController.board · OrderService.allOrders · OrderDAO.findAll · customer_order ⋈ customer">
        ${COLUMNS.map(([title, statuses]) => {
          const list = orders.filter((o) => statuses.includes(o.status));
          return html`<div class="column"><h4>${title}<span>${list.length}</span></h4>
            ${list.map((o) => html`<div class="ticket">
              <div class="row"><a class="code" href="#/staff/orders/${o.id}">${o.code}</a>${statusBadge(o.status)}</div>
              <div style="margin:8px 0 2px"><b>${o.customerName}</b></div>
              <div class="small">${o.firstItem}${o.itemCount > 1 ? ` + ${o.itemCount - 1} more` : ""}</div>
              <div class="row" style="margin-top:6px"><span class="small">${when(o.orderDate)} · ${o.paymentMethod === "COD" ? "cash on delivery" : "card"}</span><span class="money">${vnd(o.totalAmount)}</span></div>
              <div class="acts">${this.actions(o)}</div>
            </div>`)}
          </div>`;
        })}
      </div>`);
    this.bind(() => this.showBoard());
  }

  /** One button per transition the server allows from the order's status (OrderStatus.next, BR09); no rule here. */
  actions(o) {
    const next = o.next || [];
    const a = [];
    if (next.includes("PROCESSING")) a.push(html`<button class="btn small" data-act="process" data-id="${o.id}">Start processing</button>`);
    if (next.includes("SHIPPED")) a.push(html`<button class="btn small" data-act="ship" data-id="${o.id}" data-code="${o.code}">Ship…</button>`);
    if (next.includes("DELIVERED")) a.push(html`<button class="btn small" data-act="deliver" data-id="${o.id}">Mark delivered</button>`);
    if (next.includes("CANCELLED")) a.push(html`<button class="btn small ghost" data-act="cancel" data-id="${o.id}">Cancel</button>`);
    return a;
  }

  async showOrder(id) {
    const nav = this.app.nav;
    mount(this.app.view, loading());
    let o;
    try { o = await api("GET", `/api/orders/${id}`); } catch (err) { return this.app.current(nav) && mount(this.app.view, failure(err)); }
    if (!this.app.current(nav)) return;   // a newer navigation owns the page
    mount(this.app.view, html`
      <p class="crumbs"><a href="#/staff/orders">Order board</a> / <span class="code">${o.code}</span></p>
      <div class="page-head"><div><p class="eyebrow">${o.customerName} · placed ${when(o.orderDate)}</p><h1>Order <span class="code" style="font-size:.8em">${o.code}</span></h1></div>
        <div class="acts" style="display:flex;gap:8px">${this.actions(o)}</div></div>
      ${orderBody(o)}`);
    this.bind(() => this.showOrder(id));
  }

  bind(refresh) {
    this.app.view.querySelectorAll("[data-act]").forEach((b) => b.addEventListener("click", async () => {
      const id = b.dataset.id;
      try {
        if (b.dataset.act === "ship") {
          const data = await this.askShipping(b.dataset.code);
          if (!data) return;
          await api("POST", `${this.controller}/${id}/ship`, data);
          toast("Order shipped, the customer can now track it");
        } else if (b.dataset.act === "cancel") {
          if (!confirm("Cancel this order? Stock is returned and an approved card payment is refunded.")) return;
          await api("POST", `${this.controller}/${id}/cancel`);
          toast("Order cancelled");
        } else {
          await api("POST", `${this.controller}/${id}/${b.dataset.act}`);
          toast(b.dataset.act === "process" ? "Packing started" : "Delivery recorded");
        }
        refresh();
      } catch (err) {
        toast(err.message, "error");
      }
    }));
  }

  askShipping(code) {
    return new Promise((resolve) => {
      const dlg = document.createElement("dialog");
      const tracking = "VN" + Math.floor(100000000 + Math.random() * 899999999);
      dlg.innerHTML = html`<form method="dialog" data-trace="ShippingController.ship · ShippingService.ship · Order.ship (BR10) · ShippingDAO.save · shipping">
        <h3 style="margin-bottom:6px">Ship <span class="code">${code}</span></h3>
        <p class="small" style="margin-bottom:16px">The carrier and tracking number are shown to the customer (UC09).</p>
        <div class="field"><label>Carrier</label><select name="carrier">${CARRIERS.map((c) => html`<option>${c}</option>`)}</select></div>
        <div class="field"><label>Tracking number</label><input name="tracking" value="${tracking}" required></div>
        <div style="display:flex;gap:10px;justify-content:flex-end"><button class="btn ghost" value="cancel">Back</button><button class="btn accent" value="ok">Hand over to carrier</button></div>
      </form>`.__raw;
      document.body.appendChild(dlg);
      dlg.addEventListener("close", () => {
        const f = dlg.querySelector("form");
        resolve(dlg.returnValue === "ok" ? { carrier: f.carrier.value, trackingNumber: f.tracking.value } : null);
        dlg.remove();
      });
      dlg.showModal();
    });
  }
}
