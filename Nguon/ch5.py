# -*- coding: utf-8 -*-
# CHAPTER 5. CODE (V4): the ABC Online Shop application (Java 17, Spring Boot, SQLite) that implements the design of
# Chapter 4, including the AI search of Chapter 3 (Section 5.12).
# The design diagrams G0, G1 and G6 are shown in Chapter 4 (F_G0, F_G1, F_G6 are set there) and only referred to here.

chapter("Code")
p("A program is the hardest test of a design: a diagram can be inconsistent without anyone noticing, but code runs "
  "or it does not, and a test passes or fails. I built one application, the ABC Online Shop, that implements the "
  "layered design of Chapter 4 on the database of the physical model, in about 3,000 lines of Java and 1,000 lines "
  "of JavaScript. Sections 5.1 to 5.7 follow the layers from the database to the screens, Section 5.8 shows the "
  "running system, Sections 5.9 to 5.11 show how code, design and tests are kept consistent, Section 5.12 shows the "
  "AI search of Chapter 3 in the code, and Section 5.13 states what is missing.")

# ------------------------------------------------------------------------------------------------ 5.1
h2("5.1. Implementation Strategy and Environment")
p("I did not implement all 21 use cases but one vertical slice, the purchase chain, because a slice that crosses "
  "every layer tests the architecture: when a customer can find a product, fill a cart, place an order and pay, and "
  "staff can ship the order and the customer can follow it, every layer and every kind of rule has been used once. "
  "The nine use cases are UC02 Login, UC04 Browse / Search Products, UC05 View Product, UC06 Manage Shopping Cart, "
  "UC07 Place Order (with UC21 Validate Cart), UC08 Make Payment, UC09 Track Order, UC14 Process Orders (with the "
  "shipping data of UC16) and UC15 Manage Inventory. They replace my earlier in-memory Spring demo (Design 01), which "
  f"never used the designed database. Table {next_tab()} lists the environment.", keep=True)
table("Environment of the ABC Online Shop application", [
    ["Part", "Choice", "Used for"],
    ["Language, build", "Java 17, Maven 3.9.11", "all server code and the JUnit suite"],
    ["Web framework", "Spring Boot 3.2.2 with embedded Tomcat", "controllers, JSON and sessions; port 8080"],
    ["Database", "SQLite file, sqlite-jdbc 3.45.1.0, plain JDBC", "created from db/schema.sql and db/seed.sql"],
    ["Screens", "HTML, CSS and JavaScript ES modules; no framework, no build step; the browser's speech recognition", "the eight view classes"],
    ["Tests, checks", "JUnit 5 with MockMvc; Python 3.12; Node.js 24 with Playwright 1.48 on Microsoft Edge", "unit, integration, HTTP and browser tests; design and schema checks"],
], [2.8, 6.7, 6.5], size=10)
p("One environment problem cost me an evening: Maven failed with \"Input length = 1\" inside the course folder, whose "
  "path contains Vietnamese characters. Maven wrote its list of source files in the Windows code page, which has no "
  "letter such as \"ế\"; the file app/.mvn/jvm.config starts Maven with UTF-8 and the build works. The project "
  "therefore sits in the essay folder next to this report, as one git repository that is the source of every number "
  "in this chapter.")

# ------------------------------------------------------------------------------------------------ 5.2
h2("5.2. Project Structure: the Design Packages")
p("The Java packages and classes have the names of the design packages and classes, so that when a sequence diagram "
  "says that OrderService calls ProductDAO.reserveStock, I can open OrderService.java and find the call. Only the "
  "view package is not a Java package: its seven classes are ES modules in the browser.", keep=True)
code('''07_Tieu_luan              essay folder and git repository; this report is in Bai_nop
|-- db                   schema.sql, vp/vp_ddl.sql, compare_schema.py, make_seed.py, seed.sql
|-- app/src/main
|   |-- java/vn/ptit/ecom
|   |   |-- controller    AuthController, ProductController, CartController, OrderController, ...
|   |   |-- service       AuthService, CatalogService, CartService, OrderService, ...
|   |   |-- model         cart, customer, order, product, RuleViolation
|   |   |-- dao           Database, ProductDAO, CartDAO, OrderDAO, ... and one ...DAOImpl for each
|   |   `-- integration   CardProvider, SimulatedCardProvider, CardData
|   `-- resources/static  index.html, css, js/app.js, js/view/CustomerForm.js ... StockForm.js
`-- app/src/test, tests, docs, showcase, vp''', size=8)
p(f"The layers are those of Figure {F_G0} in Chapter 4: presentation (views and controllers), business logic "
  "(services and model) and data access (the DAOs and the gateway to the payment provider). The packages of Figure "
  f"{F_G1} have <<use>> dependencies that point downwards only.")
p("A text search finds SQL keywords only in the dao package, and no controller calls a DAO method; two controllers "
  "import a type declared inside a DAO interface (OrderDAO.OrderSummary, ProductDAO.Sort), which I left there "
  "because OrderSummary is a row for list screens and not a domain object. Spring wires controllers and services "
  "through constructors [14]; the DAOs are not beans, because each unit of work creates its own (Section 5.4).")

# ------------------------------------------------------------------------------------------------ 5.3
h2("5.3. The Database Comes from the Physical Model")
p("db/schema.sql is the DDL of the physical model of Chapter 4: 20 tables, 22 foreign keys, 9 UNIQUE and 34 CHECK "
  "constraints. Following the lecturer's feedback, product holds only what every product has and category names the "
  "detail table (book_detail, laptop_detail, phone_detail or apparel_detail), which the code reads through the enum "
  "DetailKind. db/compare_schema.py compares the DDL that Visual Paradigm exports from the model (db/vp/vp_ddl.sql) "
  "with schema.sql, as text and as the structure that SQLite builds from each. Its last line of output is \"tables "
  "20, foreign keys 22, textually identical: True, structurally identical: True\".")
