# -*- coding: utf-8 -*-
# Use case specifications of the five other central use cases of the purchase path, in the form of the UC07 table:
# UC04 with UC05, UC06, UC08, UC09 and UC14. Executed by uc_model.py (section "Use Case Specifications") in the
# namespace of the build script, so p(), table() and nt() are available. Every step, rule and state name below was
# checked against docs/SPEC.md and the code in app/src/main/java/vn/ptit/ecom.

p(f"Table {nt()} specifies UC04 and UC05 together, because a product page is where both a browse and a search end. "
  "It also covers the three ways to search of the AI search (Chapter 3) and the fallback when nothing is found.",
  keep=True)
table("Use case specification UC04 Browse / Search Products with UC05 View Product", [
    ["Item", "Description"],
    ["Use case name", "Browse / Search Products (UC04) and View Product (UC05)"],
    ["Primary actor", "Customer, also a guest who has not logged in"],
    ["Supporting actors", "Speech Recognition Service of the browser, for a spoken query"],
    ["Goal", "Find the products that fit what the customer wants and inspect one of them before buying"],
    ["Trigger", "The customer opens the catalogue or a category, or types or speaks a query or uploads a photo in the header"],
    ["Preconditions", "None: a guest may browse, search and open a product without logging in"],
    ["Postconditions", "Nothing is changed. The customer sees a list of ACTIVE products or the page of one product. A photo and a spoken query are not stored (AI05)"],
    ["Main flow", "1. The customer opens the catalogue, optionally one category, or types a search in the header. 2. Browsing: the system lists the ACTIVE products of the category and of its sub-categories with price and a stock badge, sorted by relevance, price or newest. Searching: the AI search interprets the query, ranks the ACTIVE products and shows how it understood the query and why each product matched. 3. The customer opens a product (UC05). 4. The system shows the common data (name, brand, price, stock state, description) and the attributes of the product's kind (book, laptop, phone or apparel), with a button to add it to the cart (UC06)."],
    ["Alternative flows", "A1 Spoken query: the browser turns speech into text, a dialog shows what it heard and the customer may correct it before the search runs (FR-S4); without speech recognition the dialog is a text box. A2 Photo: the customer uploads a JPEG or PNG image and the system returns at most six products whose pictures look most alike, or says that nothing looks alike (FR-S5). A3 The AI search finds nothing: the keyword search on name, brand and category runs and the page says so (AI04); if that finds nothing too, the page shows an empty state with the query and a link to all products. A4 The product has no stock: it is shown with the badge Out of stock, the Add to cart button is disabled and, in a text search, its relevance counts 20 % less (AI07). A5 The product is hidden or does not exist: the page says that the product does not exist (BR01)."],
    ["Exceptions", "A query longer than 200 characters, a photo above 5 MB or a file that is not a JPEG or PNG image is refused with a message and nothing is searched (AI06); an empty query asks the customer to type something. If the database cannot be read, the customer sees a general error message and nothing else."],
    ["Business rules", "BR01 and AI01: only ACTIVE products are listed or opened. AI02: the page shows how the query was understood and why each result matched. AI03: a price limit in the query is a hard filter. AI04: keyword fallback. AI05: photos and voice are never stored. AI06: text up to 200 characters, photo up to 5 MB, JPEG or PNG. AI07: out-of-stock products rank lower in a text search."],
    ["Priority", "Must Have for browsing, keyword search and the product page (FR04, FR05, FR06, NFR01); the AI search is Should Have (FR-S1 to FR-S3) and Could Have for voice and photo (FR-S4, FR-S5)"],
], [3.2, 12.8], size=10.5)

p(f"Table {nt()} specifies UC06, which fills the cart that UC07 turns into an order. Most of its alternative flows are "
  "refusals, because the cart is where BR01 and BR02 are enforced.", keep=True)
