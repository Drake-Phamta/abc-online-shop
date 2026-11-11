// View class ProductForm (UC04 Browse / Search Products, UC05 View Product). Controller: ProductController.
import { api } from "../api.js";
import { html, mount, vnd, stockBadge, loading, failure } from "../ui.js";

const SORTS = [["RELEVANCE", "Featured"], ["PRICE_ASC", "Price, low to high"], ["PRICE_DESC", "Price, high to low"], ["NEWEST", "Newest"]];
const KIND_TITLE = { BOOK: "About the book", LAPTOP: "Laptop specifications", PHONE: "Phone specifications", APPAREL: "Size and material" };
const KIND_TABLE = { BOOK: "book_detail", LAPTOP: "laptop_detail", PHONE: "phone_detail", APPAREL: "apparel_detail" };

export class ProductForm {
  constructor(app) {
    this.app = app;
    this.controller = "/api/products";
  }

  card(p) {
    return html`<a class="card" href="#/p/${p.id}">
      <div class="pic">${p.image ? html`<img src="${p.image}" alt="${p.name}" loading="lazy">` : ""}</div>
      <span class="brand-line">${p.byline || p.category}</span>
      <span class="name">${p.name}</span>
      ${p.chips.length ? html`<div class="chips">${p.chips.map((c) => html`<span class="chip">${c}</span>`)}</div>` : ""}
      <div class="foot"><span class="money">${vnd(p.price)}</span>${p.stockState !== "IN" ? stockBadge(p.stockState, p.stock) : ""}</div>
    </a>`;
  }

  async showHome() {
    const nav = this.app.nav;
    mount(this.app.view, loading());
    try {
      const [books, electronics, fashion, latest] = await Promise.all([
        api("GET", `${this.controller}?category=books`), api("GET", `${this.controller}?category=electronics`),
        api("GET", `${this.controller}?category=fashion`), api("GET", `${this.controller}?sort=NEWEST`),
      ]);
      if (!this.app.current(nav)) return;   // a newer navigation owns the page
      const dept = (slug, title, line, list) => html`<a class="dept" href="#/c/${slug}">
        <h3>${title}</h3><span class="small">${line}</span>
        <div class="pics">${list.filter((p) => p.image).slice(0, 2).map((p) => html`<img src="${p.image}" alt="">`)}</div></a>`;
      mount(this.app.view, html`
        <section class="hero">
          <div>
            <p class="eyebrow">ABC Online Shop</p>
            <h1 class="two-tone">Books, devices and clothes. <span class="muted">Chosen with care, delivered across Vietnam.</span></h1>
          </div>
          <div class="promises">
            <div class="promise"><span class="n">1</span><div><b>Free delivery from 500.000 ₫</b><span class="small">Below that, a flat 30.000 ₫ fee.</span></div></div>
            <div class="promise"><span class="n">2</span><div><b>Pay by card or on delivery</b><span class="small">Your card number is never stored by the shop.</span></div></div>
            <div class="promise"><span class="n">3</span><div><b>Track every order</b><span class="small">From packing to your door, with the carrier's tracking number.</span></div></div>
          </div>
        </section>
        <section class="departments" data-trace="ProductForm.showHome → GET /api/products?category=… · ProductController.search · CatalogService.search · ProductDAO.search · product ⋈ category">
          ${dept("books", "Books", "Fiction, business and computing", books)}
          ${dept("electronics", "Electronics", "Laptops and smartphones", electronics)}
          ${dept("fashion", "Fashion", "Clothing and shoes", fashion)}
        </section>
        <div class="section-title"><h2 class="two-tone">New in. <span class="muted">The latest arrivals.</span></h2><a class="small" href="#/c/all">View all products →</a></div>
        <section class="grid">${latest.slice(0, 8).map((p) => this.card(p))}</section>`);
    } catch (err) {
      if (this.app.current(nav)) mount(this.app.view, failure(err));
    }
  }

