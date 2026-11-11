// Entry point: routes a URL hash to a view class and keeps the header in sync with the session.
import { api } from "./api.js";
import { html, mount, vnd, failure, toast } from "./ui.js";
import { CustomerForm } from "./view/CustomerForm.js";
import { ProductForm } from "./view/ProductForm.js";
import { CartForm } from "./view/CartForm.js";
import { OrderForm } from "./view/OrderForm.js";
import { PaymentForm } from "./view/PaymentForm.js";
import { StaffOrderForm } from "./view/StaffOrderForm.js";
import { StockForm } from "./view/StockForm.js";
import { SearchForm } from "./view/SearchForm.js";

class App {
  constructor() {
    this.view = document.getElementById("view");
    this.me = { loggedIn: false };
    this.nav = 0;   // number of the current navigation; a view drops a load that a newer navigation overtook
    this.customerForm = new CustomerForm(this);
    this.productForm = new ProductForm(this);
    this.cartForm = new CartForm(this);
    this.orderForm = new OrderForm(this);
    this.paymentForm = new PaymentForm(this);
    this.staffOrderForm = new StaffOrderForm(this);
    this.stockForm = new StockForm(this);
    this.searchForm = new SearchForm(this);
  }

  async start() {
    document.getElementById("search").addEventListener("submit", (e) => {
      e.preventDefault();
      const q = new FormData(e.target).get("q").trim();
      this.go(q ? `search?q=${encodeURIComponent(q)}` : "c/all");
    });
    document.getElementById("voice").addEventListener("click", () => this.searchForm.startVoice());
    const photo = document.getElementById("photo");
    document.getElementById("camera").addEventListener("click", () => photo.click());
    photo.addEventListener("change", () => { this.searchForm.submitPhoto(photo.files[0]); photo.value = ""; });
    const lens = document.getElementById("lens");
    const setLens = (on) => { document.body.classList.toggle("lens", on); lens.checked = on; sessionStorage.setItem("lens", on ? "1" : ""); };
    lens.addEventListener("change", () => setLens(lens.checked));
    document.addEventListener("keydown", (e) => { if (e.altKey && e.key.toLowerCase() === "l") setLens(!lens.checked); });
    try { setLens(sessionStorage.getItem("lens") === "1"); } catch { /* storage may be blocked */ }
    window.addEventListener("hashchange", () => this.route());
    await this.refreshMe();
    this.route();
  }

  async refreshMe() {
    try { this.me = await api("GET", "/api/auth/me"); } catch { this.me = { loggedIn: false }; }
    this.renderHeader();
  }

  renderHeader() {
    const me = this.me;
    const account = document.getElementById("account");
    if (!me.loggedIn) {
      mount(account, html`<a href="#/login">Log in</a>`);
    } else if (me.role === "CUSTOMER") {
      mount(account, html`
        <span class="who">Hello, <b>${me.name.split(" ").pop()}</b>${me.kind && me.kind !== "Customer" ? html` · ${me.kind}` : ""}</span>
        <a href="#/orders">My orders</a>
        <a class="cart-link" href="#/cart" data-trace="CartForm · GET /api/cart · CartController.viewCart · CartService.cart">Cart <span class="count">${me.cartCount || 0}</span></a>
        <button class="link-btn" id="logout">Log out</button>`);
    } else {
      mount(account, html`<span class="who"><b>${me.name}</b> · ${me.role === "SALES" ? "Sales staff" : "Warehouse staff"}</span>
        <button class="link-btn" id="logout">Log out</button>`);
    }
    const bar = document.getElementById("staff-bar");
    mount(bar, me.loggedIn && me.role !== "CUSTOMER" ? html`<div class="staff-bar"><div class="wrap">
        <b>Staff area</b>
        ${me.role === "SALES" ? html`<a href="#/staff/orders">Order board (UC14)</a>` : html`<a href="#/staff/stock">Inventory (UC15)</a>`}
        <a href="#/">Shop front</a></div></div>` : html``);
    const out = document.getElementById("logout");
    if (out) out.addEventListener("click", () => this.customerForm.submitLogout());
  }

  setCartCount(n) {
    this.me.cartCount = n;
    const el = document.querySelector(".cart-link .count");
    if (el) el.textContent = n;
  }

  go(path) {
    location.hash = "#/" + path;
  }

  /** Customer pages need a customer session; staff pages need the staff role (BR13). */
  needs(role) {
    if (!this.me.loggedIn) {
      this.go(`login?next=${encodeURIComponent(location.hash.slice(2))}`);
      return false;
    }
    if (this.me.role !== role) {
      mount(this.view, failure(new Error("Your account cannot open this page.")));
      return false;
    }
    return true;
  }

  current(nav) {
    return nav === this.nav;
  }

  route() {
    this.nav += 1;
    const [path, query] = location.hash.replace(/^#\/?/, "").split("?");
    const parts = path.split("/").filter(Boolean);
    const params = new URLSearchParams(query || "");
    document.querySelectorAll("#nav a").forEach((a) => a.classList.toggle("on", parts[0] === "c" && parts[1] === a.dataset.dept));
    window.scrollTo({ top: 0 });
    switch (parts[0]) {
      case undefined: return this.productForm.showHome();
      case "c": return this.productForm.showCatalogue(parts[1] || "all", params.get("sort"));
      case "search": return parts[1] === "photo" ? this.searchForm.showPhotoResults() : this.searchForm.showResults(params.get("q"));
      case "p": return this.productForm.showProduct(Number(parts[1]));
      case "login": return this.customerForm.showLogin(params.get("next"));
      case "cart": return this.needs("CUSTOMER") && this.cartForm.showCart();
      case "checkout": return this.needs("CUSTOMER") && this.orderForm.showCheckout();
      case "orders": return this.needs("CUSTOMER") && (parts[1] ? this.orderForm.showOrder(Number(parts[1])) : this.orderForm.showOrders());
      case "pay": return this.needs("CUSTOMER") && this.paymentForm.showPayment(Number(parts[1]));
      case "staff":
        if (parts[1] === "stock") return this.needs("WAREHOUSE") && this.stockForm.showStock();
        if (parts[1] === "orders" && parts[2]) return this.needs("SALES") && this.staffOrderForm.showOrder(Number(parts[2]));
        return this.needs("SALES") && this.staffOrderForm.showBoard();
      default: mount(this.view, failure(new Error("This page does not exist.")));
    }
  }
}

export const app = new App();
app.start().catch((e) => toast(e.message, "error"));