p(f"A rule that matters is written twice: in the model, for a clear message, and in the schema, for the case that a "
  f"later code path forgets it. Table {next_tab()} lists the constraints that I rely on.", keep=True)
table("Business rules that the database enforces by itself", [
    ["Rule", "Constraint (db/schema.sql)", "What it stops"],
    ["BR02", "UNIQUE (cart_id, product_id); CHECK (quantity > 0) on cart_item", "two lines for one product; a line without quantity"],
    ["BR04", "CHECK (total_amount = subtotal - discount + shipping_fee) on customer_order", "a total that does not match its parts"],
    ["BR05, BR12", "CHECK (stock_quantity >= 0) on product", "negative stock, even from code that forgets the rule"],
    ["BR07", "pay_credit has card_last4, expiry and provider_token and no column for the number", "storing the full card number: there is no place for it"],
    ["BR09", "CHECK (status IN (...)) with the seven status names", "an unknown status (the transitions are in OrderStatus)"],
    ["BR10", "UNIQUE on shipping.order_id and on shipping.tracking_number", "a second shipment for an order; a reused tracking number"],
], [1.9, 7.6, 6.5], size=9.5)
p("db/make_seed.py writes db/seed.sql: 10 categories, 28 products with their detail rows, 3 customers (one VIP, one "
  "new), 2 staff accounts and 4 past orders that obey the rules of docs/SPEC.md. Passwords are PBKDF2 hashes.")

# ------------------------------------------------------------------------------------------------ 5.4
h2("5.4. Data Access Objects")
p("Each DAO is an interface, for example ProductDAO, with one implementation that holds the JDBC Connection it was "
  "given. I chose plain JDBC instead of JPA/Hibernate because it keeps the interface-and-implementation method of the "
  "course visible and lets me show every SQL statement; the price is that I write each mapping by hand. "
  "Database.inTransaction creates the seven DAOs over one connection, runs the work that a service passes in, and "
  "commits, or rolls back if the work throws:", keep=True)
code('''public <T> T inTransaction(Work<T> work) {
    try (Connection c = open()) {
        c.setAutoCommit(false);
        try {
            T result = work.run(new Daos(new ProductDAOImpl(c), new CustomerDAOImpl(c), new StaffDAOImpl(c),
                    new CartDAOImpl(c), new OrderDAOImpl(c), new PaymentDAOImpl(c), new ShippingDAOImpl(c)));
            c.commit();
            return result;
        } catch (RuntimeException | SQLException e) {
            c.rollback();
            throw e;
        }
    } catch (SQLException e) {
        throw new DataAccessError(e);
    }
}''', size=7.5, indent=0)
p("The implementation classes are package-private, so no code can use a DAO outside a transaction. open() asks SQLite "
  "to enforce foreign keys, which it does not do by default, and to use IMMEDIATE transactions with a five-second "
  "busy timeout: a transaction takes the write lock when it begins, so two simultaneous checkouts wait for each other "
  "instead of failing halfway. Even a read takes that lock, which I accepted for one database file (Section 5.13).")
p("OrderDAOImpl.findById is typical reading code: one parameterized query builds the Order, four small queries add its "
  "lines, events, payments and shipment, and a missing row gives Optional.empty(), which the service turns into a "
  "404:", keep=True)
code('''public Optional<Order> findById(int orderId) throws SQLException {
    try (PreparedStatement ps = Jdbc.prepare(connection, "SELECT * FROM customer_order WHERE order_id = ?",
             orderId);
         ResultSet rs = ps.executeQuery()) {
        if (!rs.next()) return Optional.empty();
        return Optional.of(new Order(rs.getInt("order_id"), rs.getInt("customer_id"), rs.getInt("address_id"),
                Jdbc.ts(rs.getString("order_date")), OrderStatus.valueOf(rs.getString("status")),
                PaymentMethod.valueOf(rs.getString("payment_method")),
                rs.getLong("subtotal"), rs.getLong("discount"), rs.getLong("shipping_fee"),
                rs.getLong("total_amount"), items(orderId), events(orderId),
                payments(orderId), shipping(orderId)));
    }
}''', size=7.5, indent=0)
p("Values always go through ? parameters; the only SQL built by concatenation is the name of a detail table, taken "
  "from an enum constant. That query runs for every product of a search result, so the catalogue costs one extra "
  "query per product card. I did not measure it and left it, since a JOIN per detail kind would give the search four "
  "branches (Section 5.13). The statement that matters most is the stock reservation. It does not read the stock and "
  "compare it in Java, because two customers could both read 1 and both write 0; the database decides, and the DAO "
  "reports whether a row changed:", keep=True)
code('''public boolean reserveStock(int productId, int quantity) throws SQLException {
    return Jdbc.update(connection, "UPDATE product SET stock_quantity = stock_quantity - ? "
            + "WHERE product_id = ? AND status = 'ACTIVE' AND stock_quantity >= ?",
            quantity, productId, quantity) == 1;
}''', size=7.5, indent=0)
p("The DAO decides nothing: the service turns false into a RuleViolation BR05 (Section 5.6), and the CHECK of "
  "Section 5.3 stands behind it.")

