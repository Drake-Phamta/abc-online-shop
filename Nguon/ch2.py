# -*- coding: utf-8 -*-
# CHAPTER 2. ANALYSIS  (built on Assignment 02, Assignment 03 and Test 01)

chapter("Analysis")
p("Analysis turns the requirements of Chapter 1 into models of the problem domain. The models answer \"what\" "
  "questions at a finer grain than the requirements: who does what with the system (use cases), in which order and "
  "with which decisions (activity and swimlane diagrams), how data moves (data flow diagram), which objects "
  "collaborate in one scenario (sequence diagram), and which data the shop must store (data models). The analysis "
  "class diagram, which links analysis and design, opens Chapter 4. Analysis models still say nothing about frameworks or databases; that is the "
  "subject of Chapter 4. The models were first drawn for Assignments 02 and 03 and for Test 01; for this version I "
  "redrew all of them in one Visual Paradigm project, corrected them with what the design and the prototype "
  "taught me, and say in each section what changed.")

h2("2.1. From Requirements to Analysis Models")
p("Each kind of analysis model answers a question that a requirement table cannot answer well. A functional "
  "requirement such as FR10 says that a customer submits a checkout request, but not what happens when the "
  "product is unavailable halfway through, who is responsible for each step, or which data the step reads and "
  "writes. Table 2.1 shows the models I used, the question each one answers and the requirements it refines.",
  keep=True)
table("Analysis models used for ABC Online Shop", [
    ["Model", "Question it answers", "Refines"],
    ["Use case diagram and specifications", "Who uses the system for which goal, with which normal and alternative flows?", "All FRs, grouped by actor goal"],
    ["Activity diagram", "In which order do the steps of one use case run, and where are the decisions?", "UC06, UC07, UC08, UC09, UC14"],
    ["Swimlanes of the activity diagrams", "Which actor or system is responsible for each step of a cross-role process?", "Order processing (UC14), payment (UC08)"],
    ["Data flow diagram", "Where does data come from, where is it stored, where does it go?", "FR11, FR15, FR16, FR23"],
    ["Sequence diagram", "Which objects exchange which messages in one scenario?", "FR07, FR10, FR14 (add to cart, checkout, payment)"],
    ["Analysis class diagram (Section 4.1)", "Which concepts exist and how are they related?", "Data needs of all FRs"],
    ["Data model and ERD", "Which data must be stored, with which keys and multiplicities?", "NFR07, NFR10"],
], [4.2, 7.4, 4.4], size=10.5)

h2("2.2. Actors")
p("An actor is a role that interacts with the system from outside. I derived the actors directly from the "
  "stakeholders of Section 1.4 and kept the distinction between human actors and external systems. Table 2.2 lists "
  "them. The managers' interaction is narrow (requesting reports), but it is real, so the manager is an actor; the "
  "supplier is an actor because supply information enters the system through it (UC19).", keep=True)
table("Actor catalogue", [
    ["Actor", "Type", "Direct interaction with the system"],
    ["Customer", "External person", "Register, log in, browse and search, manage cart, check out and pay, track orders, review"],
    ["Administrator", "Internal person", "Manage products and categories, promotions and reviews"],
    ["Sales Staff", "Internal person", "Process orders, maintain customer records, coordinate shipping"],
    ["Warehouse Staff", "Internal person", "View and update inventory"],
    ["Manager", "Internal person", "Request sales, inventory, order and operational reports"],
    ["Payment Provider", "External system", "Receive payment requests, return transaction results"],
    ["Shipping Provider", "External organization", "Receive delivery data, return shipment status"],
    ["Supplier", "External organization", "Provide product and replenishment information"],
], [3.3, 3.3, 9.4], size=10.5)

h2("2.3. Use Case Model")
p("A use case is a goal an actor reaches through the system, described from the actor's point of view. I named "
  "every use case with a verb and an object and kept them at the level of one sitting of one user: \"Place Order\" "
  "is a use case, \"Click the Confirm button\" is a step inside it and \"Run the shop\" is far too large. Table 2.3 "
  "lists the twenty-one use cases.", keep=True)
