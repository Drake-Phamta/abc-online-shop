# SPEC: requirements of the implemented slice

Derived from the essay (Chapter 1 FR/NFR, Chapter 2 use cases UC01 to UC21 and the UC07 specification). This file
specifies only what the application implements; every rule has an id that code and tests cite.

## 1. Scope

| Use case | Actor | FR / NFR | Implemented |
|---|---|---|---|
| UC02 Login | Customer, Sales Staff, Warehouse Staff | FR02, NFR03, NFR04 | yes |
| UC04 Browse / Search Products, with the AI search of section 6 (text, voice, photo) | Customer (also guests) | FR04, FR05, NFR01, FR-S1 to FR-S7 | yes |
| UC05 View Product | Customer (also guests) | FR06 | yes |
| UC06 Manage Shopping Cart | Customer | FR07, FR08 | yes |
| UC07 Place Order / Checkout, includes UC21 Validate Cart | Customer | FR09, FR10, FR11, FR15, FR16, NFR10 | yes |
| UC08 Make Payment | Customer, Payment Provider (simulated) | FR14 | yes |
| UC09 Track Order | Customer | FR12, FR18 | yes |
| UC14 Process Orders (incl. shipping data of UC16) | Sales Staff | FR13, FR17, FR18 | yes |
| UC15 Manage Inventory | Warehouse Staff | FR16 | yes |
| UC01, UC03, UC10 to UC13, UC16 to UC20 | | | specified in the essay only |

The Payment Provider is simulated inside the application (no real card network): card numbers ending in `0002`
are declined, all other valid numbers are approved. The provider returns a token; the shop never stores the full
number (BR07).

## 2. Business rules

| Id | Rule | Enforced in |
|---|---|---|
| BR01 | Only products with status ACTIVE can be added to a cart or ordered. | model + controller |
| BR02 | A cart holds at most one line per product; adding the product again increases the quantity. A line quantity is between 1 and the current stock. | model + DB UNIQUE(cart_id, product_id), CHECK |
| BR03 | A cart line keeps the price shown when it was added (cart price). At checkout every line is validated against the current price, status and stock (UC21). If a price changed, the line takes the current price and the customer must confirm again. | Cart validation |
| BR04 | Order total = subtotal − VIP discount + shipping fee. Subtotal = Σ quantity × unit price. VIP discount = round(subtotal × discount rate). Shipping fee = 30 000 VND, free when the subtotal after discount is at least 500 000 VND. Amounts are integer VND. | Order |
| BR05 | Stock is reserved when the order is created and never becomes negative; it is released when the order is cancelled. | DAO conditional update + DB CHECK |
| BR06 | An order needs a delivery address that belongs to the customer. | controller + FK |
| BR07 | An order is marked PAID only after an approved provider result. The shop stores the card holder, the last four digits, the expiry and the provider token, never the full card number. | Payment |
| BR08 | A customer sees and changes only their own cart and orders. | controllers (session customer id) |
| BR09 | Order status changes only along the transitions of section 3, by the actor named there. | OrderStatus transition table |
| BR10 | One shipment per order, created when the order is shipped (carrier, tracking number, fee). | DB UNIQUE(order_id) |
| BR11 | A cash-on-delivery order gets its cash payment record when it is delivered. | Order lifecycle |
| BR12 | Warehouse staff may set any stock quantity ≥ 0 for an existing product. | controller + DB CHECK |
| BR13 | Staff functions require a staff account with the matching role (SALES for orders, WAREHOUSE for stock). | controllers |

## 3. Order state machine (BR09)

