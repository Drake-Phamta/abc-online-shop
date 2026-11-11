// Shared script of the showcase (index.html in English, index.vi.html in Vietnamese) and of the file viewer pages in
// showcase/pages (made by build_pages.py). Without this script every link still works; it only makes them friendlier:
// - a document or source file opens as a readable page (Markdown rendered, code with line numbers);
// - a picture opens in a lightbox with previous / next, fit or actual size;
// - on this computer (file://) "Show in File Explorer" and "Open in Visual Paradigm" use the link type abcshop:,
//   which CHAY_DEMO.bat registers (showcase/abcshop.ps1);
// - "Open the shop" opens the demo shop, and starts it first through CHAY_DEMO.bat when it is not running.
(() => {
  "use strict";
  const ROOT = new URL("../../", document.currentScript.src); // the project folder
  const LOCAL = location.protocol === "file:";
  const PAGES = window.ABC_PAGES || {};
  const SHOP = "http://localhost:8080/";
  const INDEX = !!document.querySelector("nav.side");
  document.documentElement.classList.toggle("local", LOCAL);

  // ------------------------------------------------------------------ language
  const store = (key, value) => {
    try { if (value === undefined) return localStorage.getItem(key); localStorage.setItem(key, value); } catch (e) { /* no storage */ }
    return null;
  };
  let LANG = "en";
  if (INDEX) { LANG = document.documentElement.lang === "vi" ? "vi" : "en"; store("abc-lang", LANG); }
  else if (store("abc-lang") === "vi") LANG = "vi";
  const T = {
    en: {
      back: "← Showcase", reveal: "Show in File Explorer", raw: "Original file", openVP: "Open in Visual Paradigm",
      github: "View on GitHub", name: "Name", size: "Size", files: "files", lines: "lines",
      localOnly: "Only in the author's local copy: the course material, the archive, personal notes and the docx are not published.",
      actual: "Actual size", fit: "Fit to window", close: "Close (Esc)", prev: "‹ Previous", next: "Next ›",
      asking: "If the browser asks, choose <b>Open</b>. If nothing happens, run <b>CHAY_DEMO.bat</b> once: it teaches this computer these links.",
      revealing: "<b>Opening File Explorer</b> at this file.", openingVP: "<b>Opening the project in Visual Paradigm.</b>",
      shopUpTitle: "The shop is running: open it", shopDownTitle: "The shop is not running: click to start it (about 15 seconds)",
      shopStarting: "<b>Starting the shop</b> on a fresh demo database, about 15 seconds. It opens in the browser when it is ready. If the browser asks, choose <b>Open</b>. If no window <i>ABC Online Shop - demo server</i> appears, double-click <b>CHAY_DEMO.bat</b> in the project folder.",
      shopReady: "<b>The shop is running.</b> The browser opens it now; if it does not, <a href=\"" + SHOP + "\" target=\"_blank\" rel=\"noopener\">open it here ↗</a>",
      shopFailed: "<b>The shop did not start.</b> Double-click <b>CHAY_DEMO.bat</b> in the project folder; its window shows the reason.",
      shopRemote: "The live shop is offline right now: the presenter's computer publishes it through a tunnel during the defence period. To run it yourself, download the project and double-click <b>CHAY_DEMO.bat</b> (Java 17).",
      shopOffline: "The live shop is offline right now",
    },
    vi: {
      back: "← Trang trình bày", reveal: "Mở trong File Explorer", raw: "File gốc", openVP: "Mở bằng Visual Paradigm",
      github: "Xem trên GitHub", name: "Tên", size: "Kích thước", files: "file", lines: "dòng",
      localOnly: "Chỉ có trên máy của tác giả: tài liệu môn học, thư mục lưu trữ, ghi chú cá nhân và file docx không được đăng công khai.",
      actual: "Kích thước thật", fit: "Vừa khung", close: "Đóng (Esc)", prev: "‹ Trước", next: "Sau ›",
      asking: "Nếu trình duyệt hỏi, chọn <b>Open</b> (Mở). Nếu không có gì xảy ra, chạy <b>CHAY_DEMO.bat</b> một lần để máy nhận loại link này.",
      revealing: "<b>Đang mở File Explorer</b> tại file này.", openingVP: "<b>Đang mở project bằng Visual Paradigm.</b>",
      shopUpTitle: "Shop đang chạy: bấm để mở", shopDownTitle: "Shop chưa chạy: bấm để khởi động (khoảng 15 giây)",
      shopStarting: "<b>Đang khởi động shop</b> với dữ liệu demo mới, khoảng 15 giây. Trình duyệt sẽ tự mở shop khi sẵn sàng. Nếu trình duyệt hỏi, chọn <b>Open</b> (Mở). Nếu không thấy cửa sổ <i>ABC Online Shop - demo server</i>, bấm đúp <b>CHAY_DEMO.bat</b> trong thư mục dự án.",
      shopReady: "<b>Shop đã chạy.</b> Trình duyệt đang mở shop; nếu chưa thấy, <a href=\"" + SHOP + "\" target=\"_blank\" rel=\"noopener\">mở tại đây ↗</a>",
      shopFailed: "<b>Shop chưa khởi động được.</b> Bấm đúp <b>CHAY_DEMO.bat</b> trong thư mục dự án; cửa sổ của nó ghi rõ lý do.",
      shopRemote: "Shop trực tuyến đang tạm tắt: máy của người trình bày đưa shop lên qua tunnel trong thời gian bảo vệ. Muốn tự chạy, tải dự án về rồi bấm đúp <b>CHAY_DEMO.bat</b> (Java 17).",
      shopOffline: "Shop trực tuyến đang tạm tắt",
    },
  };
  const t = (key) => T[LANG][key];
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = (el.dataset.num ? el.dataset.num + " " : "") + t(el.dataset.i18n);
  });

  // ------------------------------------------------------------------ toast
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.setAttribute("role", "status");
  toast.setAttribute("aria-live", "polite");
  toast.hidden = true;
  document.body.append(toast);
  let toastTimer = 0;
  function say(htmlText, ms) {
    toast.innerHTML = htmlText;
    toast.hidden = false;
    clearTimeout(toastTimer);
    if (ms) toastTimer = setTimeout(() => { toast.hidden = true; }, ms);
  }

  // ------------------------------------------------------------------ paths
  function repoPath(url) {
    if (url.protocol !== ROOT.protocol || url.host !== ROOT.host) return null;
    const root = decodeURIComponent(ROOT.pathname), path = decodeURIComponent(url.pathname);
    if (!path.startsWith(root)) return null;
    return path.slice(root.length).replace(/\/$/, "");
  }
  const encodePath = (path) => path.split("/").map(encodeURIComponent).join("/");
  const viewerUrl = (path) => new URL("showcase/pages/" + encodePath(path) + (PAGES[path] === "d" ? "/index.html" : ".html"), ROOT).href;
  // a document opens in the reader's language when it has a Vietnamese twin (X.md -> X.vi.md)
  const inLanguage = (path) => {
    const vi = path.replace(/\.md$/, ".vi.md");
    return LANG === "vi" && /\.md$/.test(path) && !/\.vi\.md$/.test(path) && PAGES[vi] ? vi : path;
  };
  // published copy on GitHub Pages (<owner>.github.io/<repo>/): the same file on github.com, which renders it
  const GITHUB = /\.github\.io$/.test(location.hostname)
    ? "https://github.com/" + location.hostname.split(".")[0] + "/" + ROOT.pathname.split("/").filter(Boolean)[0] : null;
  const githubUrl = (path, folder) => GITHUB + (folder ? "/tree/main/" : "/blob/main/") + encodePath(path);
  // not published: the lecturer's material, the archive, the docx
  const LOCAL_ONLY = /^(De_bai|Luu_tru)(\/|$)|\.docx$|^docs\/CONTROL(\.vi)?\.md$/i;
  function launch(action, path) {
    location.href = "abcshop:" + action + (path ? "?p=" + encodeURIComponent(path) : "");
  }
  function reveal(path) { launch("reveal", path); say(t("revealing") + " " + t("asking"), 9000); }

  // ------------------------------------------------------------------ lightbox for pictures
  const IMAGE = /\.(png|jpe?g|gif|svg|webp)$/i;
  const gallery = [];
  let current = 0, lb = null;
  function buildLightbox() {
    lb = document.createElement("dialog");
    lb.className = "lb";
    lb.innerHTML = `<div class="bar"><div class="title"><span class="name"></span><small class="path"></small></div>
      <div class="row"><span class="count"></span>
      <button type="button" data-k="prev">${t("prev")}</button><button type="button" data-k="next">${t("next")}</button>
      <button type="button" data-k="size">${t("actual")}</button>
      <button type="button" data-k="reveal" class="local-only">${t("reveal")}</button>
      <a data-k="raw" target="_blank" rel="noopener">${t("raw")}</a>
      <button type="button" data-k="close">${t("close")}</button></div></div>
      <div class="body"><img alt=""></div>`;
    document.body.append(lb);
    const $ = (k) => lb.querySelector(`[data-k="${k}"]`);
    $("prev").addEventListener("click", () => show(current - 1));
    $("next").addEventListener("click", () => show(current + 1));
    $("size").addEventListener("click", () => {
      $("size").textContent = lb.classList.toggle("actual") ? t("fit") : t("actual");
    });
    $("reveal").addEventListener("click", () => reveal(gallery[current].path));
    $("raw").textContent = t("github");
    $("raw").hidden = !GITHUB;   // locally: fit / actual size and File Explorer; no raw picture on a black page
    $("close").addEventListener("click", () => lb.close());
    lb.addEventListener("click", (e) => { if (e.target === lb) lb.close(); });
    lb.addEventListener("keydown", (e) => {
      if (e.key === "ArrowLeft") { e.preventDefault(); show(current - 1); }
      if (e.key === "ArrowRight") { e.preventDefault(); show(current + 1); }
    });
  }
  function show(i) {
    if (!lb) buildLightbox();
    current = (i + gallery.length) % gallery.length;
    const item = gallery[current];
    lb.querySelector("img").src = item.href;
    lb.querySelector("img").alt = item.name;
    lb.querySelector(".name").textContent = item.name;
    lb.querySelector(".path").textContent = item.path;
    lb.querySelector(".count").textContent = gallery.length > 1 ? `${current + 1} / ${gallery.length}` : "";
    if (GITHUB) lb.querySelector('[data-k="raw"]').href = githubUrl(item.path);
    lb.querySelectorAll('[data-k="prev"], [data-k="next"]').forEach((b) => { b.hidden = gallery.length < 2; });
    lb.querySelector(".body").scrollTo(0, 0);
    if (!lb.open) lb.showModal();
  }
  function pictureName(a, path) {
    const img = a.querySelector("img");
    const text = (a.textContent || "").trim();
    const label = text && text.length < 90 ? text : (img && img.alt) || "";
    const file = path.split("/").pop();
    return label && label !== file ? `${label} · ${file}` : file;
  }

  // ------------------------------------------------------------------ links
  document.querySelectorAll("a[href]").forEach((a) => {
    if (a.hasAttribute("data-raw") || a.hasAttribute("data-shop") || a.closest(".lang, .vbar .vback")) return;
    const href = a.getAttribute("href");
    if (!href || href.startsWith("#") || /^(mailto|abcshop|javascript):/i.test(href)) return;
    const url = new URL(href, location.href);
    const path = repoPath(url);
    if (path === null || path.startsWith("showcase/pages/")) return;
    if (LOCAL_ONLY.test(path)) {
      a.addEventListener("click", (e) => { e.preventDefault(); if (LOCAL) reveal(path); else say(t("localOnly"), 7000); });
    } else if (IMAGE.test(path)) {
      let index = gallery.findIndex((g) => g.path === path);
      if (index < 0) { index = gallery.push({ path, href: url.href, name: pictureName(a, path) }) - 1; }
      a.addEventListener("click", (e) => { if (e.ctrlKey || e.metaKey || e.shiftKey) return; e.preventDefault(); show(index); });
    } else if (PAGES[path]) {
      a.href = viewerUrl(inLanguage(path)) + url.hash;
    } else if (/\.vpp$/i.test(path) && LOCAL) {
      a.title = t("openVP");
      a.addEventListener("click", (e) => { e.preventDefault(); launch("open", path); say(t("openingVP") + " " + t("asking"), 9000); });
    } else if (/\.(db|docx|zip|jar)$/i.test(path) && LOCAL) {
      a.title = t("reveal");
      a.addEventListener("click", (e) => { e.preventDefault(); reveal(path); });
    }
  });
  document.querySelectorAll("[data-reveal]").forEach((b) => b.addEventListener("click", () => reveal(b.dataset.reveal)));
  document.querySelectorAll("[data-github]").forEach((a) => {
    if (!GITHUB) return;
    a.href = githubUrl(a.dataset.github, PAGES[a.dataset.github] === "d") + (/^#L\d+/.test(location.hash) ? location.hash.replace(/-L?/, "-L") : "");
    a.target = "_blank";
    a.rel = "noopener";
    a.hidden = false;
  });
  // the EN / VI switch of a document remembers the language for the next pages
  document.querySelectorAll(".vlang a").forEach((a) => a.addEventListener("click", () => {
    store("abc-lang", a.getAttribute("lang") === "vi" ? "vi" : "en");
    a.href = a.getAttribute("href").split("#")[0] + location.hash;
  }));

  // ------------------------------------------------------------------ viewer pages: back link, marked lines
  const back = document.querySelector(".vbar .vback");
  if (back) {
    if (LANG === "vi") back.href = back.href.replace(/index\.html$/, "index.vi.html");
    back.addEventListener("click", (e) => {
      if (document.referrer && /\/showcase\/(index(\.vi)?\.html)?([?#].*)?$/.test(document.referrer) && history.length > 1) { e.preventDefault(); history.back(); }
    });
  }
  function markLines() {
    document.querySelectorAll(".code .ln.hl").forEach((l) => l.classList.remove("hl"));
    const m = location.hash.match(/^#L(\d+)(?:-L?(\d+))?$/);
    if (!m) return;
    const from = +m[1], to = Math.max(from, +(m[2] || m[1]));
    for (let i = from; i <= to; i++) { const l = document.getElementById("L" + i); if (l) l.classList.add("hl"); }
    const first = document.getElementById("L" + from);
    if (first) first.scrollIntoView({ block: "center" });
  }
  if (document.querySelector(".code")) { markLines(); window.addEventListener("hashchange", markLines); }

  // ------------------------------------------------------------------ showcase: language switch, section in view
  document.querySelectorAll(".lang a").forEach((a) => a.addEventListener("click", () => {
    store("abc-lang", /index\.vi\.html$/.test(a.getAttribute("href")) ? "vi" : "en");
    a.href = a.getAttribute("href").split("#")[0] + location.hash;
  }));
  const sections = [...document.querySelectorAll("nav.side > a")];
  if (sections.length && "IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => entries.forEach((en) => {
      if (en.isIntersecting) sections.forEach((l) => l.classList.toggle("on", l.getAttribute("href") === "#" + en.target.id));
    }), { rootMargin: "-40% 0px -55% 0px" });
    document.querySelectorAll("main section").forEach((s) => io.observe(s));
  }

  // ------------------------------------------------------------------ "Open the shop"
  const shopLinks = [...document.querySelectorAll("a[data-shop]")];
  if (!shopLinks.length) return;
  if (!LOCAL) {
    // published copy: the presenter's computer publishes the running shop through a Cloudflare quick tunnel and writes
    // its current address into the "Website" field of the repository (tools/quick_tunnel.ps1); the links open it
    // (also into live.txt of the branch "live", read through raw.githubusercontent.com when the API is out of its
    // hourly limit of 60 calls per network). The last address that worked is remembered in this browser and tried first.
    let live = null, liveUp = false;
    shopLinks.forEach((a) => a.addEventListener("click", (e) => { if (live && liveUp) return; e.preventDefault(); say(t("shopRemote"), 9000); }));
    const TUNNEL = /^https:\/\/[a-z0-9-]+\.trycloudflare\.com\/?$/;
    // a product photo must load: an error page of a stopped tunnel does not count as the shop
    const alive = (u) => new Promise((ok) => {
      const img = new Image(), timer = setTimeout(() => ok(false), 9000);
      img.onload = () => { clearTimeout(timer); ok(true); };
      img.onerror = () => { clearTimeout(timer); ok(false); };
      img.src = u + "img/products/el-phn-003.jpg?t=" + Date.now();
    });
    const sources = [
      async () => { try { return localStorage.getItem("abc-live-shop") || ""; } catch (e) { return ""; } },
      async () => (await (await fetch(GITHUB.replace("https://github.com/", "https://api.github.com/repos/"), { cache: "no-store" })).json()).homepage || "",
      async () => (await (await fetch(GITHUB.replace("https://github.com/", "https://raw.githubusercontent.com/") + "/live/live.txt?t=" + Date.now(), { cache: "no-store" })).text()).trim(),
    ];
    (async () => {
      const tried = new Set();
      for (const source of sources) {
        let home = "";
        try { home = await source(); } catch (e) { /* API limit or no live branch: next source */ }
        if (!TUNNEL.test(home)) continue;
        home = home.replace(/\/?$/, "/");
        if (tried.has(home)) continue;
        tried.add(home);
        if (await alive(home)) { live = home; liveUp = true; break; }
      }
      try { if (liveUp) localStorage.setItem("abc-live-shop", live); } catch (e) { }
      shopLinks.forEach((a) => {
        a.dataset.state = liveUp ? "up" : "down";
        a.title = liveUp ? t("shopUpTitle") : t("shopOffline");
        if (liveUp) { a.href = live; a.target = "_blank"; a.rel = "noopener"; }
      });
    })();
    return;
  }
  let shopUp = false, startedAt = 0;
  async function shopAnswers() {
    const ctl = new AbortController(), timer = setTimeout(() => ctl.abort(), 1500);
    try { await fetch(SHOP, { mode: "no-cors", cache: "no-store", signal: ctl.signal }); return true; }
    catch (e) { return false; }
    finally { clearTimeout(timer); }
  }
  async function checkShop() {
    shopUp = await shopAnswers();
    shopLinks.forEach((a) => { a.dataset.state = shopUp ? "up" : "down"; a.title = shopUp ? t("shopUpTitle") : t("shopDownTitle"); });
    if (!startedAt) return;
    if (shopUp) { startedAt = 0; say(t("shopReady"), 8000); }
    else if (Date.now() - startedAt > 90000) { startedAt = 0; say(t("shopFailed")); }
  }
  shopLinks.forEach((a) => {
    a.addEventListener("pointerenter", checkShop);
    a.addEventListener("click", (e) => {
      if (shopUp) return;
      e.preventDefault();
      if (!startedAt) { startedAt = Date.now(); launch("start"); }
      say(t("shopStarting"));
    });
  });
  (function loop() { checkShop().finally(() => setTimeout(loop, startedAt ? 1500 : 4000)); })();
  document.addEventListener("visibilitychange", () => { if (!document.hidden) checkShop(); });
})();