table("Use case catalogue", [
    ["ID", "Use case", "Primary actor", "Goal"],
    ["UC01", "Register Account", "Customer", "Create a customer account"],
    ["UC02", "Login", "Customer", "Access account-specific functions"],
    ["UC03", "Manage Profile", "Customer", "Maintain own profile"],
    ["UC04", "Browse / Search Products", "Customer", "Find products in the current catalogue"],
    ["UC05", "View Product", "Customer", "Inspect details, price and availability"],
    ["UC06", "Manage Shopping Cart", "Customer", "Keep selected products before checkout"],
    ["UC07", "Place Order / Checkout", "Customer", "Submit a valid purchase and get confirmation"],
    ["UC08", "Make Payment", "Customer", "Coordinate payment and get its status"],
    ["UC09", "Track Order", "Customer", "See order, payment and shipment status"],
    ["UC10", "Submit Review", "Customer", "Give post-purchase feedback"],
    ["UC11", "Manage Products and Categories", "Administrator", "Maintain the catalogue"],
    ["UC12", "Manage Promotions", "Administrator", "Maintain promotions and conditions"],
    ["UC13", "Manage Reviews", "Administrator", "Moderate customer feedback"],
    ["UC14", "Process Orders", "Sales Staff", "Move orders through operational handling"],
    ["UC15", "Manage Inventory", "Warehouse Staff", "View and update stock"],
    ["UC16", "Coordinate Shipping", "Sales Staff", "Send delivery data, receive shipment status"],
    ["UC17", "Manage Customer Records", "Sales Staff", "Maintain authorized customer data"],
    ["UC18", "Generate Management Reports", "Manager", "Get current sales, stock and order information"],
    ["UC19", "Record Supply Information", "Supplier", "Provide replenishment information"],
    ["UC20", "Apply Promotion", "Customer", "Apply an eligible promotion at checkout"],
    ["UC21", "Validate Cart", "(included by UC07)", "Check the cart against current data"],
], [1.4, 4.8, 3.4, 6.4], size=10, center_cols=(0,))
p("Figure 2.1 is the complete use case diagram, redrawn for this version in one Visual Paradigm project together with "
  "every other diagram of the essay. Customer use cases are on the left, the staff and management use cases on the "
  "right, and each external system is connected only to the use cases that exchange information with it.")
landscape()
figure("vp/png/R2.png", "Use case diagram of ABC Online Shop: twenty-one use cases, include and extend relationships with named extension points", width_cm=19.4, max_h_cm=16)
figure("vp/png/R3.png", "Use cases implemented in the prototype and their actors", width_cm=21, max_h_cm=16)
portrait()
p("The include and extend relationships needed the most care, and one of them changed after the design of Chapter 4. "
  "UC07 Place Order includes UC21 Validate Cart, because the cart is always checked before confirmation (FR09). UC20 "
  "Apply Promotion extends UC07 at the extension point \"promotion code entered\", because the extra behaviour only "
  "happens when the customer selects an eligible promotion. In Assignment 02 I had also drawn UC08 Make Payment as an "
  "include of UC07. The test I use for the choice is simple: if the base use case is incomplete without the other "
  "behaviour, it is an include; if the base use case is complete and the other behaviour is added only under a "
  "condition, it is an extend. Cash on delivery showed that the old choice failed this test: an order paid on "
  "delivery is complete when it is placed, and the payment only runs when the customer chooses a card. UC08 therefore "
  "extends UC07 at the extension point \"card payment chosen\" with the condition payment method = CARD. Figure 2.2 "
  "shows the part of the model that the prototype of Chapter 5 implements, with its actors.")

p("The overview has 21 use cases on one page, which shows the whole system but is too dense to read the actors "
  "of one area. Figures 2.3 to 2.7 are the detailed use case diagrams, one for each functional area of the shop: "
  "customer accounts, catalogue and inventory, shopping and payment, order fulfilment, and reviews, promotions and "
  "reports. Each repeats the use cases of its area with their actors and relationships, so a reader can check one "
  "area at a time, and together they contain all 21 use cases and every association of Figure 2.1. Figure 2.3 adds "
  "one thing the overview leaves out to keep its lines readable: the sales staff and the warehouse staff also log in "
  "through UC02, as Figure 2.2 shows for the prototype. UC04 of the catalogue area is refined once more for the AI "
  "search in Chapter 3 (Figure 3.1).", keep=True)
