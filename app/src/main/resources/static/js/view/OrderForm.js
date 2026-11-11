// View class OrderForm (UC07 Place Order with UC21 Validate Cart, UC09 Track Order). Controller: OrderController.
import { api } from "../api.js";
import { html, mount, vnd, when, statusBadge, STATUS, loading, failure, toast } from "../ui.js";

const PAYMENT_TONE = { APPROVED: "ok", COMPLETED: "ok", DECLINED: "danger", REFUNDED: "warn" };

const FLOW = {
  CARD: ["PENDING_PAYMENT", "PAID", "PROCESSING", "SHIPPED", "DELIVERED"],
  COD: ["PLACED", "PROCESSING", "SHIPPED", "DELIVERED"],
};

export function statusSteps(order) {
  const flow = FLOW[order.paymentMethod];
  if (order.status === "CANCELLED") return html`<div class="notice danger"><b>This order was cancelled.</b>Reserved stock was returned${order.payments.some((p) => p.status === "REFUNDED") ? " and the card payment was refunded" : ""}.</div>`;
  const at = flow.indexOf(order.status);
  return html`<div class="steps" style="grid-template-columns:repeat(${flow.length},1fr)" data-trace="OrderStatus transition table (BR09) · order_event">
    ${flow.map((s, i) => html`<div class="step ${i < at ? "done" : ""} ${i === at ? "done now" : ""}">${STATUS[s].label}</div>`)}</div>`;
}

export function orderBody(o) {
  return html`
    <div class="two-col">
      <div>
        ${statusSteps(o)}
        <section class="lines">${o.lines.map((l) => html`<div class="line" style="grid-template-columns:1fr auto">
          <div class="meta"><a href="#/p/${l.productId}">${l.name}</a><span class="small">${l.quantity} × ${vnd(l.unitPrice)} (price at checkout)</span></div>
          <div class="right"><span class="money">${vnd(l.subTotal)}</span></div></div>`)}</section>
        <h3 style="margin:28px 0 8px">History</h3>
        <ul class="timeline" data-trace="Order.getEvents · OrderDAO.findById · order_event">
          ${o.events.slice().reverse().map((e) => html`<li><time>${when(e.at)}</time><div>${statusBadge(e.status)} <b>${e.note || ""}</b><br><span class="small">by ${e.actor}</span></div></li>`)}
        </ul>
      </div>
      <aside class="panel">
        <h3>Totals</h3>
        <div class="sum-row"><span>Subtotal</span><b>${vnd(o.subtotal)}</b></div>
        ${o.discount ? html`<div class="sum-row"><span>VIP discount</span><b>− ${vnd(o.discount)}</b></div>` : ""}
        <div class="sum-row"><span>Delivery</span><b>${o.shippingFee ? vnd(o.shippingFee) : "Free"}</b></div>
        <div class="sum-row total"><span>Total</span><b>${vnd(o.total)}</b></div>
        <h3 style="margin-top:22px">Delivery</h3>
        ${o.address ? html`<p class="small"><b style="color:var(--ink)">${o.address.recipient}</b>, ${o.address.phone}<br>${o.address.line}</p>` : ""}
        ${o.shipping ? html`<p class="small" data-trace="Shipping · shipping (UNIQUE order_id, BR10)">Carrier <b style="color:var(--ink)">${o.shipping.carrier}</b>, tracking <span class="code">${o.shipping.trackingNumber}</span><br>
          Shipped ${when(o.shipping.shipped)}${o.shipping.delivered ? html`, delivered ${when(o.shipping.delivered)}` : ""}</p>` : html`<p class="small">Not shipped yet.</p>`}
        <h3 style="margin-top:22px">Payment</h3>
        <p class="small">${o.paymentMethod === "CARD" ? "Card through the payment provider" : "Cash on delivery"}</p>
        ${o.payments.map((p) => html`<div class="sum-row" data-trace="Payment (${p.method === "CARD" ? "PayCredit · pay_credit" : "PayCash · pay_cash"})"><span>${p.detail}</span><span class="badge ${PAYMENT_TONE[p.status]}">${p.status.toLowerCase()}</span></div>`)}
      </aside>
    </div>`;
}