# ------------------------------------------------------------------------------------------------ 5.5
h2("5.5. Model Classes and Business Rules")
p("The model classes hold the business rules and know nothing about HTTP or SQL, so OrderRulesTest runs its nine "
  "tests in about 30 milliseconds without a database or a web server. A broken rule is a RuleViolation with the rule "
  "id and a message for the customer. Cart.addItem is UC06: it refuses a product that is not for sale (BR01), a "
  "quantity below 1 and a quantity in the cart above the stock (BR02), and otherwise increases the line or creates "
  "one with the current price, which stays as the cart price for BR03:", keep=True)
code('''public CartItem addItem(Product product, int quantity) {
    if (quantity < 1) throw new RuleViolation("BR02", "Quantity must be at least 1.");
    if (product.getStatus() != Product.Status.ACTIVE)
        throw new RuleViolation("BR01", product.getName() + " is not for sale.");
    Optional<CartItem> line = find(product.getId());
    int wanted = quantity + line.map(CartItem::getQuantity).orElse(0);
    if (wanted > product.getStockQuantity())
        throw new RuleViolation("BR02",
                "Only " + product.getStockQuantity() + " of " + product.getName() + " in stock.");
    if (line.isPresent()) {
        line.get().setQuantity(wanted);
        return line.get();
    }
    CartItem item = new CartItem(product, quantity, product.getPrice());
    items.add(item);
    return item;
}''', size=7.5, indent=0)
p("The stock check of the sequence diagram of Chapter 2 is the third condition. At checkout the cart does not decide "
  "it alone: Cart.validate (UC21) asks the product, p.isAvailable(i.getQuantity()), and only names the reason "
  "(UNAVAILABLE or NOT_ENOUGH_STOCK) for the customer. The product holds the stock, so it is the expert that answers "
  "[4]. addItem and setQuantity still compare the stock themselves (Section 5.13).")
p("Amounts are integer VND and computed in one place, Order.Totals.of (BR04). The rate comes from the customer: "
  "Customer.discountRate() returns zero and CustomerVIP overrides it, so the generalization of the analysis model is "
  "used as polymorphism. AT03 is this method: 5 % of 1,000,000 gives 50,000 off, free delivery and a total of "
  "950,000. Order.place, the factory of UC07, refuses a foreign address (BR06) and blocking cart issues (BR05), copies "
  "the lines with their prices and starts the order as PENDING_PAYMENT (card) or PLACED (cash on delivery):",
  keep=True)
code('''public static Totals of(long subtotal, BigDecimal discountRate) {
    long discount = BigDecimal.valueOf(subtotal).multiply(discountRate)
            .setScale(0, RoundingMode.HALF_UP).longValue();
    long afterDiscount = subtotal - discount;
    long fee = afterDiscount >= FREE_SHIPPING_FROM ? 0 : SHIPPING_FEE;
    return new Totals(subtotal, discount, fee, afterDiscount + fee);
}''', size=8.5)
p("BR09 is the rule that is easiest to scatter, as a check in every controller method that changes an order. I put "
  "it into one transition table in OrderStatus (from, to, actor), and Order.changeStatus, the only way to change a "
  "status, refuses everything that is not in the table:", keep=True)
code('''static {
    allow(PENDING_PAYMENT, PAID, Actor.PROVIDER);
    allow(PENDING_PAYMENT, CANCELLED, Actor.CUSTOMER);
    allow(PLACED, PROCESSING, Actor.SALES);
    allow(PLACED, CANCELLED, Actor.CUSTOMER, Actor.SALES);
    allow(PAID, PROCESSING, Actor.SALES);
    allow(PAID, CANCELLED, Actor.SALES);
    allow(PROCESSING, SHIPPED, Actor.SALES);
    allow(PROCESSING, CANCELLED, Actor.SALES);
    allow(SHIPPED, DELIVERED, Actor.SALES);
}''', size=8.5)
p("A declined card is not a transition: Order.recordCardPayment stores the DECLINED payment, and only an APPROVED one "
  "calls changeStatus(PAID) (BR07). The same table tells the screens which buttons to offer. The server sends "
  "OrderStatus.next(actor) with every order and, as a BoardCard record, with every card of the order board, and "
  "StaffOrderForm.actions draws one button for each allowed transition and decides nothing. A review of the code "
  "found that my first board repeated the status checks in JavaScript. The server would still have answered a "
  "forbidden transition with 409, but a change of the table would have had to be made twice, so I moved the set to "
  "the server.")

# ------------------------------------------------------------------------------------------------ 5.6
h2("5.6. Services: One Use Case Step, One Transaction")
p(f"A service method is one use case step and one transaction. In the design sequence diagram of UC07 (Figure {F_G6} "
  "in Chapter 4) messages 3 to 17 are the work of OrderService.placeOrder:", keep=True)
code('''public Order placeOrder(int customerId, int addressId, PaymentMethod method, Long expectedTotal) {
    return db.inTransaction(d -> {
        Customer customer = d.customers().findById(customerId)
                .orElseThrow(() -> new NotFound("Customer not found."));
        Address address = d.customers().address(addressId)
                .orElseThrow(() -> new RuleViolation("BR06", "Choose one of your delivery addresses."));
        Cart cart = d.carts().findOrCreate(customerId);
        Order order = Order.place(customer, cart, address, method, LocalDateTime.now());
        if (expectedTotal != null && expectedTotal != order.getTotalAmount())
            throw new RuleViolation("BR03",
                    "Prices changed since you opened checkout. Please check the new total.",
                    List.of(Map.of("expectedTotal", expectedTotal, "newTotal", order.getTotalAmount())));
        for (OrderItem i : order.getItems())
            if (!d.products().reserveStock(i.productId(), i.quantity()))
                throw new RuleViolation("BR05", i.productName() + " has just sold out in this quantity.");
        d.orders().insert(order);
        d.carts().clear(cart);
        return order;
    });
}''', size=7.5, indent=0)
p("Messages 4 and 5 are inTransaction and its lambda; 6 to 9 load the customer, the address (unknown or foreign: BR06) "
  "and the cart; 10 is Order.place; 12 refuses the order with BR03 when the total differs from the expectedTotal that "
  "the customer saw; 13 and 14 reserve the stock line by line, and a false answer becomes BR05 and undoes the lines "
  "already reserved; 15 and 16 store the order and empty the cart; 17 is the commit. Any exception undoes "
  "everything, and reserving the stock before the order row is written is what makes the rollback test of "
  "Section 5.10 meaningful.")