figure("vp/png/R4.png", "Detailed use case diagram: customer accounts (diagram R4)", width_cm=13.5, max_h_cm=9)
figure("vp/png/R5.png", "Detailed use case diagram: catalogue and inventory (diagram R5)", width_cm=14.5, max_h_cm=13.5)
figure("vp/png/R6.png", "Detailed use case diagram: shopping and payment, with the include and extend relationships of UC07 (diagram R6)", width_cm=16, max_h_cm=7.5)
figure("vp/png/R7.png", "Detailed use case diagram: order fulfilment (diagram R7)", width_cm=16, max_h_cm=9)
figure("vp/png/R8.png", "Detailed use case diagram: reviews, promotions and reports (diagram R8)", width_cm=16, max_h_cm=11)

h2("2.4. Use Case Specification: Place Order")
p("A diagram shows that a use case exists; the specification says what happens inside it. I specified the use cases "
  "of the order path in full; Table 2.4 is the specification of UC07, the most important one. The other "
  "specifications, the business rules BR01 to BR13 and the acceptance tests are in the specification file of the "
  "project (SPEC.md), so that the code and the tests can cite the same rule numbers.", keep=True)
table("Use case specification UC07 Place Order / Checkout", [
    ["Item", "Description"],
    ["Primary actor", "Customer"],
    ["Supporting actor", "Payment Provider (through the extension UC08)"],
    ["Goal", "Purchase the selected products and receive a confirmed order"],
    ["Trigger", "Customer selects Checkout"],
    ["Preconditions", "The customer is logged in; the cart has at least one line"],
    ["Postconditions", "The order and its lines are stored with the prices of checkout; stock is reserved; the cart is empty; the order is PLACED (cash on delivery) or PENDING_PAYMENT (card)"],
    ["Main flow", "1. Customer opens checkout. 2. System validates the cart (UC21): price, status and stock of every line. 3. Customer chooses a delivery address and a payment method. 4. System shows the subtotal, the VIP discount, the shipping fee and the total (BR04). 5. Customer confirms. 6. System, in one transaction, validates the cart again, creates the order and its lines, reserves the stock (BR05) and empties the cart. 7. Cash on delivery: the order is PLACED and the confirmation is shown. Card: UC08 continues with the order PENDING_PAYMENT."],
    ["Alternative flows", "A1 A product is unavailable or not in stock: confirmation is blocked, the line is marked. A2 No address or an address of another customer: refused (BR06). A3 A price changed since the page was shown: the lines take the current price and the customer confirms the new total (BR03)."],
    ["Exceptions", "The order cannot be stored: the transaction is rolled back, nothing is reserved and the cart is unchanged"],
    ["Business rules", "BR03 to BR06; an order is never marked paid without an approved provider result (BR07, in UC08)"],
], [3.2, 12.8], size=10.5)
p("Writing the specification again for the prototype changed one decision of Assignment 02. The old main flow "
  "created the order after the payment. FR14 asks that the provider's result is recorded \"against the correct "
  "order\", which needs an order reference before the provider is called, and the stock must be held while the "
  "customer types the card data. The order is therefore created first, in state PENDING_PAYMENT, and it becomes PAID "
  "only after an approved result, which keeps the original rule of A4.")
p("The other use cases of the implemented scope are specified in the same form, more briefly, in the following "
  "tables. Every rule they name has an identifier that the code and the tests cite (BR01 to BR13, and AI01 to AI07 "
  "for the AI search of Chapter 3).", keep=True)


def spec(title, rows):
    table(title, [["Item", "Description"]] + rows, [3.2, 12.8], size=10)


