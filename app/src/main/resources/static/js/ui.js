// Rendering helpers shared by the view classes. html`` escapes every value unless it is raw().

const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };

export const raw = (s) => ({ __raw: String(s) });

function render(v) {
  if (v === null || v === undefined || v === false) return "";
  if (Array.isArray(v)) return v.map(render).join("");
  if (typeof v === "object" && "__raw" in v) return v.__raw;
  return String(v).replace(/[&<>"']/g, (c) => ESC[c]);
}

export function html(strings, ...values) {
  let out = strings[0];
  values.forEach((v, i) => { out += render(v) + strings[i + 1]; });
  return raw(out);
}

export function mount(el, template) {
  el.innerHTML = template.__raw;
}

const VND = new Intl.NumberFormat("vi-VN");
export const vnd = (n) => VND.format(n) + " ₫";

export function when(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }) + ", "
    + d.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
}

export const STATUS = {
  PENDING_PAYMENT: { label: "Waiting for payment", tone: "warn" },
  PLACED: { label: "Placed", tone: "accent" },
  PAID: { label: "Paid", tone: "accent" },
  PROCESSING: { label: "Processing", tone: "warn" },
  SHIPPED: { label: "Shipped", tone: "ok" },
  DELIVERED: { label: "Delivered", tone: "ok" },
  CANCELLED: { label: "Cancelled", tone: "danger" },
};

export const statusBadge = (s) => html`<span class="badge ${STATUS[s]?.tone || ""}">${STATUS[s]?.label || s}</span>`;

export function stockBadge(state, stock) {
  if (state === "OUT") return html`<span class="badge danger">Out of stock</span>`;
  if (state === "LOW") return html`<span class="badge warn">Only ${stock} left</span>`;
  return html`<span class="badge ok">In stock</span>`;
}

let toastTimer;
export function toast(message, kind = "") {
  let el = document.querySelector(".toast");
  if (!el) {
    el = document.createElement("div");
    el.className = "toast";
    el.setAttribute("role", "status");
    document.body.appendChild(el);
  }
  el.textContent = message;
  el.className = "toast show " + kind;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.className = "toast " + kind; }, 3200);
}

export const loading = () => html`<div class="empty"><p class="small">Loading…</p></div>`;

export function failure(err) {
  return html`<div class="empty"><h3>Something went wrong</h3><p>${err.message}</p>
    <p><a class="btn ghost" href="#/">Back to the shop</a></p></div>`;
}