p("UC08 is where I broke the rule of one method and one transaction on purpose: PaymentService.pay uses two short "
  "transactions with the provider call between them.", keep=True)
code('''public PaymentResult pay(int orderId, int customerId, CardData card) {
    Order before = db.inTransaction(d -> OrderService.load(d, orderId, customerId));
    if (before.getStatus() != OrderStatus.PENDING_PAYMENT)
        throw new RuleViolation("BR07", "Order " + before.code() + " is not waiting for a card payment.");

    CardProvider.Result result = provider.charge(before.code(), before.getTotalAmount(), card);

    return db.inTransaction(d -> {
        Order o = OrderService.load(d, orderId, customerId);
        // ... a PayCredit with status APPROVED or DECLINED, the last four digits and the token
        o.recordCardPayment(payment, now);
        d.payments().saveAll(o.getId(), o.getPayments());
        d.orders().saveProgress(o);
        return new PaymentResult(result.approved(), o, result.reason());
    });
}''', size=8, indent=0)
p("A card payment crosses a network. Inside one transaction the write lock of SQLite would be held until the provider "
  "answers, and every other customer would wait. So the first transaction loads and checks the order (own order, BR08, "
  "PENDING_PAYMENT), the provider call has no transaction, and the second transaction loads the order again, because "
  "it may have been cancelled meanwhile, and Order.recordCardPayment checks status and amount (BR07). The price is a "
  "gap that I know about: if the provider approves and the second transaction fails, a payment was made that the shop "
  "has not recorded; a real system needs an outbox table and a reconciliation job (Section 5.13). The provider is an "
  "interface, CardProvider, with one simulated implementation: a number ending in 0002 is declined, any other valid "
  "number is approved with a random token. CardData checks format, Luhn checksum and expiry first (UC08 A2), and only "
  "the last four digits, expiry, holder and token reach the database.")

# ------------------------------------------------------------------------------------------------ 5.7
h2("5.7. Controllers and Views")
p("A controller translates HTTP into one service call and back: it reads the user from the session, checks the shape "
  "of the request, calls one service method and returns a record of the Views class. CartController.addItem shows "
  "the four jobs:", keep=True)
code('''@PostMapping("/items")
public Views.CartView addItem(@RequestBody AddItem req, HttpSession session) {
    CurrentUser u = CurrentUser.require(session, Role.CUSTOMER);
    if (req.productId() == null || req.quantity() == null)
        throw new IllegalArgumentException("Choose a product and a quantity.");
    return Views.CartView.of(carts.addItem(u.id(), req.productId(), req.quantity()));
}''', size=8.5)
p("CurrentUser.require is where BR08 and BR13 start: the customer id comes from the session, never from the request, "
  "so changing a parameter cannot show another customer's order, and a customer on a staff endpoint gets 403 (AT10). "
  "ApiErrors maps the other exceptions to HTTP answers with a small JSON body: malformed input "
  "(IllegalArgumentException) to 400, a missing login to 401, NotFound (also another customer's order) to 404, a "
  "RuleViolation to 409 and a DataAccessError to 500 with a general message. I chose 409 for rule violations because "
  "the request is well formed and only conflicts with the state of the shop.")
p("The views are ES modules with the names of the design classes: show methods render, submit methods send input to "
  "the controller, and api() turns an error answer into an ApiError that every view shows in the same way. "
  "CartForm.submitAddItem is the view side of UC06, with alternative flow A2 first: a guest is sent to the login "
  "page and returns afterwards:", keep=True)
code('''async submitAddItem(productId, quantity) {
  if (!this.app.me.loggedIn) {
    toast("Log in to add products to your cart.");
    return this.app.go(`login?next=${encodeURIComponent(`p/${productId}`)}`);
  }
  // ...
  try {
    const cart = await api("POST", `${this.controller}/items`, { productId, quantity });
    this.app.setCartCount(cart.count);
    // ...
  } catch (err) {
    toast(err.message, "error");
  }
}''', size=8.5)
p("Every part of a page produced by a particular chain of classes carries a data-trace attribute, and Alt+L switches "
  "on the design lens, which labels each part with its view method, endpoint, controller, service, DAO and tables.")

# ------------------------------------------------------------------------------------------------ 5.8
h2("5.8. The Running System")
p("The application is built with Maven and started with one command; --abc.db.reset=true recreates the SQLite file "
  "from db/schema.sql and db/seed.sql, which I do before every demonstration. CHAY_DEMO.bat in the project folder runs "
  "the same command with a double-click, using Java 17 even when an older Java comes first on the PATH, and opens the "
  "shop in the browser. The check scripts print one result per line and end with a non-zero exit code on failure:", keep=True)