| From | To | Actor / trigger | Side effect |
|---|---|---|---|
| (new) | PENDING_PAYMENT | Customer confirms checkout with card | order + items created, stock reserved, cart emptied |
| (new) | PLACED | Customer confirms checkout with cash on delivery | same |
| PENDING_PAYMENT | PAID | Provider approves the card payment (UC08) | payment APPROVED + pay_credit row |
| PENDING_PAYMENT | PENDING_PAYMENT | Provider declines (UC08 A4) | payment DECLINED row; customer may retry |
| PENDING_PAYMENT | CANCELLED | Customer gives up | stock released |
| PLACED | CANCELLED | Customer or Sales Staff | stock released |
| PLACED, PAID | PROCESSING | Sales Staff | |
| PAID, PROCESSING | CANCELLED | Sales Staff | stock released; an approved payment becomes REFUNDED |
| PROCESSING | SHIPPED | Sales Staff enters carrier and tracking number | shipping row created |
| SHIPPED | DELIVERED | Sales Staff (carrier confirmation) | shipping DELIVERED; COD: payment COMPLETED + pay_cash row |

Change from the essay's UC07 text: the order is now created **before** the payment (state PENDING_PAYMENT) because
FR14 records the provider result "against the correct order", which needs an existing order reference, and stock
must be held while the customer pays. The order still becomes PAID only after approval (BR07), as UC07 requires.

## 4. Use case specifications

### UC02 Login
Main flow: 1. User enters email and password. 2. System checks the account (customer or staff) and the password
hash. 3. System starts a session with the user's id and role and opens the role's start page.
Alternative: A1 wrong email or password: generic message, no hint which one was wrong.

### UC04 Browse / Search Products, UC05 View Product
Main flow: 1. Customer opens the catalogue, optionally a category (a parent category shows its sub-categories'
products), or types a search in the header. 2. Browsing: System lists the ACTIVE products of the category with
price and availability, sorted by relevance, price or newest. Searching: the AI search of section 6 interprets the
query, ranks the ACTIVE products and shows how it understood the query and why each result matched. 3. Customer
opens a product. 4. System shows the common data (name, brand, price, stock state, description) and the attributes
of the product's detail kind (book, laptop, phone, apparel).
Kinds of search (diagram AI1: the abstract use case Search Products is specialized by Search by Text, Search by
Voice and Search by Photo; every kind includes Rank and Explain Results, text and voice also include Interpret
Query): by text as in step 2; by voice, the browser turns speech into text, the customer can correct the text, then
the search runs as by text; by photo, the customer uploads a photo and System ranks the products whose images look
most alike. Alternative: A1 nothing found after a typed or spoken query (AI04, Fall Back to Keyword Search extends
Search Products at "nothing found"): keyword search on name, brand and category; if that is empty too, an empty
state with the query and a link back to all products.

### UC06 Manage Shopping Cart
Main flow: 1. Customer adds a product with a quantity. 2. System checks BR01, BR02 and stock, adds or merges the line
with the current price as cart price. 3. Customer changes a quantity or removes a line. 4. System recalculates the
subtotal.
Alternatives: A1 quantity above stock: refused with the available quantity. A2 not logged in: asked to log in, then
returned to the product.

### UC07 Place Order / Checkout, UC21 Validate Cart
Main flow: 1. Customer opens checkout. 2. System validates the cart (UC21, BR03). 3. Customer chooses a delivery
address and a payment method (card or cash on delivery). 4. System shows subtotal, VIP discount, shipping fee and
total (BR04). 5. Customer confirms. 6. System, in one transaction, re-validates the cart, creates the order and its
lines with the unit prices, reserves stock (BR05) and empties the cart. 7. Cash on delivery: order PLACED,
confirmation shown. Card: UC08 runs.
Alternatives: A1 product unavailable or not enough stock: confirmation blocked, line marked, cart unchanged. A2 no
or foreign address: refused (BR06). A3 price changed since the cart: lines updated, customer must confirm the new
total.

### UC08 Make Payment
Main flow: 1. Customer enters card holder, number, expiry and CVV for a PENDING_PAYMENT order of their own. 2. System
sends the amount and the order reference to the provider. 3. Provider approves and returns a token. 4. System
records the payment (APPROVED, last four digits, token) and sets the order PAID.
Alternatives: A1 declined: payment recorded as DECLINED, order stays PENDING_PAYMENT, customer may retry or cancel.
A2 invalid card data (format, expired): refused before calling the provider.

