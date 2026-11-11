// View class SearchForm (UC04 search with the AI search, docs/SPEC.md section 6). Controller: SearchController.
import { api, ApiError } from "../api.js";
import { html, mount, vnd, stockBadge, loading, failure, toast } from "../ui.js";

const TRACE_TEXT = "SearchForm.showResults → GET /api/search · SearchController.search · SearchService.search · "
  + "QueryInterpreter.interpret · ProductIndex.rank · product ⋈ category + *_detail";
const TRACE_PHOTO = "SearchForm.submitPhoto → POST /api/search/photo · SearchController.searchByPhoto · "
  + "SearchService.searchByPhoto · ImageIndex.rank · product image files";

export class SearchForm {
  constructor(app) {
    this.app = app;
    this.controller = "/api/search";
    this.lastPhoto = null;   // {url, name, result}: the photo stays in this page only (AI05)
  }

  /** The understood query as chips (AI02). */
  understood(r) {
    const u = r.understood;
    const chips = [
      ...u.terms.map((t) => html`<span class="chip">${t}</span>`),
      ...u.related.map((t) => html`<span class="chip soft" title="related words of the shop's lexicon">${t}</span>`),
      ...u.corrections.map((t) => html`<span class="chip fix" title="spelling corrected to a catalogue word">${t}</span>`),
    ];
    if (u.maxPrice !== null && u.minPrice !== null) chips.push(html`<span class="chip price">${vnd(u.minPrice)} to ${vnd(u.maxPrice)}</span>`);
    else if (u.maxPrice !== null) chips.push(html`<span class="chip price">at most ${vnd(u.maxPrice)}</span>`);
    else if (u.minPrice !== null) chips.push(html`<span class="chip price">at least ${vnd(u.minPrice)}</span>`);
    if (u.cheap) chips.push(html`<span class="chip price">cheaper first</span>`);
    return html`<div class="understood"><span class="label">Understood as</span>${chips}</div>`;
  }

  card(f, max) {
    const p = f.product;
    const share = max > 0 ? Math.max(8, Math.round((f.score / max) * 100)) : 0;
    return html`<a class="card found" href="#/p/${p.id}">
      <div class="pic">${p.image ? html`<img src="${p.image}" alt="${p.name}" loading="lazy">` : ""}</div>
      <span class="brand-line">${p.byline || p.category}</span>
      <span class="name">${p.name}</span>
      <div class="foot"><span class="money">${vnd(p.price)}</span>${p.stockState !== "IN" ? stockBadge(p.stockState, p.stock) : ""}</div>
      <div class="why">
        ${max > 0 ? html`<div class="meter" title="relevance ${f.score}"><i style="width:${share}%"></i></div>` : ""}
        <ul>${f.reasons.map((x) => html`<li>${x}</li>`)}</ul>
      </div>
    </a>`;
  }

  results(r) {
    const max = r.results.reduce((m, f) => Math.max(m, f.score), 0);
    return html`<div class="grid" data-trace="${r.mode === "PHOTO" ? TRACE_PHOTO : TRACE_TEXT}">${r.results.map((f) => this.card(f, max))}</div>`;
  }

  /** FR-S1 to FR-S3 and FR-S6: typed or spoken text. */
  async showResults(q) {
    const nav = this.app.nav;
    if (!q) return this.app.go("c/all");
    mount(this.app.view, loading());
    let r;
    try {
      r = await api("GET", `${this.controller}?q=${encodeURIComponent(q)}`);
    } catch (err) {
      return this.app.current(nav) && mount(this.app.view, failure(err));
    }
    if (!this.app.current(nav)) return;   // a newer navigation owns the page
    const how = r.fallback ? "Keyword search" : "AI search";
    mount(this.app.view, html`
      <div class="page-head"><div>
        <p class="eyebrow">${how} · ${r.results.length} products · ${r.tookMs} ms</p>
        <h1>Results for “${q}”</h1>
      </div></div>
      ${this.understood(r)}
      ${r.fallback && r.results.length ? html`<p class="note">The AI search found nothing close enough, so these are plain keyword matches (AI04).</p>` : ""}
      ${r.results.length === 0
        ? html`<div class="empty"><h3>No products found</h3><p>Neither the AI search nor the keyword search found anything for “${q}”.
            Try other words, a photo, or <a href="#/c/all">see all products</a>.</p></div>`
        : this.results(r)}`);
  }