code('''# in app/
mvn test
mvn package
java -jar target/abc-online-shop-1.0.0.jar --abc.db.reset=true

# in the repository root, with the server running
python tests/smoke_api.py
node tests/e2e/run_e2e.mjs
python tests/design_vs_code.py
python db/compare_schema.py''', size=9)
p(f"tests/e2e/run_e2e.mjs drives the running application in Microsoft Edge and saves a screenshot per step, so the "
  f"figures below are not mock-ups. Figure {next_fig()} is the catalogue (UC04): the small boxes under a title are the "
  "first values of the detail row of the category, and \"Only 3 left\" comes from the stock quantity.", keep=True)
figure("docs/evidence/e2e/02_catalogue.png", "Catalogue for a guest (UC04): detail values as small boxes, stock state as a badge", width_cm=10.5)
p(f"In Figure {next_fig()} (UC07) a VIP customer has three laptops in the cart: 3 x 18,990,000 = 56,970,000 VND, "
  "minus 5 % (2,848,500), free delivery, total 54,121,500, as BR04 says.", keep=True)
figure("docs/evidence/e2e/08_checkout.png", "Checkout (UC07, UC21): the totals are those of Order.Totals.of", width_cm=10.5)
p(f"Placing the order created ORD-000005 as PENDING_PAYMENT with the stock reserved. In Figure {next_fig()} the card "
  "ending in 0002 was declined and the order is kept (UC08 A1); a second card, ending in 4242, was approved and the "
  "order became PAID.", keep=True)
figure("docs/evidence/e2e/10_payment_declined.png", "Card payment (UC08): a declined card keeps the order and its stock", width_cm=10.5)
p(f"Figure {next_fig()} is the order board of UC14: Paid and Placed orders offer Start processing and Cancel, the "
  "shipped order only Mark delivered, as the server's BR09 table allows.", keep=True)
figure("docs/evidence/e2e/13_order_board.png", "Order board of the sales staff (UC14): one column per stage of the lifecycle", width_cm=10.5)
p(f"After processing, shipping and delivery, the customer opened the order (UC09). Figure {next_fig()} shows the page "
  "with the design lens on: the history is the six order_event rows, both card attempts appear, and only the last "
  "four digits are stored (BR07). The labels name the view method, endpoint, controller, service, DAO and tables.",
  keep=True)
figure("docs/evidence/e2e/17_trace_lens.png", "Order tracking (UC09) with the design lens: the code behind each part of the page", width_cm=10.5)
p(f"In Figure {next_fig()} a warehouse staff member typed -5 as stock (UC15). Product.updateStock refused it with "
  "BR12 and a 409, and the run found the stored stock unchanged; the CHECK of Section 5.3 stands behind it.",
  keep=True)
figure("docs/evidence/e2e/19_stock_refused.png", "Inventory (UC15): a negative quantity is refused by rule BR12 and nothing is saved", width_cm=10.5)

# ------------------------------------------------------------------------------------------------ 5.9
h2("5.9. Keeping Code and Design Consistent")
p("A check that fails is better than names that happen to match. A Visual Paradigm plugin script exports the design "
  "classes and the messages of the design sequences as two tab-separated files, and tests/design_vs_code.py "
  "compares them with the javap output of the compiled classes and with the JavaScript view classes. It checks "
  "six things:", keep=True)
dash("every design class exists in its package (72 classes);")
dash("every attribute exists as a field of the same type (169);")
dash("every operation exists with the same name, parameter types and return type (134);")
dash("every view operation exists in the JavaScript class with the same number of parameters (25);")
dash("every call of the design sequences of UC04, UC06, UC07 and UC08 names an operation of the receiver (48);")
dash("no class of the ai package imports another part of the application (6 files).")
p("On 11 November 2026 it printed \"design and code agree\"; its exit code is the number of problems, so it can stop "
  "a build. The only correction it made me apply was a name: the seven DAO implementations called their JDBC field "
  "conn and the design says connection (commit 5df0074). Its limit is that it checks that an operation exists, not "
  "that anyone calls it. A search for callers showed that the design operation Product.isAvailable passed the check "
  "and was never called, because the cart compared the stock itself. Cart.validate now asks the product, and the "
  "cart only names the reason.")
p("The structural change that the design forced on the code is the service layer. My first working UC07 had no "
  "OrderService: OrderController.placeOrder opened the transaction, loaded customer, address and cart, checked BR06 "
  "and BR03, reserved the stock and wrote the order. It worked and its tests passed, but the class had three reasons "
  "to change (HTTP format, checkout rules, transaction boundary), a second entry point would have needed a copy, and "
  "the steps could be reached only through HTTP. Commit feab5f3 moved the bodies into six service classes. The "
  "listings show the controller method before and after:", keep=True)
code('''@PostMapping("/api/orders")
public Map<String, Object> placeOrder(@RequestBody PlaceOrder req, HttpSession session) {
    CurrentUser u = CurrentUser.require(session, Role.CUSTOMER);
    // ...
    return db.inTransaction(d -> {
        Customer customer = d.customers().findById(u.id()).orElseThrow();
        // ...
        Cart cart = d.carts().findOrCreate(u.id());
        Order order = Order.place(customer, cart, address, method, LocalDateTime.now());
        // ... BR03: the total must equal the one the customer confirmed
        for (OrderItem i : order.getItems())
            if (!d.products().reserveStock(i.productId(), i.quantity()))
                throw new RuleViolation("BR05", i.productName() + " has just sold out in this quantity.");
        d.orders().insert(order);
        d.carts().clear(cart);
        return Map.of("orderId", order.getId(), "code", order.code(), "status", order.getStatus(),
                "total", order.getTotalAmount());
    });
}''', size=7.5, indent=0)
code('''@PostMapping("/api/orders")
public Map<String, Object> placeOrder(@RequestBody PlaceOrder req, HttpSession session) {
    CurrentUser u = CurrentUser.require(session, Role.CUSTOMER);
    if (req.addressId() == null) throw new IllegalArgumentException("Choose a delivery address.");
    Order order = orders.placeOrder(u.id(), req.addressId(), parseMethod(req.paymentMethod()),
            req.expectedTotal());
    return Map.of("orderId", order.getId(), "code", order.code(), "status", order.getStatus(),
            "total", order.getTotalAmount());
}''', size=7.5, indent=0)
p(f"The commit touched 16 files (489 lines added, 220 removed): OrderController went from 169 to 112 lines, "
  "CartController from 73 to 54, PaymentController from 55 to 32 and ShippingController from 52 to 37. The rules "
  "did not change, only where they live: cohesion went up, because each class has one reason to change, and "
  f"coupling went down, because a controller knows services and nothing below. Figure {F_G6} already has this shape "
  "(message 3). The existing tests were not touched; the commit added the rollback test of Section 5.10.")

