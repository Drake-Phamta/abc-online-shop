# -*- coding: utf-8 -*-
"""End-to-end smoke run over HTTP against a freshly seeded server (java -jar ... --abc.db.reset=true).

Walks UC02 -> UC04/05 -> UC06 -> UC07 -> UC08 (declined, then approved) -> UC14 (process, ship, deliver) -> UC09 and
UC15, and checks the key business rules (BR02, BR05, BR08, BR09, BR13). Prints one line per check
and exits non-zero on the first failure. Usage: python tests/smoke_api.py [base_url]
"""
import http.cookiejar
import json
import sqlite3
import sys
import urllib.error
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
DB = sys.argv[2] if len(sys.argv) > 2 else "app/data/abc_shop.db"


class Client:
    def __init__(self):
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def call(self, method, path, body=None):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(BASE + path, data=data, method=method, headers={"Content-Type": "application/json"})
        try:
            with self.opener.open(req) as r:
                return r.status, json.loads(r.read() or b"null")
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"null")


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not ok:
        sys.exit(1)


def stock(product_id):
    with sqlite3.connect(DB) as c:
        return c.execute("SELECT stock_quantity FROM product WHERE product_id = ?", (product_id,)).fetchone()[0]


anon, an, lan, sales, wh = Client(), Client(), Client(), Client(), Client()
s, me = anon.call("GET", "/api/auth/me")
check("UC02 anonymous session", s == 200 and me["loggedIn"] is False)
s, err = an.call("POST", "/api/auth/login", {"email": "an.nguyen@example.com", "password": "wrong"})
check("UC02 A1 wrong password refused", s == 401, err.get("message"))
s, me = an.call("POST", "/api/auth/login", {"email": "an.nguyen@example.com", "password": "demo1234"})
check("UC02 customer login", s == 200 and me["role"] == "CUSTOMER", f"{me.get('name')}, {me.get('kind')}")
lan.call("POST", "/api/auth/login", {"email": "lan.tran@example.com", "password": "demo1234"})
sales.call("POST", "/api/auth/login", {"email": "sales@example.com", "password": "demo1234"})
wh.call("POST", "/api/auth/login", {"email": "warehouse@example.com", "password": "demo1234"})

s, tree = anon.call("GET", "/api/categories")
check("UC04 category tree", s == 200 and len(tree) == 3 and all(r["children"] for r in tree), ", ".join(r["name"] for r in tree))
s, laptops = anon.call("GET", "/api/products?category=laptops")
check("UC04 browse a leaf category", s == 200 and laptops and all(p["categorySlug"] == "laptops" for p in laptops), f"{len(laptops)} laptops")
s, electronics = anon.call("GET", "/api/products?category=electronics")
check("UC04 parent category includes sub-categories", len(electronics) > len(laptops))
s, found = anon.call("GET", "/api/products?q=" + urllib.request.quote(laptops[0]["name"].split()[0]))
check("UC04 keyword search", s == 200 and any(p["id"] == laptops[0]["id"] for p in found))
s, page = anon.call("GET", f"/api/products/{laptops[0]['id']}")
check("UC05 product page with laptop_detail specs", s == 200 and any(x["label"] == "Processor" for x in page["specs"]),
      ", ".join(f"{x['label']}={x['value']}" for x in page["specs"][:3]))

pid = laptops[0]["id"]
s, _ = anon.call("POST", "/api/cart/items", {"productId": pid, "quantity": 1})
check("BR08/UC06 A2 cart needs login", s == 401)
s, err = an.call("POST", "/api/cart/items", {"productId": pid, "quantity": 999})
check("BR02 quantity above stock refused", s == 409 and err["rule"] == "BR02", err["message"])
s, cart = an.call("POST", "/api/cart/items", {"productId": pid, "quantity": 1})
check("UC06 add to cart", s == 200 and cart["count"] == 1)
s, cart = an.call("POST", "/api/cart/items", {"productId": pid, "quantity": 1})
check("BR02 same product merges into one line", len(cart["lines"]) == 1 and cart["lines"][0]["quantity"] == 2)
s, cart = an.call("PUT", f"/api/cart/items/{pid}", {"quantity": 1})
check("UC06 change quantity", cart["lines"][0]["quantity"] == 1)

s, co = an.call("GET", "/api/checkout")
t = co["totals"]
check("BR04 VIP discount and free delivery", t["discount"] == round(t["subtotal"] * 0.05) and t["shippingFee"] == 0,
      f"subtotal {t['subtotal']}, discount {t['discount']}, total {t['total']}")
before = stock(pid)
s, placed = an.call("POST", "/api/orders", {"addressId": co["addresses"][0]["id"], "paymentMethod": "CARD", "expectedTotal": t["total"]})
check("UC07 order placed, waiting for card payment", s == 200 and placed["status"] == "PENDING_PAYMENT", placed.get("code"))
check("BR05 stock reserved at order creation", stock(pid) == before - 1, f"{before} -> {stock(pid)}")
oid = placed["orderId"]
s, cart = an.call("GET", "/api/cart")
check("UC07 cart emptied", cart["count"] == 0)