export class OrderForm {
  constructor(app) {
    this.app = app;
    this.controller = "/api/orders";
  }

  async showCheckout() {
    const nav = this.app.nav;
    mount(this.app.view, loading());
    let data;
    try { data = await api("GET", "/api/checkout"); } catch (err) { return this.app.current(nav) && mount(this.app.view, failure(err)); }
    if (!this.app.current(nav)) return;   // a newer navigation owns the page
    const cart = data.cart;
    this.app.setCartCount(cart.count);
    if (cart.lines.length === 0) return this.app.go("cart");
    const blocking = data.issues.filter((i) => i.blocking);
    const changed = data.issues.filter((i) => i.kind === "PRICE_CHANGED");
    const t = data.totals;
    mount(this.app.view, html`
      <div class="page-head"><div><p class="eyebrow">Checkout</p><h1>Review and place your order</h1></div></div>
      ${blocking.length ? html`<div class="notice danger" data-trace="Cart.validate (UC21, BR03) · blocking issues stop UC07 (A1)"><b>Some products cannot be ordered as they are.</b><ul>${blocking.map((i) => html`<li>${i.message}</li>`)}</ul><a href="#/cart">Change your cart</a></div>` : ""}
      ${changed.length ? html`<div class="notice warn" data-trace="Cart.validate (UC21, BR03) · price changed, cart_item.cart_price updated"><b>Prices changed since you added these products.</b><ul>${changed.map((i) => html`<li>${i.message}</li>`)}</ul>The totals below already use the new prices.</div>` : ""}
      <div class="two-col">
        <form id="checkout" data-trace="OrderForm.showCheckout ← GET /api/checkout · OrderController.checkout · OrderService.checkout · Cart.validate, Order.Totals (BR04)">
          <h3>Deliver to</h3>
          <div class="choice">${data.addresses.map((a, i) => html`<label><input type="radio" name="address" value="${a.id}" ${a.isDefault || i === 0 ? "checked" : ""}>
            <span><b>${a.recipient}</b> · ${a.phone}<span class="small">${a.line}</span></span></label>`)}</div>
          <h3>Payment</h3>
          <div class="choice">
            <label><input type="radio" name="method" value="CARD" checked><span><b>Card</b><span class="small">Pay now through the payment provider. The shop keeps only the last four digits.</span></span></label>
            <label><input type="radio" name="method" value="COD"><span><b>Cash on delivery</b><span class="small">Pay the courier when the parcel arrives.</span></span></label>
          </div>
          <h3>Items</h3>
          <section class="lines">${cart.lines.map((l) => html`<div class="line" style="grid-template-columns:64px 1fr auto">
            <div class="thumb" style="width:64px;height:64px">${l.image ? html`<img src="${l.image}" alt="">` : ""}</div>
            <div class="meta"><span>${l.name}</span><span class="small">${l.quantity} × ${vnd(l.cartPrice)}</span></div>
            <span class="money">${vnd(l.subTotal)}</span></div>`)}</section>
        </form>
        <aside class="panel sticky">
          <h3>Order total</h3>
          <div class="sum-row"><span>Subtotal</span><b>${vnd(t.subtotal)}</b></div>
          ${t.discount ? html`<div class="sum-row"><span>${data.customerKind} discount (${Math.round(data.discountRate * 100)} %)</span><b>− ${vnd(t.discount)}</b></div>` : ""}
          <div class="sum-row"><span>Delivery</span><b>${t.shippingFee ? vnd(t.shippingFee) : "Free"}</b></div>
          <div class="sum-row total"><span>Total</span><b>${vnd(t.total)}</b></div>
          <button class="btn accent wide" id="place" ${blocking.length ? "disabled" : ""} style="margin-top:16px"
            data-trace="OrderForm.submitOrder → POST /api/orders · OrderController.placeOrder · OrderService.placeOrder · Order.place, ProductDAO.reserveStock (BR05), OrderDAO.insert · customer_order, order_item">Place order</button>
          <p class="small" style="margin-top:12px">Stock is reserved when you place the order and released if it is cancelled.</p>
        </aside>
      </div>`);
    document.getElementById("place").addEventListener("click", () => {
      const f = document.getElementById("checkout");
      this.submitOrder(Number(f.address.value), f.method.value, t.total);
    });
  }