table("Use case specification UC06 Manage Shopping Cart", [
    ["Item", "Description"],
    ["Use case name", "Manage Shopping Cart (UC06)"],
    ["Primary actor", "Customer"],
    ["Supporting actors", "None"],
    ["Goal", "Keep the products the customer wants to buy, with their quantities, until checkout"],
    ["Trigger", "The customer selects Add to cart on a product page, or opens the cart"],
    ["Preconditions", "The customer is logged in with a customer account"],
    ["Postconditions", "The cart is stored with one line per product, each with a quantity from 1 to the stock and the price of the moment the line was added (cart price); the header shows the new number of items"],
    ["Main flow", "1. The customer chooses a product and a quantity and selects Add to cart. 2. The system checks that the product is for sale (BR01), that the quantity is at least 1 and that the quantity in the cart, with this one, does not exceed the stock (BR02). 3. The system adds a line with the current price as cart price, or increases the quantity of the existing line, and saves the cart. 4. The customer opens the cart, changes a quantity or removes a line. 5. The system checks a new quantity against the stock, saves the cart and shows the new subtotal, the sum of quantity times cart price."],
    ["Alternative flows", "A1 The quantity is above the stock: refused with the quantity that is available, and the cart is unchanged (BR02). A2 The customer is not logged in: the system opens the login page (UC02) and returns to the product afterwards. A3 The product is not ACTIVE: refused with the message that it is not for sale (BR01). A4 A new quantity below 1: refused, the customer removes the line instead."],
    ["Exceptions", "The product does not exist: refused with a message. The cart cannot be saved: the transaction is rolled back, the cart is as before and the customer sees a general error message."],
    ["Business rules", "BR01 only ACTIVE products. BR02 one line per product, quantity from 1 to the current stock. BR03 the cart price stays the price shown when the line was added; UC21 compares it with the current price at checkout. BR08 a customer works only on the own cart, and the customer id comes from the session, not from the request."],
    ["Priority", "Must Have (FR07, FR08)"],
], [3.2, 12.8], size=10.5)

p(f"Table {nt()} specifies UC08, the extension of UC07 for card payments. Because the provider is an outside system, "
  "its exceptions say what happens when the answer comes late or is not recorded.", keep=True)
table("Use case specification UC08 Make Payment", [
    ["Item", "Description"],
    ["Use case name", "Make Payment (UC08), an extension of UC07 at the extension point \"card payment chosen\""],
    ["Primary actor", "Customer"],
    ["Supporting actors", "Payment Provider, simulated inside the application: a card number that ends in 0002 is declined and any other valid number is approved"],
    ["Goal", "Pay an order by card and have the provider's result recorded against that order"],
    ["Trigger", "The customer has placed an order with the payment method card, and the checkout opens its payment page; the Pay now button of the order page opens it again later"],
    ["Preconditions", "The customer is logged in; an order of the customer is PENDING_PAYMENT and the stock of its lines is reserved"],
    ["Postconditions", "A payment record holds the result, APPROVED or DECLINED, with the card holder, the last four digits, the expiry and, for an approved card, the provider's token; the order history has an entry for it. The order is PAID after an approved result and stays PENDING_PAYMENT after a declined one. The full card number and the CVV are never stored"],
    ["Main flow", "1. The customer enters the card holder, the card number, the expiry as MM/YY and the CVV and confirms. 2. The system checks the card data: holder, number format and Luhn checksum, expiry date and CVV (A2). 3. The system loads the order, which must be the customer's own (BR08) and PENDING_PAYMENT, and sends its reference and its stored total to the provider; the amount never comes from the request. 4. The provider approves the payment and returns a token. 5. In a second transaction the system loads the order again, records the payment as APPROVED with the last four digits and the token, and sets the order PAID (BR07). 6. The system shows the order, which is now PAID."],
    ["Alternative flows", "A1 The card is declined: the payment is recorded as DECLINED, the order stays PENDING_PAYMENT with its stock reserved, and the page offers another card; the customer may also cancel the order in UC09. A2 The card data is invalid: refused with a message before the provider is called, and nothing is stored. A3 The order is not waiting for a card payment, for example already PAID or CANCELLED: refused (BR07). A4 The order belongs to another customer or does not exist: the answer is not found (BR08)."],
    ["Exceptions", "The order was cancelled while the provider was answering: the second transaction refuses to record the payment (BR07) and the customer sees the refusal. The second transaction fails for another reason: the payment is not recorded, the order stays PENDING_PAYMENT and the customer sees a general error message. When the provider had approved, both cases leave a charge that the shop has not recorded; a real system closes this gap with an outbox table and a reconciliation job (Chapter 6)."],
    ["Business rules", "BR07 an order becomes PAID only after an approved provider result, and only the card holder, the last four digits, the expiry and the token are stored. BR08 own orders only. BR09 the provider's approval is the only actor that moves an order from PENDING_PAYMENT to PAID. BR04 the amount is the total of the stored order."],
    ["Priority", "Must Have (FR14)"],
], [3.2, 12.8], size=10.5)

p(f"Table {nt()} specifies UC09, which gives the customer the data that UC07, UC08 and UC14 produce. Its main alternative "
  "flow is the privacy rule behind FR12: another customer's order is answered as not found.", keep=True)