# ------------------------------------------------------------------------------------------------ 5.10
h2("5.10. Testing")
p("I tested at four levels, and everything passed on 11 November 2026. Unit: OrderRulesTest, 9 tests on Cart, Order, "
  "Totals and OrderStatus without a database or a web server. Integration: CheckoutFlowTest, 5 tests through MockMvc "
  "on controller, service, DAO and a real SQLite file built from schema.sql and seed.sql, and SearchTest, 10 tests of "
  "the AI search on the same kind of file. System: tests/smoke_api.py, 36 HTTP checks on the running jar, and "
  "tests/e2e/run_e2e.mjs, 30 checks in Microsoft Edge. Acceptance: AT01 to AT17 of docs/SPEC.md, in the Given, When, "
  "Then form of Section 1.12; AT11 to AT17 belong to the AI search and are listed in Section 5.12.")
p(f"Table {next_tab()} maps the criteria to the tests. I put each criterion at the cheapest level that can show it: "
  "AT03 needs no database, so it is a unit test, while AT04 needs the database to decide a race, so it is an "
  "integration test. Four more tests cover rules without a criterion: hiddenProductsCannotBeAdded (BR01), "
  "placingNeedsAnOwnAddressAndEnoughStock (BR06, BR05), customersCannotCancelOncePackingStarted (BR09) and "
  "theDatabaseItselfRefusesNegativeStock (the CHECK of Section 5.3, without the model).", keep=True)
table("Acceptance criteria and the tests that show them", [
    ["ID", "Criterion", "Rule", "Tests"],
    ["AT01", "Stock 2, customer adds 3: refused, cart unchanged", "BR02", "addingTheSameProductMergesLinesAndRespectsStock; smoke: quantity above stock refused"],
    ["AT02", "Cart price 1,000,000, price now 900,000: checkout takes 900,000 and flags the change", "BR03", "validationTakesOverChangedPrices"],
    ["AT03", "VIP 5 %, subtotal 1,000,000: discount 50,000, delivery free, total 950,000", "BR04", "totalsApplyVipDiscountAndFreeDelivery; smoke: VIP discount and free delivery"],
    ["AT04", "Stock 1, two customers order 1: the second is refused, stock stays 0", "BR05", "lastUnitCanBeSoldOnlyOnce; aFailedOrderWriteRollsBackTheStockReservation"],
    ["AT05", "Card ending 0002: DECLINED, order still PENDING_PAYMENT; a valid card then gives PAID", "BR07", "cardOrderBecomesPaidOnlyAfterApproval; smoke and e2e: declined, then approved"],
    ["AT06", "Order of customer B requested by customer A: 404", "BR08", "ordersOfOtherCustomersAreNotFound; smoke: another customer gets 404"],
    ["AT07", "Order PLACED, staff ships it directly: refused, it must be PROCESSING", "BR09", "lifecycleFollowsTheTransitionTable; smoke: cannot ship before processing"],
    ["AT08", "COD order shipped, then delivered: DELIVERED and a cash payment recorded", "BR11", "lifecycleFollowsTheTransitionTable"],
    ["AT09", "PAID order cancelled by staff: CANCELLED, stock released, payment REFUNDED", "BR05, BR09", "cancellingAPaidOrderRefundsTheCard; smoke: staff cancel returns stock"],
    ["AT10", "Customer session calls a staff endpoint: 403", "BR13", "staffFunctionsNeedTheStaffRole; smoke and e2e: customer cannot open the board"],
], [1.3, 5.9, 1.7, 7.1], size=8.5, center_cols=(0, 2))
p("The test I value most is the rollback test: a trigger makes every INSERT into customer_order fail, an order is "
  "placed, the answer must be 500, and the stock, the cart and the number of orders must be as before.")
p("The browser run found a defect that no JUnit test or HTTP check could see, because the server was right. A slow "
  "answer, for example the home page after logout, could arrive after the user had moved on and replace the page they "
  "were looking at. Commit 96dbb93 fixes it: App.route() numbers every navigation, and each of the six views that "
  "load data remembers the number when it starts a load and returns without drawing if a newer navigation has "
  "overtaken it. What the tests do not cover is listed in Section 5.13.", keep=True)
code('''route() {
  this.nav += 1;
  // ...
}

async showCart(cart) {
  const nav = this.app.nav;
  if (!cart) {
    // ...
    if (!this.app.current(nav)) return;   // a newer navigation owns the page
  }''', size=8.5)