spec("Use case specification UC02 Login", [
    ["Actors", "Customer, Sales Staff, Warehouse Staff"],
    ["Pre / postconditions", "The account exists / a session holds the user's id and role; the start page of the role is open"],
    ["Main flow", "1. The user enters email and password. 2. The system checks the account (customer or staff) and the password hash. 3. The system starts a new session and opens the role's start page."],
    ["Alternative flows", "A1 Wrong email or password: one generic message that does not tell which of the two was wrong."],
    ["Rules", "Passwords stored only as hashes; a new session id at login (NFR03, NFR04)"],
])
spec("Use case specification UC04 Browse / Search Products and UC05 View Product", [
    ["Actors", "Customer (also a guest); Speech Recognition Service for a spoken query"],
    ["Pre / postconditions", "None / nothing is changed; the customer sees products and can open one"],
    ["Main flow", "1. The customer opens a category, or types a search. 2. Browsing: the system lists the ACTIVE products of the category and its sub-categories with price and availability, sorted by relevance, price or newest. Searching: the AI search interprets the query and ranks the ACTIVE products; the page shows how the query was understood and why each result matched. 3. The customer opens a product. 4. The system shows the common data and the attributes of the product's detail kind (book, laptop, phone, apparel)."],
    ["Alternative flows", "A1 Spoken query: the browser turns speech into text, which the customer can correct. A2 Photo: the products whose pictures look most alike. A3 Nothing found: keyword search; if empty too, an empty state with a link to all products."],
    ["Rules", "Only ACTIVE products (BR01, AI01); price limits are filters (AI03); fallback (AI04); photos never stored (AI05)"],
])
spec("Use case specification UC06 Manage Shopping Cart", [
    ["Actors", "Customer"],
    ["Pre / postconditions", "The customer is logged in / the cart lines are stored with the price of the moment they were added"],
    ["Main flow", "1. The customer adds a product with a quantity. 2. The system checks that the product is for sale and that the quantity is in stock, and adds a line or increases the existing one, with the current price as cart price. 3. The customer changes a quantity or removes a line. 4. The system recalculates the subtotal."],
    ["Alternative flows", "A1 Quantity above the stock: refused with the available quantity. A2 Not logged in: the login page, then back to the product."],
    ["Rules", "Only ACTIVE products (BR01); one line per product, quantity between 1 and the stock (BR02)"],
])
spec("Use case specification UC08 Make Payment", [
    ["Actors", "Customer; Payment Provider"],
    ["Pre / postconditions", "An order of the customer in PENDING_PAYMENT / a payment record with its result; the order PAID if the card was approved"],
    ["Main flow", "1. The customer enters card holder, number, expiry and CVV. 2. The system checks the format and the expiry and sends the amount and the order reference to the provider. 3. The provider approves and returns a token. 4. The system records the payment (APPROVED, last four digits, token) and sets the order PAID."],
    ["Alternative flows", "A1 Declined: the payment is recorded as DECLINED and the order stays PENDING_PAYMENT; the customer may try another card or cancel. A2 Invalid card data: refused before the provider is called."],
    ["Rules", "Only the last four digits and the token are stored; PAID only after an approved result (BR07)"],
])
spec("Use case specification UC09 Track Order", [
    ["Actors", "Customer"],
    ["Pre / postconditions", "The customer is logged in / nothing is changed, except when the customer cancels"],
    ["Main flow", "1. The customer opens My orders. 2. The system lists the customer's orders, newest first. 3. The customer opens one. 4. The system shows the lines, the totals, the payment records, the shipment with carrier and tracking number, and the status history."],
    ["Alternative flows", "A1 The order belongs to someone else: \"not found\", the same answer as for a missing order. A2 The customer cancels before packing started."],
    ["Rules", "Customers see only their own orders (BR08); cancellation only in the states BR09 allows"],
])
spec("Use case specification UC14 Process Orders (with the shipping data of UC16)", [
    ["Actors", "Sales Staff"],
    ["Pre / postconditions", "The staff member is logged in with the sales role / the order is in its new state; an event row records who changed it and when"],
    ["Main flow", "1. The sales staff opens the order board, grouped by status. 2. The staff moves an order on: start processing, ship with carrier and tracking number, mark delivered, or cancel. 3. The system applies the side effects: a shipment record when shipped, a cash payment when a cash order is delivered, released stock and a refund when an order is cancelled."],
    ["Alternative flows", "A1 The transition is not allowed from the current state: refused, with the actions that are allowed."],
    ["Rules", "Transition table (BR09); one shipment per order, unique tracking number (BR10); cash recorded on delivery (BR11); staff role required (BR13)"],
])
spec("Use case specification UC15 Manage Inventory", [
    ["Actors", "Warehouse Staff"],
    ["Pre / postconditions", "The staff member is logged in with the warehouse role / the new stock quantity is stored"],
    ["Main flow", "1. The warehouse staff opens the stock list, lowest stock first. 2. The staff sets a new quantity. 3. The system stores it."],
    ["Alternative flows", "A1 A negative or non-numeric quantity: refused, the stored value is unchanged."],
    ["Rules", "Stock never becomes negative (BR12), also checked by the database; staff role required (BR13)"],
])