  async showCatalogue(category, sort, q) {
    const nav = this.app.nav;
    sort = sort || "RELEVANCE";
    mount(this.app.view, loading());
    try {
      const params = new URLSearchParams({ sort });
      if (category && category !== "all") params.set("category", category);
      if (q) params.set("q", q);
      const [tree, products] = await Promise.all([api("GET", "/api/categories"), api("GET", `${this.controller}?${params}`)]);
      if (!this.app.current(nav)) return;   // a newer navigation owns the page
      const all = tree.flatMap((r) => [r, ...r.children]);
      const current = all.find((c) => c.slug === category);
      const title = q ? html`Results for “${q}”` : current ? current.name : "All products";
      const base = q ? `search?q=${encodeURIComponent(q)}&` : `c/${category}?`;
      mount(this.app.view, html`
        <div class="catalogue">
          <aside class="tree" data-trace="GET /api/categories · ProductController.categories · CatalogService.categories · ProductDAO.categories · category (tree)">
            <a href="#/c/all" class="${!current && !q ? "on" : ""}">All products</a>
            ${tree.map((r) => html`<h4>${r.name}</h4>
              <a href="#/c/${r.slug}" class="parent ${current?.slug === r.slug ? "on" : ""}">All ${r.name.toLowerCase()}</a>
              ${r.children.map((c) => html`<a href="#/c/${c.slug}" class="${current?.slug === c.slug ? "on" : ""}">${c.name}</a>`)}`)}
          </aside>
          <section>
            <div class="page-head"><div><p class="eyebrow">${products.length} products</p><h1>${title}</h1></div></div>
            <div class="toolbar">
              <div class="sorts">${SORTS.map(([k, label]) => html`<button data-sort="${k}" class="${k === sort ? "on" : ""}">${label}</button>`)}</div>
            </div>
            ${products.length === 0
              ? html`<div class="empty"><h3>No products found</h3><p>${q ? html`Nothing matches “${q}”. Try another word or ` : "This category is empty. "}<a href="#/c/all">see all products</a>.</p></div>`
              : html`<div class="grid" data-trace="ProductForm.showCatalogue → GET /api/products · ProductController.search · CatalogService.search · ProductDAO.search · product ⋈ category + *_detail (chips)">${products.map((p) => this.card(p))}</div>`}
          </section>
        </div>`);
      this.app.view.querySelectorAll("[data-sort]").forEach((b) => b.addEventListener("click", () => this.app.go(`${base}sort=${b.dataset.sort}`)));
    } catch (err) {
      if (this.app.current(nav)) mount(this.app.view, failure(err));
    }
  }

  async showProduct(id) {
    const nav = this.app.nav;
    mount(this.app.view, loading());
    let page;
    try {
      page = await api("GET", `${this.controller}/${id}`);
      if (!this.app.current(nav)) return;   // a newer navigation owns the page
    } catch (err) {
      return this.app.current(nav) && mount(this.app.view, failure(err));
    }
    const p = page.product;
    const canBuy = p.stockState !== "OUT";
    mount(this.app.view, html`
      <p class="crumbs"><a href="#/">Shop</a> / ${page.parentSlug ? html`<a href="#/c/${page.parentSlug}">${page.parentCategory}</a> / ` : ""}<a href="#/c/${p.categorySlug}">${p.category}</a></p>
      <section class="product">
        <div class="pic">${p.image ? html`<img src="${p.image}" alt="${p.name}">` : ""}</div>
        <div data-trace="ProductForm.showProduct → GET /api/products/${p.id} · ProductController.product · CatalogService.product · ProductDAO.findById · product ⋈ category + ${KIND_TABLE[p.detailKind] || "-"}">
          <span class="eyebrow">${p.byline || p.category}</span>
          <h1>${p.name}</h1>
          ${stockBadge(p.stockState, p.stock)}
          <div class="price-big">${vnd(p.price)}</div>
          <p class="lead">${page.description}</p>
          <div class="buy" data-trace="CartForm.submitAddItem → POST /api/cart/items · CartController.addItem · CartService.addItem · Cart.addItem (BR01, BR02) · CartDAO.save · cart_item">
            <div class="stepper"><button type="button" data-step="-1" aria-label="Fewer">−</button><input id="qty" type="number" min="1" max="${p.stock}" value="1" aria-label="Quantity"><button type="button" data-step="1" aria-label="More">+</button></div>
            <button class="btn accent" id="add" ${canBuy ? "" : "disabled"}>${canBuy ? "Add to cart" : "Out of stock"}</button>
          </div>
          <h3>${KIND_TITLE[p.detailKind] || "Details"}</h3>
          <table class="specs" data-trace="ProductDetail.specs() · ${KIND_TABLE[p.detailKind] || "-"} (chosen by category.detail_kind)">
            ${page.specs.map((s) => html`<tr><th>${s.label}</th><td>${s.value}</td></tr>`)}
            <tr><th>Category</th><td>${page.parentCategory ? `${page.parentCategory} › ` : ""}${p.category}</td></tr>
            <tr><th>SKU</th><td class="code">${p.sku}</td></tr>
          </table>
        </div>
      </section>`);
    const qty = document.getElementById("qty");
    this.app.view.querySelectorAll("[data-step]").forEach((b) => b.addEventListener("click", () => {
      qty.value = Math.max(1, Math.min(p.stock || 1, Number(qty.value) + Number(b.dataset.step)));
    }));
    document.getElementById("add").addEventListener("click", () => this.app.cartForm.submitAddItem(p.id, Number(qty.value)));
  }
}
