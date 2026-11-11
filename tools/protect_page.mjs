// Password protection for a readable page of the published copy (GitHub Pages serves static files only).
// The page is encrypted with AES-256-GCM, the key derived from the password with PBKDF2-SHA256; the published file
// holds only the ciphertext and a password form, and the browser decrypts it with the Web Crypto API. Used by
// showcase/publish_pages.ps1 for the defence notes; the password never goes into the repository.
// Usage: node tools/protect_page.mjs <page.html> <out.html>   (password in the environment variable ABC_PAGE_PASSWORD)
import { readFileSync, writeFileSync } from "fs";
import { webcrypto as crypto } from "crypto";

const [, , input, output] = process.argv;
const password = process.env.ABC_PAGE_PASSWORD || "";
if (!input || !output || password.length < 8) { console.error("usage: ABC_PAGE_PASSWORD=<8+ chars> node protect_page.mjs <in> <out>"); process.exit(2); }

const ITER = 400000;
const html = readFileSync(input, "utf8")
  .replace(/\s*<a class="vbtn" data-github="[^"]*"[^>]*>[^<]*<\/a>/g, "");   // its source is not published
const salt = crypto.getRandomValues(new Uint8Array(16));
const iv = crypto.getRandomValues(new Uint8Array(12));
const base = await crypto.subtle.importKey("raw", new TextEncoder().encode(password), "PBKDF2", false, ["deriveKey"]);
const key = await crypto.subtle.deriveKey({ name: "PBKDF2", hash: "SHA-256", salt, iterations: ITER }, base,
  { name: "AES-GCM", length: 256 }, false, ["encrypt"]);
const data = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, new TextEncoder().encode(html)));
const b64 = (u) => Buffer.from(u).toString("base64");

const vi = /<html[^>]*lang="vi"/.test(html);
const T = vi
  ? { title: "Trang được bảo vệ", lead: "Trang này cần mật khẩu.", ph: "Mật khẩu", open: "Mở", keep: "Nhớ trên thiết bị này", wrong: "Sai mật khẩu.", back: "Về showcase" }
  : { title: "Protected page", lead: "This page needs a password.", ph: "Password", open: "Open", keep: "Remember on this device", wrong: "Wrong password.", back: "Back to the showcase" };
const css = (html.match(/<link rel="stylesheet" href="[^"]*showcase\.css">/) || [""])[0];
const home = (css.match(/href="([^"]*)showcase\/assets\/showcase\.css"/) || ["", "../../../"])[1] + "showcase/" + (vi ? "index.vi.html" : "index.html");

writeFileSync(output, `<!doctype html>
<html lang="${vi ? "vi" : "en"}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>${T.title}</title>${css}
<style>.gate{max-width:420px;margin:12vh auto;padding:28px;border:1px solid #d8d0c4;border-radius:12px;background:#fffdf9}
.gate input[type=password]{width:100%;box-sizing:border-box;padding:10px 12px;font-size:16px;margin:12px 0;border:1px solid #bbb;border-radius:8px}
.gate button{padding:9px 20px;font-size:15px;border-radius:8px;border:0;background:#1f1c18;color:#fff;cursor:pointer}
.gate .err{color:#b3261e;min-height:1.4em;margin:8px 0 0}.gate label{font-size:14px;margin-left:10px}</style></head>
<body><form class="gate" id="gate"><h2>&#128274; ${T.title}</h2><p>${T.lead}</p>
<input type="password" id="pw" placeholder="${T.ph}" autocomplete="current-password" autofocus>
<button type="submit">${T.open}</button><label><input type="checkbox" id="keep"> ${T.keep}</label>
<p class="err" id="err"></p><p><a href="${home}">${T.back}</a></p></form>
<script>
(() => {
  const P = { salt: "${b64(salt)}", iv: "${b64(iv)}", data: "${b64(data)}", iter: ${ITER} };
  const bytes = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));
  const get = (s, k) => { try { return s.getItem(k); } catch (e) { return null; } };
  const put = (s, k, v) => { try { s.setItem(k, v); } catch (e) { } };
  async function open(pw) {
    const base = await crypto.subtle.importKey("raw", new TextEncoder().encode(pw), "PBKDF2", false, ["deriveKey"]);
    const key = await crypto.subtle.deriveKey({ name: "PBKDF2", hash: "SHA-256", salt: bytes(P.salt), iterations: P.iter },
      base, { name: "AES-GCM", length: 256 }, false, ["decrypt"]);
    const html = new TextDecoder().decode(await crypto.subtle.decrypt({ name: "AES-GCM", iv: bytes(P.iv) }, key, bytes(P.data)));
    const hash = location.hash;
    document.open(); document.write(html); document.close();
    if (hash) setTimeout(() => { const t = document.getElementById(decodeURIComponent(hash.slice(1))); if (t) t.scrollIntoView(); }, 300);
  }
  const saved = get(sessionStorage, "abc-page-pw") || get(localStorage, "abc-page-pw");
  if (saved) open(saved).catch(() => { });
  document.getElementById("gate").addEventListener("submit", async (e) => {
    e.preventDefault();
    const pw = document.getElementById("pw").value;
    try {
      put(sessionStorage, "abc-page-pw", pw);
      if (document.getElementById("keep").checked) put(localStorage, "abc-page-pw", pw);
      await open(pw);
    } catch (err) {
      try { sessionStorage.removeItem("abc-page-pw"); localStorage.removeItem("abc-page-pw"); } catch (e2) { }
      document.getElementById("err").textContent = "${T.wrong}";
    }
  });
})();
</script></body></html>
`);
console.log("protected", output, Math.round(data.length / 1024) + " KB");