  /** FR-S4: speech to text in the browser; the customer can correct the text before it is searched. */
  startVoice() {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const box = document.createElement("div");
    box.className = "voice";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-label", "Search by voice");
    mount(box, html`<form class="voice-card">
      <div class="voice-head"><span class="dot ${Recognition ? "on" : ""}"></span><b id="voice-state">${Recognition ? "Listening…" : "Voice input is not available in this browser"}</b>
        <select id="voice-lang" aria-label="Language"><option value="en-US">English</option><option value="vi-VN">Tiếng Việt</option></select></div>
      <p class="small">${Recognition ? "Say what you are looking for, for example “red sneakers under three million”. You can correct the text before searching."
        : "Type your search instead; the AI search treats it the same way."}</p>
      <input id="voice-text" name="q" autocomplete="off" placeholder="Your words appear here" aria-label="Spoken text">
      <div class="voice-actions"><button type="button" class="btn ghost small" id="voice-cancel">Cancel</button>
        <button class="btn accent small" id="voice-go">Search</button></div>
    </form>`);
    document.body.appendChild(box);
    const text = box.querySelector("#voice-text");
    let rec = null;
    const close = () => { if (rec) rec.abort(); box.remove(); };
    const listen = () => {
      if (!Recognition) { text.focus(); return; }
      if (rec) rec.abort();
      rec = new Recognition();
      rec.lang = box.querySelector("#voice-lang").value;
      rec.interimResults = true;
      rec.onresult = (e) => { text.value = Array.from(e.results).map((x) => x[0].transcript).join(" "); };
      rec.onerror = (e) => { box.querySelector("#voice-state").textContent = e.error === "not-allowed" ? "Microphone blocked: type instead" : "Could not hear you: type or try again"; box.querySelector(".dot").classList.remove("on"); };
      rec.onend = () => { box.querySelector(".dot").classList.remove("on"); if (box.querySelector("#voice-state").textContent === "Listening…") box.querySelector("#voice-state").textContent = "Check the text, then search"; };
      box.querySelector(".dot").classList.add("on");
      box.querySelector("#voice-state").textContent = "Listening…";
      try {
        rec.start();
      } catch {   // no microphone or speech service: the text box still works
        box.querySelector("#voice-state").textContent = "Voice input is not available here: type instead";
        box.querySelector(".dot").classList.remove("on");
      }
    };
    box.querySelector("#voice-lang").addEventListener("change", listen);
    box.querySelector("#voice-cancel").addEventListener("click", close);
    box.addEventListener("click", (e) => { if (e.target === box) close(); });
    box.querySelector("form").addEventListener("submit", (e) => {
      e.preventDefault();
      const q = text.value.trim();
      if (!q) { toast("Say or type what you are looking for.", "error"); return; }
      close();
      this.app.go(`search?q=${encodeURIComponent(q)}`);
    });
    listen();
  }

  /** FR-S5: the photo goes to the server once, is compared and dropped there (AI05). */
  async submitPhoto(file) {
    if (!file) return;
    if (!/^image\/(jpeg|png)$/.test(file.type)) { toast("Choose a JPEG or PNG photo.", "error"); return; }
    if (file.size > 5 * 1024 * 1024) { toast("The photo is larger than 5 MB.", "error"); return; }
    mount(this.app.view, loading());
    const form = new FormData();
    form.append("photo", file);
    try {
      const res = await fetch(`${this.controller}/photo`, { method: "POST", body: form, credentials: "same-origin" });
      const r = await res.json();
      if (!res.ok) throw new ApiError(res.status, r);
      if (this.lastPhoto) URL.revokeObjectURL(this.lastPhoto.url);
      this.lastPhoto = { url: URL.createObjectURL(file), name: file.name, result: r };
      if (location.hash === "#/search/photo") this.showPhotoResults(); else this.app.go("search/photo");
    } catch (err) {
      mount(this.app.view, failure(err));
    }
  }

  showPhotoResults() {
    const last = this.lastPhoto;
    if (!last) {
      mount(this.app.view, html`<div class="empty"><h3>Search by photo</h3><p>Use the camera button in the search bar to choose a photo of a product.</p></div>`);
      return;
    }
    const r = last.result;
    mount(this.app.view, html`
      <div class="page-head photo-head">
        <img class="photo-query" src="${last.url}" alt="Your photo">
        <div><p class="eyebrow">Photo search · ${r.results.length} products · ${r.tookMs} ms</p>
          <h1>Products that look like your photo</h1>
          <p class="small">Compared by colour and outline with every product picture. Your photo is not stored.</p></div>
      </div>
      ${r.results.length === 0
        ? html`<div class="empty"><h3>Nothing looks alike</h3><p>No product picture is close enough to this photo. Try a photo with the product in the middle, or search by words.</p></div>`
        : this.results(r)}`);
  }
}