### UC09 Track Order
Main flow: 1. Customer opens "My orders". 2. System lists the customer's orders, newest first. 3. Customer opens one.
4. System shows lines, totals, payment records, shipment (carrier, tracking number) and the status history.
Alternative: A1 the order belongs to someone else: "not found" (BR08), same as a missing order.

### UC14 Process Orders
Main flow: 1. Sales Staff opens the order board grouped by status. 2. Staff moves an order along BR09 (process,
ship with carrier and tracking number, deliver, cancel). 3. System applies the side effects of section 3.
Alternative: A1 transition not allowed from the current status: refused with the allowed actions.

### UC15 Manage Inventory
Main flow: 1. Warehouse Staff opens the stock list (low stock first). 2. Staff sets a new quantity. 3. System stores it
(BR12).
Alternative: A1 negative or non-numeric quantity: refused.

## 5. Acceptance tests (behaviour)

| Id | Given | When | Then | Rule |
|---|---|---|---|---|
| AT01 | product with stock 2 | customer adds 3 | refused, cart unchanged | BR02 |
| AT02 | cart line added at 1 000 000, price now 900 000 | checkout validation | line price 900 000, "price changed" flag | BR03 |
| AT03 | VIP 5 %, subtotal 1 000 000 | totals | discount 50 000, shipping 0, total 950 000 | BR04 |
| AT04 | stock 1, two orders for 1 | second checkout | refused, stock stays 0 | BR05 |
| AT05 | card ending 0002 | pay | DECLINED, order still PENDING_PAYMENT; retry with valid card → PAID | BR07 |
| AT06 | order of customer B | customer A requests it | 404 | BR08 |
| AT07 | order PLACED | staff ships it directly | refused (must be PROCESSING) | BR09 |
| AT08 | COD order SHIPPED | staff delivers | DELIVERED, cash payment recorded | BR11 |
| AT09 | order PAID with stock reserved | staff cancels | CANCELLED, stock released, payment REFUNDED | BR05, BR09 |
| AT10 | customer session | calls staff endpoint | 403 | BR13 |
| AT11 | catalogue of the demo data | search "red sneakers" | Converse Chuck Taylor (red canvas shoes) first; "sneakers" understood as shoes | AI02 |
| AT12 | same | search "macbok air" | Apple MacBook Air first; the page shows the correction macbok → macbook | AI02 |
| AT13 | same | search "laptop under 10 million" | only laptops priced at most 10 000 000 ₫ (ThinkPad T470, Latitude 5480) | AI03 |
| AT14 | same | search "book for a programmer" | Clean Code and The Pragmatic Programmer in the first three | AI02 |
| AT15 | photo of a catalogue product, cropped, darker and on another background | search by photo | that product first | FR-S5 |
| AT16 | same | search "xyzzy" | AI search and keyword search find nothing; empty state says so | AI04 |
| AT17 | a text file sent as photo | search by photo | 400 "not a JPEG or PNG image", nothing stored | AI05, AI06 |

## 6. AI search (Chapter 3): specification of the AI component

Built from the lecturer's notes "Integrating AI into E-Commerce Systems": business problem, requirements, AI and
data requirements, then the component, its interactions, failures, risks and evaluation.