# ------------------------------------------------------------------------------------------------ 5.11
h2("5.11. Traceability from Requirement to Test")
p(f"Chapter 1 traces problems to requirements and use cases, and the chain continues into the code. Table {next_tab()} "
  "follows each implemented use case to the view, controller, service and DAO methods that carry it and to its tests "
  "(DAO names are those of the interfaces). docs/TRACEABILITY.md holds the full chain, from requirement and "
  "diagram to code line and test, with a link for each step, and tests/check_links.py checks the links. The table "
  "works in both directions: a failing AT04 means that BR05 is broken, which comes from FR15 and FR16 of Chapter 1, "
  "and the code to open first is ProductDAOImpl.reserveStock and OrderService.placeOrder.",
  keep=True)
table("From use case to code and tests", [
    ["Use case", "View", "Controller", "Service", "DAO", "Tests"],
    ["UC02", "CustomerForm.submitLogin", "AuthController.login", "AuthService.login", "CustomerDAO.findAccount, StaffDAO.findAccount", "smoke, e2e"],
    ["UC04, UC05", "ProductForm.showCatalogue, showProduct", "ProductController.search, product", "CatalogService.search, product", "ProductDAO.search, findById", "smoke, e2e"],
    ["UC04 AI search", "SearchForm.showResults, startVoice, submitPhoto", "SearchController.search, searchByPhoto", "SearchService.search, searchByPhoto", "ProductDAO.search; ai: QueryInterpreter, ProductIndex, ImageIndex", "AT11 to AT17"],
    ["UC06", "CartForm.submitAddItem", "CartController.addItem", "CartService.addItem", "CartDAO.findOrCreate, save", "AT01, e2e"],
    ["UC07, UC21", "OrderForm.submitOrder", "OrderController.placeOrder", "OrderService.placeOrder", "ProductDAO.reserveStock, OrderDAO.insert", "AT02 to AT04"],
    ["UC08", "PaymentForm.submitPayment", "PaymentController.pay", "PaymentService.pay", "PaymentDAO.saveAll, OrderDAO.saveProgress", "AT05"],
    ["UC09", "OrderForm.showOrder", "OrderController.order", "OrderService.details", "OrderDAO.findById", "AT06"],
    ["UC14", "StaffOrderForm.showBoard", "OrderController.process, ShippingController.ship", "OrderService.process, ShippingService.ship", "OrderDAO.saveProgress, ShippingDAO.save", "AT07 to AT10"],
    ["UC15", "StockForm.submitStock", "ProductController.updateStock", "CatalogService.updateStock", "ProductDAO.updateStock", "smoke, e2e (BR12)"],
], [1.5, 3.0, 3.0, 2.9, 3.4, 2.2], size=8.5)

# ------------------------------------------------------------------------------------------------ 5.12
h2("5.12. The AI Search in Code")
p("The AI search of Chapter 3 is the package ai, six classes and about 530 lines, plus SearchService, "
  "SearchController and the view SearchForm. Nothing in ai imports the rest of the application, which the check of "
  "Section 5.9 confirms on every run. QueryInterpreter holds the lexicon that the sales staff keep. It is two small "
  "tables, words that mean the same thing and words that are a kind of another, because the first version with "
  "plain synonym groups ranked burgundy boots above red sneakers (Section 3.11):", keep=True)
code('''static final String[][] SYNONYMS = {
        {"laptop", "notebook", "ultrabook"},
        {"smartphone", "phone", "mobile", "cellphone"},
        {"sneaker", "trainer"},
        // ...
};
static final String[][] BROADER = {
        {"sneaker", "shoe"}, {"trainer", "shoe"}, {"boot", "shoe"},
        {"burgundy", "red"}, {"indigo", "blue"}, // ...
};''', size=8.5)
p("Before the words are looked up, the interpreter takes out a price limit (\"under 10 million\", \"duoi 5 trieu\", "
  "\"500k\") as a filter, replaces Vietnamese phrases by their English words and corrects a word that the catalogue "
  "does not use to the nearest catalogue word, one edit away for words of five to seven letters and two from eight. "
  "ProductIndex then scores every product. A related word stands in for the customer's word and does not add to "
  "it, so for each word of the query only the best of the word and its related words counts:", keep=True)
code('''for (Map.Entry<String, Double> e : qv.entrySet()) {
    Double w = d.vector().get(e.getKey());
    if (w == null) continue;
    String origin = via.getOrDefault(e.getKey(), e.getKey());   // the customer's word behind it
    double part = e.getValue() * w;
    if (part > best.getOrDefault(origin, 0.0)) {
        best.put(origin, part);
        bestWord.put(origin, e.getKey());
    }
}
double score = best.values().stream().mapToDouble(Double::doubleValue).sum();''', size=8.5)
p("The words in bestWord become the reasons on the result page, with the field they were found in: \"colour: "
  "red\", \"category: shoe (related to sneaker)\". SearchService puts the steps of the design sequence together and "
  "keeps the fallback of AI04 in one place:", keep=True)
code('''public SearchResult search(String text) {
    // ...
    List<Product> active = activeProducts();                 // one short transaction
    Indexes ix = indexes(active);                            // rebuilt if the catalogue changed (FR-S7)
    SearchQuery q = ix.interpreter().interpret(text);
    List<Hit> hits = ix.text().rank(q, TOP_K);
    if (!hits.isEmpty()) return new SearchResult(Mode.TEXT, q, items(hits, active, true), false, ms(t0));
    List<Item> keyword = db.inTransaction(d -> d.products().search(text.trim(), null, ProductDAO.Sort.RELEVANCE))
            // ...
    return new SearchResult(Mode.KEYWORD, q, keyword, true, ms(t0));
}''', size=8.5)
p(f"The search box in the header has two more buttons, a microphone and a camera. Figure {next_fig()} is the page "
  "for \"red sneakers under 3 million\": the line \"Understood as\" shows the terms, the related words in grey and the "
  "price limit in green, and each card shows its relevance and its reasons.", keep=True)
