// View class PaymentForm (UC08 Make Payment). Controller: PaymentController, /api/orders/{id}/payments.
import { api } from "../api.js";
import { html, mount, vnd, loading, failure, toast } from "../ui.js";

export class PaymentForm {
  constructor(app) {
    this.app = app;
    this.controller = "/api/orders";
  }

  async showPayment(orderId) {
    const nav = this.app.nav;
    mount(this.app.view, loading());
    let o;
    try { o = await api("GET", `${this.controller}/${orderId}`); } catch (err) { return this.app.current(nav) && mount(this.app.view, failure(err)); }
    if (!this.app.current(nav)) return;   // a newer navigation owns the page
    if (o.status !== "PENDING_PAYMENT") return this.app.go(`orders/${o.id}`);
    const declined = o.payments.filter((p) => p.status === "DECLINED").length;
    mount(this.app.view, html`
      <p class="crumbs"><a href="#/orders">My orders</a> / <a href="#/orders/${o.id}" class="code">${o.code}</a> / Payment</p>
      <div class="two-col">
        <form class="panel" id="pay" novalidate data-trace="PaymentForm.submitPayment → POST /api/orders/${o.id}/payments · PaymentController.pay · PaymentService.pay · CardProvider.charge · Order.recordCardPayment (BR07) · payment, pay_credit">
          <p class="eyebrow">Card payment</p>
          <h2 style="margin-bottom:18px">Pay ${vnd(o.total)} for <span class="code">${o.code}</span></h2>
          ${declined ? html`<div class="notice danger"><b>The last attempt was declined.</b>Your order and its reserved stock are kept. Try another card or cancel the order.</div>` : ""}
          <div class="field"><label for="holder">Name on card</label><input id="holder" name="holder" autocomplete="cc-name" placeholder="NGUYEN VAN AN"></div>
          <div class="field"><label for="number">Card number</label><input id="number" name="number" inputmode="numeric" autocomplete="cc-number" placeholder="4242 4242 4242 4242"></div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
            <div class="field"><label for="expiry">Expiry (MM/YY)</label><input id="expiry" name="expiry" autocomplete="cc-exp" placeholder="08/28"></div>
            <div class="field"><label for="cvv">CVV</label><input id="cvv" name="cvv" inputmode="numeric" autocomplete="cc-csc" placeholder="123"></div>
          </div>
          <p class="small" id="pay-error" role="alert" style="color:var(--danger)"></p>
          <button class="btn accent wide" type="submit">Pay ${vnd(o.total)}</button>
          <p class="small" style="margin-top:12px">Test cards of the simulated provider: 4242 4242 4242 4242 is approved, 4000 0000 0000 0002 is declined.</p>
        </form>
        <aside class="panel">
          <h3>Order</h3>
          ${o.lines.map((l) => html`<div class="sum-row"><span>${l.quantity} × ${l.name}</span><b>${vnd(l.subTotal)}</b></div>`)}
          ${o.discount ? html`<div class="sum-row"><span>VIP discount</span><b>− ${vnd(o.discount)}</b></div>` : ""}
          <div class="sum-row"><span>Delivery</span><b>${o.shippingFee ? vnd(o.shippingFee) : "Free"}</b></div>
          <div class="sum-row total"><span>Total</span><b>${vnd(o.total)}</b></div>
          <p class="small">The shop stores the card holder, the last four digits, the expiry and the provider's token. The full number and the CVV are never stored.</p>
        </aside>
      </div>`);
    const f = document.getElementById("pay");
    f.addEventListener("submit", (e) => {
      e.preventDefault();
      this.submitPayment(o, { cardHolder: f.holder.value, cardNumber: f.number.value, expiry: f.expiry.value, cvv: f.cvv.value });
    });
  }

  async submitPayment(order, card) {
    const error = document.getElementById("pay-error");
    const btn = document.querySelector("#pay button[type=submit]");
    error.textContent = "";
    btn.disabled = true;
    btn.textContent = "Contacting the payment provider…";
    try {
      const res = await api("POST", `${this.controller}/${order.id}/payments`, card);
      if (res.approved) {
        toast("Payment approved. Thank you!");
        this.app.go(`orders/${order.id}`);
      } else {
        toast(res.message, "error");
        this.showPayment(order.id);
      }
    } catch (err) {
      error.textContent = err.message;
      btn.disabled = false;
      btn.textContent = `Pay again`;
    }
  }
}