h2("2.5. Activity Modeling")
p("Activity diagrams show the control flow of a use case: actions, decisions with guard conditions and the final "
  "states. For this version every activity diagram has swimlanes, so each one also shows who performs an action. "
  "Figure 2.8 is the activity diagram of UC07. The customer lane holds what the customer does, the Shop System lane "
  "what the system does. Its four decisions are the alternative flows of Table 2.4: a blocking issue sends the "
  "customer back to the cart, a changed price is taken over before the totals are shown, a failed transaction "
  "(total changed or a product just sold out) asks the customer to confirm again, and the payment method decides "
  "between the two endings.")
figure("vp/png/A2.png", "Activity diagram of UC07 Place Order / Checkout with the customer and system lanes", width_cm=16, max_h_cm=21.5)
p("I wrote the conditions on the outgoing flows ([blocking issue], [no blocking issue]) and left the decision nodes "
  "unnamed. My first version put a question inside each diamond and the same words again on the flows, and the "
  "question made the diamonds large and pushed the flows apart. The guards alone are the UML way and read just as "
  "well. The activity of UC06 (Figure 2.9) has the same structure on a smaller scale: a guest is sent to the login "
  "first, a product that is not for sale or a quantity above stock is refused with the reason, and the two branches "
  "[already in the cart] and [new product] meet again in a merge node before the cart is saved. Every loop back "
  "also ends in a merge node, never directly on an action: in UML an action with two incoming flows waits for both "
  "(an implicit join), so the customer who updates the cart could never open checkout again.")
figure("vp/png/A1.png", "Activity diagram of UC06 Manage Shopping Cart", width_cm=16, max_h_cm=21.5)

h2("2.6. Responsibilities: Swimlane Diagram")
p("Order processing involves three parties, and the swimlanes of Figure 2.10 show the handoffs between them: the "
  "sales staff choose an order and an action, the Shop System checks that the action is allowed from the current "
  "status, and the Shipping Provider carries the parcel. A refused action ends with the allowed actions shown; "
  "process and cancel end in the system lane; ship continues with the carrier and the tracking number, the shipment "
  "record, the delivery by the carrier and the confirmation by the staff. Each handoff is an information flow that "
  "must be recorded, and each one appears again as a requirement (FR13, FR17, FR18) and as a column or table in "
  "Chapter 4 (status, shipping, order_event).")
landscape()
figure("vp/png/A5.png", "Activity diagram with swimlanes of UC14 Process Orders: sales staff, system and shipping provider", width_cm=17.2, max_h_cm=16)
portrait()
p("The decision \"allowed from the current status\" is the activity form of the order state machine (BR09). In "
  "Assignment 02 the same check was spread over three decisions (payment acceptable, stock ready, shipping "
  "available). Drawing it once, before the action is chosen, made it clear that one table of allowed transitions is "
  "enough, and that table became the class OrderStatus in the design.")

h2("2.7. Data Flow Diagram")
p("The data flow diagram takes a different view: it ignores control flow and follows the data. The context diagram "
  "of Chapter 1 shows the whole system as one process; Figure 2.11 opens it into seven processes and six data stores, "
  "with the same external entities. The processes are numbered in the order of a purchase: 1 manage accounts and "
  "customer records, 2 browse and search the catalogue, 3 manage the cart, 4 place, pay and track orders, 5 fulfil orders, "
  "6 maintain catalogue and stock, 7 produce reports. The stores D1 to D6 hold customers, the catalogue, carts, "
  "orders, payments and shipments.")
landscape()
figure("vp/png/A6.png", "Level 1 data flow diagram: seven processes, six data stores and the external entities, balanced with the context diagram", width_cm=26.5, max_h_cm=15.5)
portrait()
p("Two rules guided the drawing. Every store must be written by some process and read by another, otherwise "
  "either a requirement is missing or the store is useless; all six pass. And every flow carries a name that says "
  "which data moves, such as \"stock reservation\" from process 4 to the catalogue store. A third rule is balance "
  "with the context diagram: the flows to and from the external entities carry the names of Figure 1.4 (\"status "
  "changes, shipping data\" from the sales staff, \"product, category and promotion updates\" from the "
  "administrator), so the level 1 diagram says the same as level 0, only in more detail. A process may only send "
  "what it can build from its inputs: the reports of process 7 read the payments, the shipments, the catalogue and "
  "the orders, and the customer records that the sales staff receive come from process 1, which reads D1. The stores "
  "D1 to D5 and the Sales Staff appear a second time next to the process that uses them, as the note in the diagram "
  "says, which keeps every flow short. Two crossings remain where the stock reservation of process 4 passes the "
  "cart flows; Visual Paradigm draws them with line jumps.")