figure("docs/evidence/e2e/20_search_ai_text.png", "AI search for \"red sneakers under 3 million\": the understood query and the reasons of each result", width_cm=14)
p(f"In Figure {next_fig()} the end-to-end run uploaded a photo of the Nike Air Max 90 on a beige background, one of "
  f"the photos of Table {T_EVAL_PHOTO}; the shoe is first, with the share of similar colours and of similar outline. "
  "The voice dialog shows what the browser heard and lets the customer correct it before the search runs (FR-S4); if "
  "the browser has no speech recognition, the same dialog is a text box.", keep=True)
figure("docs/evidence/e2e/21_search_photo.png", "Photo search: the uploaded photo and the products that look most alike", width_cm=14)
p(f"Table {next_tab()} links the acceptance criteria of the AI search to the tests that show them. The ranking "
  f"quality itself is measured by tests/search_eval.py with the results of Tables {T_EVAL_TEXT} and {T_EVAL_PHOTO}.", keep=True)
table("Acceptance criteria of the AI search and the tests that show them", [
    ["ID", "Criterion", "Rule", "Tests"],
    ["AT11", "\"red sneakers\": the red Converse first; \"sneakers\" understood as shoes", "AI02", "synonymsAndColourFindTheRedSneakers; e2e"],
    ["AT12", "\"macbok air\": MacBook Air first, correction shown", "FR-S1", "misspelledWordIsCorrectedAndShown; e2e"],
    ["AT13", "\"laptop under 10 million\": only laptops up to 10,000,000", "AI03", "priceLimitIsAHardFilter; smoke"],
    ["AT14", "\"book for a programmer\": Clean Code and The Pragmatic Programmer in the first three", "AI02", "relatedWordsReachTheRightBooks"],
    ["AT15", "Cropped, darker photo of a product: that product first", "FR-S5", "photoOfAProductFindsIt; e2e (Nike photo)"],
    ["AT16", "\"xyzzy\": keyword fallback, empty, said so", "AI04", "nothingFoundFallsBackToKeywordSearch; smoke"],
    ["AT17", "A text file sent as photo: 400, nothing stored", "AI05, AI06", "aTextFileIsNotAPhoto"],
    ["-", "Out-of-stock laptop not first for \"laptop\"; query over 200 characters refused", "AI07, AI06", "outOfStockProductRanksLower; tooLongQueryIsRefused; smoke"],
], [1.3, 7.0, 1.9, 5.8], size=8.5, center_cols=(0, 2))
# ------------------------------------------------------------------------------------------------ 5.13
h2("5.13. Limitations and Future Work")
p(f"Table {next_tab()} states what the application does not do, what that means today and what I would do next. Every "
  "limitation sits in one place, and none of the next steps changes the layers.", keep=True)
table("Limitations of the application and the next steps", [
    ["Limitation", "What it means now", "Next step"],
    ["Nine of 21 use cases", "no registration (customers are seeded), reviews, promotions, reports or supplier input", "add each as a service, a model rule and a DAO"],
    ["SQLite", "one writer at a time; every service call, even a read, takes the write lock", "PostgreSQL behind the DAO interfaces, with indexes"],
    ["AI search on a word model", "28 products; the lexicon is a list in the code; \"warm clothes for winter\" finds nothing; photos are compared by colour and outline, not by learned features", "an embedding model behind ProductIndex and ImageIndex; a lexicon screen for the sales staff; search logs for the success rate"],
    ["Simulated payment provider", "no network; a failure after the provider's answer leaves a payment unrecorded", "a real provider, an outbox table, a reconciliation job"],
    ["Extra query per product card", "ProductDAOImpl loads each detail row separately (28 queries for all products)", "one JOIN per detail kind"],
    ["Session security", "no CSRF token and no limit on failed logins", "a CSRF token; a delay after failed logins"],
    ["Stock rule in two places", "Cart.validate asks Product.isAvailable, but Cart.addItem and Cart.setQuantity compare the stock themselves", "let them call isAvailable too"],
    ["Test gaps", "views tested only through the browser run, DAOs only through the services; no accessibility audit, no load test", "a test per SQL statement; an accessibility check"],
], [3.2, 7.0, 5.8], size=9)

# ------------------------------------------------------------------------------------------------ 5.14
h2("5.14. Chapter Summary")
p("The code confirmed the layered design and showed me weaknesses that the diagrams had not. The application runs "
  "nine use cases on the 20-table database of the physical model, with the AI search of Chapter 3 in UC04. The "
  "database that Visual Paradigm generates has the tables, columns and rules of the database the application runs, "
  "the code skeleton that Visual Paradigm generates is fully implemented, and the design classes, attributes, "
  "operations and sequence calls agree with the code. On 11 November 2026 the 24 JUnit tests, 36 HTTP checks and 30 "
  "browser checks passed, and the AI search found the right product first for 29 of 30 labelled queries.")
p("The weaknesses were of different kinds, and I fixed them. My first controllers did the work of services (commit "
  "feab5f3). A slow page load could replace the page the user had moved to, which only the browser run could see "
  "(commit 96dbb93). The design check and a search for callers showed that Product.isAvailable was never called, and "
  "a review showed that the order board repeated BR09 in JavaScript. The generated code showed compositions that the "
  "model had left navigable both ways, and the first ranking of the AI search put burgundy boots above red sneakers. "
  "The limits that remain are known and each sits in one place (Section 5.13).")