s, err = lan.call("GET", f"/api/orders/{oid}")
check("BR08 another customer gets 404", s == 404)
s, err = an.call("POST", f"/api/orders/{oid}/payments", {"cardHolder": "NGUYEN VAN AN", "cardNumber": "1234", "expiry": "08/28", "cvv": "123"})
check("UC08 A2 invalid card refused before the provider", s == 400, err["message"])
s, res = an.call("POST", f"/api/orders/{oid}/payments", {"cardHolder": "NGUYEN VAN AN", "cardNumber": "4000 0000 0000 0002", "expiry": "08/28", "cvv": "123"})
check("UC08 A1 declined card keeps the order waiting", s == 200 and not res["approved"] and res["status"] == "PENDING_PAYMENT")
s, res = an.call("POST", f"/api/orders/{oid}/payments", {"cardHolder": "NGUYEN VAN AN", "cardNumber": "4242 4242 4242 4242", "expiry": "08/28", "cvv": "123"})
check("UC08 approved card makes the order PAID (BR07)", res["approved"] and res["status"] == "PAID")
with sqlite3.connect(DB) as c:
    stored = c.execute("SELECT card_last4, provider_token FROM pay_credit pc JOIN payment p ON p.payment_id = pc.payment_id "
                       "WHERE p.order_id = ? ORDER BY p.payment_id", (oid,)).fetchall()
check("BR07 only last four digits and token stored", [r[0] for r in stored] == ["0002", "4242"] and stored[1][1].startswith("tok_"), str(stored))

s, err = an.call("GET", "/api/staff/orders")
check("BR13 customer cannot open the staff board", s == 403)
s, err = sales.call("POST", f"/api/staff/orders/{oid}/ship", {"carrier": "GHN", "trackingNumber": "GHN123"})
check("BR09 cannot ship before processing", s == 409 and err["rule"] == "BR09", err["message"])
s, o = sales.call("POST", f"/api/staff/orders/{oid}/process")
check("UC14 process", o["status"] == "PROCESSING")
s, o = sales.call("POST", f"/api/staff/orders/{oid}/ship", {"carrier": "GHN", "trackingNumber": "GHN-SMOKE-001"})
check("UC14 ship creates the shipment (BR10)", o["status"] == "SHIPPED" and o["shipping"]["trackingNumber"] == "GHN-SMOKE-001")
s, o = sales.call("POST", f"/api/staff/orders/{oid}/deliver")
check("UC14 deliver", o["status"] == "DELIVERED" and o["shipping"]["status"] == "DELIVERED")
s, o = an.call("GET", f"/api/orders/{oid}")
check("UC09 customer sees history", [e["status"] for e in o["events"]] ==
      ["PENDING_PAYMENT", "PENDING_PAYMENT", "PAID", "PROCESSING", "SHIPPED", "DELIVERED"], " > ".join(e["status"] for e in o["events"]))

# cash on delivery, then cancellation by staff returns the stock
s, books = anon.call("GET", "/api/products?category=fiction")
bid = [p for p in books if p["stock"] >= 2][0]["id"]
lan.call("POST", "/api/cart/items", {"productId": bid, "quantity": 2})
s, co = lan.call("GET", "/api/checkout")
b0 = stock(bid)
s, placed = lan.call("POST", "/api/orders", {"addressId": co["addresses"][0]["id"], "paymentMethod": "COD", "expectedTotal": co["totals"]["total"]})
check("UC07 cash on delivery order PLACED", placed["status"] == "PLACED")
s, o = sales.call("POST", f"/api/staff/orders/{placed['orderId']}/cancel")
check("BR05/BR09 staff cancel returns stock", o["status"] == "CANCELLED" and stock(bid) == b0, f"stock {b0} -> {stock(bid)}")

s, rows = wh.call("GET", "/api/staff/stock")
check("UC15 stock list, lowest first", rows[0]["stock"] <= rows[-1]["stock"])
s, err = wh.call("PUT", f"/api/staff/stock/{pid}", {"quantity": -3})
check("BR12 negative stock refused", s == 409 and err["rule"] == "BR12")
s, row = wh.call("PUT", f"/api/staff/stock/{pid}", {"quantity": 25})
check("UC15 stock updated in the database", row["stock"] == 25 and stock(pid) == 25)

# AI search (docs/SPEC.md section 6): guests may search
s, r = anon.call("GET", "/api/search?q=laptop%20under%2010%20million")
check("AT13 AI search price limit is a hard filter", s == 200 and r["results"] and all(f["product"]["price"] <= 10_000_000 for f in r["results"])
      and r["understood"]["maxPrice"] == 10_000_000, ", ".join(f["product"]["name"] for f in r["results"]))
s, r = anon.call("GET", "/api/search?q=xyzzy")
check("AT16 nothing found: keyword fallback, empty", s == 200 and r["fallback"] is True and r["results"] == [])
s, err = anon.call("GET", "/api/search?q=" + "x" * 201)
check("AI06 query longer than 200 characters refused", s == 400, err.get("message"))
print("ALL CHECKS PASSED")