h2("2.8. Interaction Modeling: Sequence Diagram")
p("A sequence diagram shows the messages that objects exchange in one scenario. In analysis I use the boundary, "
  "control and entity stereotypes [4]: a boundary is a screen, a control coordinates one use case, an entity holds "
  "business data. The robustness rules decide who may talk to whom: the actor only to a boundary, a boundary only to "
  "a control, and an entity only to the entities it is made of. Figure 2.12 is the scenario \"add a product to the "
  "cart\" of UC06. ProductView passes the customer's choice to CartControl, which reads status and stock from the "
  "Product and only then asks the Cart to add the item. An alt fragment with three operands covers the outcomes: the "
  "product is not for sale or the quantity is above stock (refused with BR01 or BR02, the Cart is not touched), the "
  "product is already in the cart (the Cart increases the quantity of its CartItem), or it is new (the Cart adds a "
  "line with the current price). Each lifeline is active, shown by its bar, from the call it receives until its last "
  "message, so no object sends anything while it is inactive.")
landscape()
figure("vp/png/A7.png", "Analysis sequence diagram of UC06 Manage Shopping Cart, adding an item, with boundary, control and entity objects", width_cm=23.9, max_h_cm=16)
figure("vp/png/A8.png", "Analysis sequence diagram of UC07 Place Order / Checkout", width_cm=18.1, max_h_cm=16)
portrait()
p("The stock check is made by the control object, which reads the Product that holds the stock quantity; the screen "
  "never checks stock itself. The same split appears in the scenario of UC07 (Figure 2.13): CheckoutView, "
  "OrderControl and the entities Cart, Product and Order. The control reads the cart lines and the current prices, "
  "creates the Order with a «create» message, which is why the Order's lifeline starts lower, at that message, and "
  "then reserves the stock and empties the cart. Return messages "
  "are dashed lines with an open arrowhead and carry the returned value, so the reader sees at once which arrows are "
  "requests and which are answers.")

h2("2.9. Payment and Order Tracking Flows")
p("Besides checkout, two use cases shape the design of Chapter 4 more than the others: UC08 Make Payment decides "
  "what the shop may store about a card, and UC09 Track Order decides who may read an order.")
p("The payment flow (Figure 2.14) has three lanes. The system first checks the card data itself (format, Luhn check "
  "digit and expiry) and refuses invalid data before anything leaves the shop. It then checks that the order belongs "
  "to the customer and still waits for payment, and only then sends the order reference and the amount to the "
  "provider. An approved result is recorded with the last four digits and the provider's token and makes the order "
  "PAID; a declined result is recorded as well, and the order stays PENDING_PAYMENT so that the customer can try "
  "another card or give up, which cancels the order and releases the stock.")
landscape()
figure("vp/png/A3.png", "Activity diagram of UC08 Make Payment with the customer, system and payment provider lanes", width_cm=15.9, max_h_cm=16)
figure("vp/png/A9.png", "Analysis sequence diagram of UC08 Make Payment", width_cm=22.4, max_h_cm=16)
portrait()
p("Two details reach the database. The card is seen by the provider, not by the shop, so the shop has no reason to "
  "keep the card number; Chapter 4 keeps only the last four digits and the token. And a declined payment is "
  "recorded too, so one order can have several payments with different statuses. The same steps appear as messages "
  "in the analysis sequence of Figure 2.15. PaymentControl talks to the Order and creates the Payment entity; it "
  "reaches the provider through PaymentGateway, a boundary, because in the robustness rules an actor, even an "
  "external system, only talks to a boundary.")
p("The tracking flow (Figure 2.16) starts with the customer's order list. When the customer opens an order, the "
  "system first checks that it belongs to them and answers \"not found\" otherwise, the same answer as for a missing "
  "order, so nobody can learn which order numbers exist (BR08). An own order is shown with its lines, totals, "
  "payments, shipment and status history, and an order that is not processed yet can be cancelled from there.")
