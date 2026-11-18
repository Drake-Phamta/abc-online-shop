// Password protection for a binary file of the published copy (for example a PDF that a protected page shows).
// Same scheme as protect_page.mjs: AES-256-GCM, key from the password with PBKDF2-SHA256 (400,000 iterations).
// Output layout: "ABCENC01" (8 bytes) | salt (16) | iv (12) | ciphertext with the GCM tag.
// A protected page decrypts it in the browser with the password its gate stored in sessionStorage ("abc-page-pw").
// Usage: node tools/protect_file.mjs <in> <out>   (password in the environment variable ABC_PAGE_PASSWORD)
import { readFileSync, writeFileSync } from "fs";
import { webcrypto as crypto } from "crypto";

const [, , input, output] = process.argv;
const password = process.env.ABC_PAGE_PASSWORD || "";
if (!input || !output || password.length < 8) { console.error("usage: ABC_PAGE_PASSWORD=<8+ chars> node protect_file.mjs <in> <out>"); process.exit(2); }

const ITER = 400000;
const plain = readFileSync(input);
const salt = crypto.getRandomValues(new Uint8Array(16));
const iv = crypto.getRandomValues(new Uint8Array(12));
const base = await crypto.subtle.importKey("raw", new TextEncoder().encode(password), "PBKDF2", false, ["deriveKey"]);
const key = await crypto.subtle.deriveKey({ name: "PBKDF2", hash: "SHA-256", salt, iterations: ITER }, base,
  { name: "AES-GCM", length: 256 }, false, ["encrypt"]);
const data = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, plain));
writeFileSync(output, Buffer.concat([Buffer.from("ABCENC01", "ascii"), Buffer.from(salt), Buffer.from(iv), Buffer.from(data)]));
console.log("protected", output, Math.round(data.length / 1024) + " KB");