  async submitOrder(addressId, paymentMethod, expectedTotal) {
    const btn = document.getElementById("place");
    btn.disabled = true;
    btn.textContent = "Placing order…";
    try {
      const res = await api("POST", this.controller, { addressId, paymentMethod, expectedTotal });
      this.app.setCartCount(0);
      if (res.status === "PENDING_PAYMENT") {
        toast(`Order ${res.code} created. Complete the card payment.`);
        this.app.go(`pay/${res.orderId}`);
      } else {
        toast(`Order ${res.code} placed. Pay the courier on delivery.`);
        this.app.go(`orders/${res.orderId}`);
      }
    } catch (err) {
      toast(err.message, "error");
      this.showCheckout();
    }
  }

  async showOrders() {
    const nav = this.app.nav;
    mount(this.app.view, loading());
    let orders;
    try { orders = await api("GET", this.controller); } catch (err) { return this.app.current(nav) && mount(this.app.view, failure(err)); }
    if (!this.app.current(nav)) return;   // a newer navigation owns the page
    mount(this.app.view, html`
      <div class="page-head"><div><p class="eyebrow">Your account</p><h1>My orders</h1></div></div>
      ${orders.length === 0 ? html`<div class="empty"><h3>No orders yet</h3><p><a href="#/c/all">Start shopping</a></p></div>` : html`
      <table class="orders-table" data-trace="OrderForm.showOrders ← GET /api/orders · OrderController.myOrders · OrderService.ordersOf · OrderDAO.findByCustomer (BR08)">
        <thead><tr><th>Order</th><th>Date</th><th>Items</th><th>Status</th><th style="text-align:right">Total</th></tr></thead>
        <tbody>${orders.map((o) => html`<tr class="clickable" data-id="${o.id}"><td class="code">${o.code}</td><td>${when(o.orderDate)}</td>
          <td>${o.firstItem}${o.itemCount > 1 ? html` <span class="small">+ ${o.itemCount - 1} more</span>` : ""}</td><td>${statusBadge(o.status)}</td>
          <td style="text-align:right" class="money">${vnd(o.totalAmount)}</td></tr>`)}</tbody></table>`}`);
    this.app.view.querySelectorAll("tr[data-id]").forEach((tr) => tr.addEventListener("click", () => this.app.go(`orders/${tr.dataset.id}`)));
  }

  async showOrder(id) {
    const nav = this.app.nav;
    mount(this.app.view, loading());
    let o;
    try { o = await api("GET", `${this.controller}/${id}`); } catch (err) { return this.app.current(nav) && mount(this.app.view, failure(err)); }
    if (!this.app.current(nav)) return;   // a newer navigation owns the page
    const canCancel = o.next.includes("CANCELLED");
    mount(this.app.view, html`
      <p class="crumbs"><a href="#/orders">My orders</a> / <span class="code">${o.code}</span></p>
      <div class="page-head" data-trace="OrderForm.showOrder ← GET /api/orders/${o.id} · OrderController.order · OrderService.details · OrderDAO.findById · customer_order, order_item, order_event, payment, shipping">
        <div><p class="eyebrow">Placed ${when(o.orderDate)}</p><h1>Order <span class="code" style="font-size:.8em">${o.code}</span></h1></div>
        <div style="display:flex;gap:10px">
          ${o.status === "PENDING_PAYMENT" ? html`<a class="btn accent" href="#/pay/${o.id}">Pay now</a>` : ""}
          ${canCancel ? html`<button class="btn ghost" id="cancel">Cancel order</button>` : ""}
        </div>
      </div>
      ${orderBody(o)}`);
    const c = document.getElementById("cancel");
    if (c) c.addEventListener("click", () => this.submitCancel(o));
  }

  async submitCancel(o) {
    if (!confirm(`Cancel order ${o.code}? Reserved stock goes back to the shop.`)) return;
    try {
      await api("POST", `${this.controller}/${o.id}/cancel`);
      toast(`Order ${o.code} cancelled`);
      this.showOrder(o.id);
    } catch (err) {
      toast(err.message, "error");
    }
  }
}
