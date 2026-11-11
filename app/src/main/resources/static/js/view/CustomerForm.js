// View class CustomerForm (UC02 Login). Controller: AuthController, /api/auth.
import { api } from "../api.js";
import { html, mount, toast } from "../ui.js";

const DEMO = [
  { email: "an.nguyen@example.com", label: "Customer, VIP level 2 (5 % discount)" },
  { email: "lan.tran@example.com", label: "Customer, new account" },
  { email: "sales@example.com", label: "Sales staff (order board)" },
  { email: "warehouse@example.com", label: "Warehouse staff (inventory)" },
];

export class CustomerForm {
  constructor(app) {
    this.app = app;
    this.controller = "/api/auth";
  }

  showLogin(next) {
    this.next = next;
    mount(this.app.view, html`
      <section class="login">
        <div>
          <p class="eyebrow">Account</p>
          <h1 class="two-tone">Welcome back. <span class="muted">Your cart and orders are waiting.</span></h1>
          <p class="lead">Customers see their own cart and orders only; staff accounts open the order board or the inventory.</p>
        </div>
        <form class="panel" id="login-form" data-trace="CustomerForm.submitLogin → POST /api/auth/login · AuthController.login · AuthService.login · CustomerDAO/StaffDAO.findAccount · customer, staff">
          <h3>Log in</h3>
          <div class="field"><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="username" required></div>
          <div class="field"><label for="password">Password</label><input id="password" name="password" type="password" autocomplete="current-password" required></div>
          <p class="small" id="login-error" role="alert"></p>
          <button class="btn accent wide" type="submit">Log in</button>
          <div class="demo-accounts">
            <span class="small">Demo accounts (password demo1234):</span>
            ${DEMO.map((d) => html`<button type="button" data-email="${d.email}"><b>${d.email}</b><br><span class="small">${d.label}</span></button>`)}
          </div>
        </form>
      </section>`);
    const form = document.getElementById("login-form");
    form.querySelectorAll("[data-email]").forEach((b) => b.addEventListener("click", () => {
      form.email.value = b.dataset.email;
      form.password.value = "demo1234";
      form.password.focus();
    }));
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      this.submitLogin(form.email.value, form.password.value);
    });
  }

  async submitLogin(email, password) {
    const error = document.getElementById("login-error");
    error.textContent = "";
    try {
      const me = await api("POST", `${this.controller}/login`, { email, password });
      await this.app.refreshMe();
      toast(`Logged in as ${me.name}`);
      const start = me.role === "SALES" ? "staff/orders" : me.role === "WAREHOUSE" ? "staff/stock" : this.next || "";
      this.app.go(start);
    } catch (err) {
      error.textContent = err.message;
      error.style.color = "var(--danger)";
    }
  }

  async submitLogout() {
    await api("POST", `${this.controller}/logout`);
    await this.app.refreshMe();
    this.app.go("");
  }
}