table("Use case specification UC09 Track Order", [
    ["Item", "Description"],
    ["Use case name", "Track Order (UC09)"],
    ["Primary actor", "Customer"],
    ["Supporting actors", "None"],
    ["Goal", "See the status, the payments and the shipment of the customer's orders without asking the staff"],
    ["Trigger", "The customer opens My orders"],
    ["Preconditions", "The customer is logged in"],
    ["Postconditions", "Nothing is changed, except when the customer cancels an order (A2): the order is CANCELLED, its stock is released and its history has a new entry"],
    ["Main flow", "1. The customer opens My orders. 2. The system lists the customer's orders, newest first, with code, date, first item, status and total. 3. The customer opens one order. 4. The system shows the lines with the prices of checkout, the amounts of BR04, the payment records (method, status, last four digits of a card), the shipment with carrier, tracking number and status once it exists, and the status history with the actor and the time of every change."],
    ["Alternative flows", "A1 The order belongs to another customer or does not exist: the same answer for both, not found (BR08). A2 The customer cancels: the button is offered only while the order is PENDING_PAYMENT or PLACED, and then the order becomes CANCELLED and the system releases its stock; in every other status, including PAID, the button is gone and the server refuses the request (BR09). A3 The customer is not logged in: the system opens the login page (UC02) and returns afterwards."],
    ["Exceptions", "The cancellation cannot be stored: the transaction is rolled back, the order keeps its status and its stock stays reserved, and the customer sees a general error message."],
    ["Business rules", "BR08 customers see only their own orders; the customer id comes from the session. BR09 a customer cancels only along the transition table. BR05 the stock of a cancelled order is released."],
    ["Priority", "Must Have (FR12, FR18); the response time of NFR02 is Should Have"],
], [3.2, 12.8], size=10.5)

p(f"Table {nt()} specifies UC14 together with the shipping data of UC16 that the staff member enters. It carries most of "
  "the order lifecycle (BR09), one transaction for each transition.", keep=True)
table("Use case specification UC14 Process Orders with the shipping data of UC16", [
    ["Item", "Description"],
    ["Use case name", "Process Orders (UC14), with the shipping data exchanged in UC16"],
    ["Primary actor", "Sales Staff"],
    ["Supporting actors", "Shipping Provider (the carrier). In the prototype the staff member enters the carrier and the tracking number and confirms the delivery by hand"],
    ["Goal", "Move each order through packing, shipping and delivery, or cancel it, and keep every change in the order's history"],
    ["Trigger", "A sales staff member opens the order board"],
    ["Preconditions", "The staff member is logged in with the sales role (BR13); orders exist"],
    ["Postconditions", "The order is in its new state and its history has an entry with the new state, the actor and the time. The side effects are stored: a shipment when the order is shipped, a cash payment when a cash-on-delivery order is delivered, and the stock returned with an approved payment marked REFUNDED when an order is cancelled"],
    ["Main flow", "1. The sales staff opens the order board, grouped into To process, Processing, On the way and Closed. 2. The staff selects Start processing on a PLACED or PAID order; the system sets it PROCESSING. 3. When the parcel is ready, the staff selects Ship, chooses the carrier and enters the tracking number (UC16); the system sets the order SHIPPED and creates its one shipment (BR10). 4. When the carrier has delivered, the staff selects Mark delivered; the system sets the order DELIVERED and the shipment delivered and, for cash on delivery, records the cash payment as COMPLETED (BR11). 5. After every step the customer can see the new status and the history in UC09."],
    ["Alternative flows", "A1 Cancel: from PLACED, PAID or PROCESSING the staff may cancel; the system returns the reserved stock and marks an approved card payment REFUNDED (BR05, BR09). A PENDING_PAYMENT order can be cancelled only by its customer. A2 The transition is not allowed from the current status, for example shipping an order that is still PLACED: refused (BR09); the board offers only the allowed actions, so this happens with an out-of-date page or a direct request. A3 Carrier or tracking number missing: refused (BR10). A4 The user is not logged in or has another role: refused, 401 or 403 (BR13)."],
    ["Exceptions", "A tracking number that another shipment already has: the database refuses it, the transaction is rolled back, the order keeps its status and the staff member sees a general error message. Any other failure while a step is stored undoes that step in the same way."],
    ["Business rules", "BR09 the transition table and the actor of each transition. BR10 one shipment per order, unique tracking number, carrier and tracking number required. BR11 cash is recorded when a cash-on-delivery order is delivered. BR05 the stock of a cancelled order is released. BR13 the sales role is required."],
    ["Priority", "Must Have (FR13, FR17, FR18)"],
], [3.2, 12.8], size=10.5)