| Item | ABC Online Shop |
|---|---|
| Business problem | Customers who do not type the exact product name find nothing: the keyword search matches substrings of name, brand and category only. "red sneakers", "macbok", "laptop under 10 million" or a photo of a shoe return no product, so a customer who wants to buy leaves. Chapter 1 asks for more: stakeholder need SN02 "browse and search the catalogue efficiently" and FR05 (Must) "let customers search the product catalogue". |
| Business objective | More searches that end at a product page or in the cart (search success rate), fewer searches without result. |
| Business requirement | The shop helps customers find the right product in one search, whether they type, speak or show a photo. |
| Functional requirements | FR-S1 interpret a free-text query: synonyms and related words, spelling mistakes, price limits; FR-S2 rank the ACTIVE products by relevance; FR-S3 show how the query was understood and why each result matched; FR-S4 accept a spoken query (speech to text in the browser, editable before it is sent); FR-S5 accept a photo and return the products whose pictures look most alike; FR-S6 fall back to keyword search when the AI search finds nothing; FR-S7 keep the index in step with the catalogue (built from the database at start). |
| AI function | Ranking: for a query q and every product p, a relevance score s(q, p); the result is the top k products. Text: a vector space model whose term weights (TF-IDF) are learned from the catalogue text, with query expansion. Photo: a feature vector of colour and shape per image, cosine similarity. |
| Input | text up to 200 characters, or one JPEG or PNG image up to 5 MB |
| Output | up to 12 products, each with a score and its reasons; the understood query (terms, expansions, corrections, price limits); a flag when the fallback was used |
| Data source | product (name, brand, description, price, status), category (name and parent), book_detail, laptop_detail, phone_detail, apparel_detail (all values), product images in the shop's image folder; nothing new is stored |
| Location | AI component in the business logic layer (package `ai`), called by the SearchService; no external service |
| Interaction | SearchForm (view) → SearchController → SearchService → QueryInterpreter, ProductIndex, ImageIndex; SearchService reads the catalogue through ProductDAO |
| Performance | text search under 300 ms, photo search under 1 s on the demo machine; hit@1 and MRR better than the keyword search on the labelled queries (section 6.2) |
| Update | the index is built from the database when the first search runs and rebuilt after a catalogue change |
| Human role | sales staff keep the list of related words (the lexicon in QueryInterpreter) and check the labelled queries before a change goes live |
| Risks | wrong or missing results; unfair ranking (a brand always first); photos of people; very long or crafted input; see 6.3 |
| Evaluation | technical: hit@1, recall@5, MRR, zero-result rate, photo top-1 and top-3 accuracy, latency; business: search success rate and conversion after search (needs live traffic, planned) |

### 6.1 Rules of the AI search

| Id | Rule |
|---|---|
| AI01 | Only ACTIVE products are indexed and returned (BR01). |
| AI02 | The result page shows how the query was understood (expanded words, corrections, price limit) and every result shows why it matched (explainability). |
| AI03 | A price limit in the query ("under 10 million", "below 500k") is a hard filter: no result above it. |
| AI04 | When the AI search finds nothing, the keyword search runs; the page says which search produced the results. |
| AI05 | Photos and voice are processed in memory and never stored; search texts are not logged with the customer. |
| AI06 | Input limits: text up to 200 characters, photo up to 5 MB, JPEG or PNG only. |
| AI07 | In a text search, a product out of stock is still shown, with its stock badge, but its relevance counts 20 % less: it stays in front only when it is clearly more relevant than the products that can be bought now. A photo shows one product, so the photo search keeps it in its place (the customer learns that it is out of stock). |

### 6.2 Evaluation protocol

`tests/search_eval.py` runs against a fresh server: 30 labelled queries (`tests/search/queries.json`, each with the
SKUs that a shop assistant would show) through the keyword search and the AI search, and 84 photos made from the
catalogue images (crop, rotation, lighting, other background; `tests/search/make_photos.py`) through the photo
search. Output in `docs/evidence/search_eval.txt`.

### 6.3 Failure and risk analysis

| Failure or risk | Effect | Response in the design |
|---|---|---|
| Query uses words that are not in the catalogue | no result | lexicon expansion, spelling correction, then keyword fallback (AI04) |
| Low-quality or unrelated photo | unrelated products shown | the page shows the similarity score; results under the threshold are not shown |
| Browser has no speech recognition (or no network for it) | voice button cannot listen | the dialog says so and keeps the text box; typing works |
| Catalogue changed | stale results | index rebuilt after a change; prices and stock of results are read fresh from the database |
| Unfair ranking | some products never seen | ranking uses query terms only, no brand boost; the labelled queries check other brands |
| Privacy of photos | personal data in photos | processed in memory, not stored, not logged (AI05) |
| Oversized or crafted input | slow search, errors | limits of AI06, the file type is checked before decoding |
