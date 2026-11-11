// View class CartForm (UC06 Manage Shopping Cart). Controller: CartController, /api/cart.
import { api } from "../api.js";
import { html, mount, vnd, loading, failure, toast } from "../ui.js";

export class CartForm {
  constructor(app) {
    this.app = app;
    this.controller = "/api/cart";
  }

  async submitAddItem(productId, quantity) {
    if (!this.app.me.loggedIn) {
      toast("Log in to add products to your cart.");
      return this.app.go(`login?next=${encodeURIComponent(`p/${productId}`)}`);
    }
    if (this.app.me.role !== "CUSTOMER") return toast("Staff accounts cannot buy.", "error");
    try {
      const cart = await api("POST", `${this.controller}/items`, { productId, quantity });
      this.app.setCartCount(cart.count);
      toast(`Added to your cart · ${cart.count} item${cart.count === 1 ? "" : "s"}`);
    } catch (err) {
      toast(err.message, "error");
    }
  }

  async showCart(cart) {
    const nav = this.app.nav;
    if (!cart) {
      mount(this.app.view, loading());
      try { cart = await api("GET", this.controller); } catch (err) { return this.app.current(nav) && mount(this.app.view, failure(err)); }
      if (!this.app.current(nav)) return;   // a newer navigation owns the page
    }
    this.app.setCartCount(cart.count);
    if (cart.lines.length === 0) {
      return mount(this.app.view, html`<div class="empty"><h2>Your cart is empty</h2>
        <p class="lead" style="margin:10px auto 20px">Find something you like in the catalogue.</p>
        <a class="btn" href="#/c/all">Browse products</a></div>`);
    }
    mount(this.app.view, html`
      <div class="page-head"><div><p class="eyebrow">Shopping cart</p><h1>${cart.count} item${cart.count === 1 ? "" : "s"} in your cart</h1></div></div>
      <div class="two-col">
        <section class="lines" data-trace="CartForm.showCart ← GET /api/cart · CartController.viewCart · CartService.cart · CartDAO.findOrCreate · cart, cart_item ⋈ product">
          ${cart.lines.map((l) => html`
            <div class="line">
              <a class="thumb" href="#/p/${l.productId}">${l.image ? html`<img src="${l.image}" alt="">` : ""}</a>
              <div class="meta">
                <a href="#/p/${l.productId}">${l.name}</a>
                <span class="small">${vnd(l.cartPrice)} each${l.cartPrice !== l.currentPrice ? html` · <b style="color:var(--warn)">now ${vnd(l.currentPrice)}, updated at checkout</b>` : ""}</span>
                <div class="stepper" data-product="${l.productId}">
                  <button type="button" data-step="-1" aria-label="Fewer">−</button><input type="number" min="1" max="${l.stock}" value="${l.quantity}" aria-label="Quantity"><button type="button" data-step="1" aria-label="More">+</button>
                </div>
              </div>
              <div class="right"><span class="money">${vnd(l.subTotal)}</span><button class="link-btn" data-remove="${l.productId}">Remove</button></div>
            </div>`)}
        </section>
        <aside class="panel sticky">
          <h3>Summary</h3>
          <div class="sum-row"><span>Subtotal</span><b>${vnd(cart.subtotal)}</b></div>
          <p class="small">VIP discount and delivery fee are calculated at checkout. Delivery is free from 500.000 ₫.</p>
          <a class="btn accent wide" href="#/checkout">Go to checkout</a>
        </aside>
      </div>`);
    this.app.view.querySelectorAll(".stepper[data-product]").forEach((s) => {
      const id = Number(s.dataset.product);
      const input = s.querySelector("input");
      s.querySelectorAll("[data-step]").forEach((b) => b.addEventListener("click", () => this.changeQuantity(id, Number(input.value) + Number(b.dataset.step))));
      input.addEventListener("change", () => this.changeQuantity(id, Number(input.value)));
    });
    this.app.view.querySelectorAll("[data-remove]").forEach((b) => b.addEventListener("click", () => this.removeItem(Number(b.dataset.remove))));
  }

  async changeQuantity(productId, quantity) {
    if (quantity < 1) return this.removeItem(productId);
    try {
      this.showCart(await api("PUT", `${this.controller}/items/${productId}`, { quantity }));
    } catch (err) {
      toast(err.message, "error");
      this.showCart();
    }
  }

  async removeItem(productId) {
    try {
      this.showCart(await api("DELETE", `${this.controller}/items/${productId}`));
      toast("Removed from your cart");
    } catch (err) {
      toast(err.message, "error");
    }
  }
}
