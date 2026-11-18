# DESIGN: data model and class design of the implemented slice

Input: SPEC.md, the analysis class diagram (A10 in `vp/1_Analysis.vpp`, essay Figure 2.1) and the lecturer's
feedback on Product. Output: the data model of `vp/2_DataModel.vpp`, `db/schema.sql` and the packages under
`app/src/main/java/vn/ptit/ecom`, modelled in `vp/3_Design.vpp`.

## 1. Classes and relationships (analysis model A10)

Category (tree) 1 — 0..* Product; BookDetail, LaptopDetail, PhoneDetail, ApparelDetail are subclasses of Product (the
category's detail kind says which one); Customer 1 — 0..* Address; Customer 1 — 0..1 Cart; Cart 1 — 0..* CartItem; CartItem 0..* — 1
Product; Customer 1 — 0..* Order; Order 1 — 1..* OrderItem; OrderItem 0..* — 1 Product; Order 1 — 0..* Payment
(Cash or Credit); Order 1 — 0..1 Shipping; Shipping 0..* — 1 Address; Order 1 — 1..* OrderEvent; Customer is VIP 0..1,
New 0..1; Staff (Sales or Warehouse).

## 2. From the analysis model to the database

The data model is not drawn by hand. In `vp/2_DataModel.vpp` the classes of A10 become the class diagram D1: every
attribute gets a type and a multiplicity (1 = NOT NULL, 0..1 = NULL), every class an identifier and the stereotype
«ORM Persistable», every association end a role name and a multiplicity, and the three generalizations the
inheritance strategy Table per subclass. VP's Synchronize to Entity Relationship Diagram then generates the ERD D2
(20 tables, 122 columns, 22 foreign keys); the only hand edits are the names of the foreign key columns
(`CategoryCategoryId` becomes `CategoryId`, the parent of a category `ParentId`), the table `Order` renamed `Orders`
(ORDER is an SQL keyword) and the layout. Tools > DB > Generate Database (SQLite) writes `db/vp/vp_ddl.sql`.
`db/make_schema.py` copies every CREATE TABLE of that DDL into `db/schema.sql` and adds the rules a data model cannot
hold (34 CHECK, 9 UNIQUE, 5 ON DELETE CASCADE, each marked `-- rule`); `db/compare_schema.py` checks that the two
still have the same tables, columns, types, NOT NULL, keys and foreign keys.

| Analysis class (A10) | Generated table(s) (D2) | Rules added in schema.sql | Reason |
|---|---|---|---|
| Category (tree) | `Category`, `ParentId` to itself | UNIQUE `Slug`; CHECK `DetailKind` in BOOK, LAPTOP, PHONE, APPAREL | the detail kind says which subclass the products of a category have |
| Product and its subclasses BookDetail, LaptopDetail, PhoneDetail, ApparelDetail | `Product` plus one table per subclass; its `ProductId` is both primary key and foreign key to `Product` | UNIQUE `Sku`; CHECK `Price > 0`, `StockQuantity >= 0`, `Status` in ACTIVE, HIDDEN; ON DELETE CASCADE on the four detail tables | lecturer's feedback; Table per subclass keeps one key `ProductId` for CartItem and OrderItem |
| Customer and its subclasses CustomerVIP, CustomerNew | `Customer`, `CustomerVIP`, `CustomerNew`, PK = FK | UNIQUE `Email`; CHECK `DiscountRate` above 0 and at most 0.5 | Table per subclass |
| Address | `Address` with recipient and phone | CHECK `IsDefault` in 0, 1 | delivery needs a receiver |
| Cart, CartItem | `Cart`, `CartItem` | UNIQUE `Cart.CustomerId`; UNIQUE (`CartId`, `ProductId`); CHECK `Quantity > 0`; ON DELETE CASCADE from `Cart` | BR02 |
| Order | `Orders` with status, payment method, subtotal, discount, shipping fee, total | CHECK `TotalAmount = Subtotal - Discount + ShippingFee`; CHECK on the seven states | BR04 stored as a checked fact, BR09 |
| OrderItem | `OrderItem` with `UnitPrice` and the `ProductName` snapshot | UNIQUE (`OrderId`, `ProductId`); CHECK `Quantity > 0`, `UnitPrice > 0` | BR03, 3NF exception explained in the essay |
| OrderEvent | `OrderEvent` | | the history that UC09 shows |
| Payment and its subclasses PayCash, PayCredit | `Payment`, `PayCash`, `PayCredit` (last 4, expiry, provider token) | CHECK `Method`, `Amount > 0`, `Status` | BR07: no column for the card number |
| Shipping | `Shipping` | UNIQUE `OrderId`, UNIQUE `TrackingNumber` | BR10 |
| Staff | `Staff` with role | UNIQUE `Email`; CHECK `Role` in SALES, WAREHOUSE | actors of UC14, UC15 need accounts (UC02), BR13 |

Normalisation: 1NF (atomic columns, repeating groups in own tables), 2NF (single-column keys; the composite UNIQUE
keys are not primary keys), 3NF except two intended historical values (`OrderItem.UnitPrice`,
`OrderItem.ProductName`) and the stored totals of an order, which equal the computed values at checkout and are
guarded by a CHECK.

## 3. Packages and classes (three layers)

The design classes in VP (diagrams G1 to G4b and G8, folder "5 Design" of `vp/3_Design.vpp`) and the code have the
same packages, classes, attributes and operations; `tests/design_vs_code.py` checks this against the compiled classes
and the JS views (80 classes: 72 Java classes with 169 attributes and 134 operations, 8 view classes with 25
operations, and 48 calls of the design sequences G5, G6, G7 and G9), and that no file of the `ai` package imports
another part of the application. `tests/vpgen_vs_code.py` starts from the other side: the 80 files that VP's Instant
Generator wrote from the same model (`docs/evidence/vp_codegen_v5`) must all exist in the code with the same fields
and methods (72 classes, 173 fields, 157 methods, and the 25 operations of the 8 view classes).

| Layer (G1) | Package | Classes | Responsibility |
|---|---|---|---|
| Presentation | `view` (browser, ES modules) | CustomerForm, ProductForm, CartForm, OrderForm, PaymentForm, StaffOrderForm, StockForm, SearchForm | one class per screen group; `show…` renders, `submit…` sends the user's input to its controller |
| Presentation | `controller` | AuthController, ProductController, CartController, OrderController, PaymentController, ShippingController, SearchController, CurrentUser | HTTP only: reads the user from the session (BR08, BR13), parses and checks input, calls one service operation, returns a view record |
| Business logic | `service` | AuthService, CatalogService, CartService, OrderService, PaymentService, ShippingService, SearchService, NotFound | one operation per use case step; owns the transaction (`Database.inTransaction`) and calls the model's rules and the DAOs |
| Business logic | `model.product`, `model.customer`, `model.cart`, `model.order`, `model` | Category, Product and its subclasses BookDetail, LaptopDetail, PhoneDetail, ApparelDetail, DetailKind; Customer, CustomerVIP, CustomerNew, FullName, Address, Account, Role; Cart, CartItem, CartIssue; Order, Totals, OrderItem, OrderEvent, OrderStatus, PaymentMethod, Payment, PayCredit, PayCash, Shipping; RuleViolation | domain rules: Cart (BR01 to BR03), Order.place and Totals (BR04), OrderStatus transition table (BR09) |
| Data access | `dao` | Database, Daos, Work, DataAccessError, ProductDAO, CustomerDAO, StaffDAO, CartDAO, OrderDAO, PaymentDAO, ShippingDAO and one `…DAOImpl` each | JDBC on the SQLite file; every `…DAOImpl` holds the unit of work's `connection`; no business rules |
| Business logic | `ai` (G8) | QueryInterpreter, SearchQuery, ProductIndex, ImageIndex, Document, Hit | the AI search: documents in, ranked hits with reasons out; imports nothing else of the application, so SearchService is the only place that knows products (essay chapter 3, SPEC section 6) |
| Data access | `integration` | CardProvider, SimulatedCardProvider, CardData, Result | gateway to the payment provider (simulated: cards ending 0002 are declined) |

Dependencies point down only: view → controller (HTTP, JSON) → service → dao → SQLite; service → integration →
payment provider; controller, service and dao use the model. A controller never calls a DAO and no SQL exists above
the DAOs. Before the service layer was introduced (commit feab5f3) the controllers opened the transactions
themselves; the move is the answer to "where does the business logic live?" in the defence.

## 4. Key interaction: Place Order with card (design sequences G6 and G7)

1. `OrderForm.submitOrder(addressId, paymentMethod, expectedTotal)` → `POST /api/orders` → `OrderController.placeOrder(req, session)`.
2. The controller takes the customer id from the session (BR08) and calls `OrderService.placeOrder(customerId, addressId, method, expectedTotal)`.
3. The service runs one transaction, `Database.inTransaction(work)`; in it: `CustomerDAO.findById`, `CustomerDAO.address` (BR06), `CartDAO.findOrCreate`, `Order.place(customer, cart, address, method, now)`, which validates the cart (UC21, BR03) and computes the totals (BR04).
4. A changed total against `expectedTotal` → `RuleViolation BR03`, the transaction rolls back and the customer confirms again.
5. `ProductDAO.reserveStock(productId, quantity)` per line: `UPDATE Product SET StockQuantity = StockQuantity - ? WHERE ProductId = ? AND Status = 'ACTIVE' AND StockQuantity >= ?`; 0 rows → `RuleViolation BR05` and rollback (tested by `CheckoutFlowTest.aFailedOrderWriteRollsBackTheStockReservation`).
6. `OrderDAO.insert(order)` (items and the first event), `CartDAO.clear(cart)`, commit. The order is `PENDING_PAYMENT` (card) or `PLACED` (cash on delivery).
7. Card (G7): `PaymentForm.submitPayment(order, card)` → `POST /api/orders/{id}/payments` → `PaymentController.pay` builds `CardData` (format, Luhn and expiry checked) → `PaymentService.pay(orderId, customerId, card)`: transaction 1 loads the order (BR08) and checks it waits for a card payment; `CardProvider.charge(order code, total, card)` runs outside any transaction, so no database lock is held while the provider answers; transaction 2 reloads the order, `Order.recordCardPayment(payment, now)` (PAID only when approved, BR07, BR09), `PaymentDAO.saveAll`, `OrderDAO.saveProgress`.
## 5. Key interaction: AI search by text (design sequence G9)

1. `SearchForm.showResults(q)` → `GET /api/search?q=` → `SearchController.search(q)` (input checked: at most 200 characters, AI06).
2. `SearchService.search(text)` reads the ACTIVE products in one short transaction (`Database.inTransaction`, `ProductDAO.search`) with fresh price and stock.
3. If the catalogue changed since the last index (FR-S7), `ProductIndex.build(documents)` rebuilds the TF-IDF index and its vocabulary; `ImageIndex` is rebuilt the same way for the photo search.
4. `QueryInterpreter.interpret(text)` returns a `SearchQuery`: terms, related words from the lexicon, spelling corrections (Damerau-Levenshtein against the vocabulary) and price limits.
5. `ProductIndex.rank(q, k)` returns `Hit`s with a score and the reasons (the words that contributed most). No hit (AI04): the keyword search of UC04 runs in its place and the result says so.
6. AI07: an out-of-stock product is ranked lower (text search only), then `SearchService.SearchResult(mode, understood, items, fallback, tookMs)` → `SearchView` → the page shows how the query was understood and why each product matched.