figure("vp/png/A4.png", "Activity diagram of UC09 Track Order", width_cm=15.8, max_h_cm=16)
p("The ownership check before any data is read becomes the rule that customer data is always queried with the "
  "customer id of the session. The status history is the reason for a new table, order_event, which the analysis "
  "model of Test 01 did not have.")

h2("2.10. Data Modeling")
p("The analysis class diagram describes concepts; the data model describes what must be stored. The class diagram of "
  "the analysis is presented in Section 4.1, where it opens the design. Here I show the step that turns it into a "
  "data model (Figure 2.17). Every class received the <<ORM Persistable>> stereotype, so Visual Paradigm can map it "
  "to a table, and typed attributes. Every relationship received multiplicities (1, 0..1, 0..*, 1..*) and a reading "
  "label such as places, contains or is paid by. The generalizations of customer and payment were kept, because "
  "they will become one table per subclass, and the product details are compositions of Product: a detail row lives "
  "and dies with its product.")
landscape()
figure("vp/png/D1.png", "Data model with ORM Persistable classes, multiplicities and relationship names", width_cm=26.5, max_h_cm=16)
figure("vp/png/D2.png", "Conceptual data model: entities and named relationships", width_cm=26.5, max_h_cm=15.5)
portrait()
p("The data model is then carried through the classic three levels. The conceptual model (Figure 2.18) names the "
  "twenty entities and the twenty-two relationships with their cardinality in crow's foot notation and says nothing "
  "about attributes, types or keys. The logical and physical levels follow in Section 4.2, where they become the "
  "tables of the database.")
p(f"Table {next_tab()} reads six of the multiplicities in plain language, which is the check I used to make sure that each "
  "one matches a business rule and not just a habit of drawing \"many\" everywhere.", keep=True)
table("Reading the multiplicities of the data model", [
    ["Relationship", "Multiplicity", "Meaning for the business"],
    ["Customer places Order", "1 to 0..*", "A customer may have no orders yet; every order has exactly one customer"],
    ["Order contains Order Item", "1 to 1..*", "An order without lines cannot exist"],
    ["Order is paid by Payment", "1 to 0..*", "No payment yet (cash on delivery, or a card not yet tried), later one or several, declined ones included"],
    ["Order is shipped by Shipping", "1 to 0..1", "At most one shipment; none before dispatch"],
    ["Category classifies Product", "1 to 0..*", "Every product is in one category; a new category may be empty"],
    ["Product is described by Book Detail", "1 to 0..1", "A product has the detail row of its category's kind, and only that one"],
], [4.6, 2.6, 8.8], size=10.5)

h2("2.11. Consistency Checks Across Models")
p("Having seven kinds of models creates a risk: each one is correct on its own, but they contradict each other. "
  f"Before moving to design I ran the checks of Table {next_tab()}. Three of them found real problems.", keep=True)
table("Consistency checks between the analysis models", [
    ["Check", "Models compared", "Result"],
    ["Every FR is covered by a use case", "Requirements, use cases", "Passed after adding UC17 (FR27)"],
    ["Every use case step that stores data has a class to store it in", "Use case specs, class model", "Found: the status history of UC09 needed Order Event"],
    ["Every message in a sequence diagram is a responsibility of the receiving class", "Sequences, class model", "Passed; the stock check is received by Product, which holds the stock"],
    ["Every DFD data store is written and read", "DFD", "Passed (D1 to D6)"],
    ["Prices used at checkout are stored historically", "Class model, data model", "Passed: cart price and order price are separate attributes"],
    ["Each cart or order line refers to exactly one product", "Class model", "Found in Test 01 (four unrelated product classes); solved by Product with Category and detail classes"],
    ["An include is needed every time, an extend only under a condition", "Use cases, activities", "Found: Make Payment is an extend of Place Order"],
], [6.6, 4.4, 5.0], size=10.5)

h2("2.12. Chapter Summary")
p("The analysis phase produced a use case model with twenty-one use cases and the specifications of the order path, "
  "five activity diagrams with swimlanes, a level 1 data flow diagram, three sequence diagrams with boundary, control "
  "and entity objects, a data model with multiplicities and a conceptual model of twenty entities. The main lesson is "
  "that the models check each other. The class model found the product problem that the use case text hid, the "
  "activity diagram of UC07 showed that payment is conditional, and the tracking flow asked for a status history "
  "that no class held. In the next chapter the same analysis approach is applied to a newer kind of requirement: "
  "features that rely on artificial intelligence.")
