# -*- coding: utf-8 -*-
# Chapter 1, sections 1.19 to 1.21: actors, use cases and the use case specifications (moved here from the
# Analysis chapter, as in the lecturer's board: the requirement chapter ends with the use case model).

h2("1.19. Actors")
p("An actor is a role that interacts with the system from outside. I derived the actors directly from the "
  "stakeholders of Section 1.4 and kept the distinction between human actors and external systems. Table " + nt() + " lists "
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

h2("1.20. Use Case Model")
p("A use case is a goal an actor reaches through the system, described from the actor's point of view. I named "
  "every use case with a verb and an object and kept them at the level of one sitting of one user: \"Place Order\" "
  "is a use case, \"Click the Confirm button\" is a step inside it and \"Run the shop\" is far too large. Table " + nt() + " "
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
h3("1.20.1. General Use Case Diagram")
p(f"Figure {nf(1)} is the general use case diagram, drawn in the Analysis file of Visual Paradigm "
  "(vp/1_Analysis.vpp). It shows all twenty-one use cases of Table 1.20 and the actors that use them. Customer use "
  "cases are on the left, the staff and management use cases on the right, and each external system is connected "
  "only to the use cases that exchange information with it. Sales Staff and Warehouse Staff are specializations of "
  "Staff, which logs in through UC02.")
landscape()
F_R2 = figure("vp/png/R2.png", "General use case diagram of ABC Online Shop: twenty-one use cases and their actors, with the include and extend relationships of UC07", width_cm=19.4, max_h_cm=16)
portrait()
p("The include and extend relationships needed the most care, and one of them changed after the design of Chapter 5. "
  "UC07 Place Order includes UC21 Validate Cart, because the cart is always checked before confirmation (FR09). UC20 "
  "Apply Promotion extends UC07 at the extension point \"promotion code entered\", because the extra behaviour only "
  "happens when the customer selects an eligible promotion. In Assignment 02 I had also drawn UC08 Make Payment as an "
  "include of UC07. The test I use for the choice is simple: if the base use case is incomplete without the other "
  "behaviour, it is an include; if the base use case is complete and the other behaviour is added only under a "
  "condition, it is an extend. Cash on delivery showed that the old choice failed this test: an order paid on "
  "delivery is complete when it is placed, and the payment only runs when the customer chooses a card. UC08 therefore "
  f"extends UC07 at the extension point \"card payment chosen\" with the condition payment method = CARD.")

h3("1.20.2. Detailed Use Case Diagrams")
p("The general diagram has 21 use cases on one page, which shows the whole system but is too dense to read the actors "
  f"of one area. Figures {nf(1)} to {nf(5)} are the detailed use case diagrams, one for each functional area of the shop: "
  "customer accounts, catalogue and inventory, shopping and payment, order fulfilment, and reviews, promotions and "
  "reports. Each repeats the use cases of its area with their actors and relationships, so a reader can check one "
  f"area at a time, and together they contain all 21 use cases and every association of Figure {F_R2}. In Figure "
  f"{nf(1)} the sales staff and the warehouse staff are linked to UC02 directly, where the general diagram links them "
  "through the actor Staff. UC04 of the catalogue area is refined once more for the AI search in Chapter 3. The nine "
  "use cases that the prototype implements are listed in Section 6.1.", keep=True)
figure("vp/png/R4.png", "Detailed use case diagram: customer accounts (diagram R4)", width_cm=13.5, max_h_cm=9)
figure("vp/png/R5.png", "Detailed use case diagram: catalogue and inventory (diagram R5)", width_cm=14.5, max_h_cm=13.5)
figure("vp/png/R6.png", "Detailed use case diagram: shopping and payment, with the include and extend relationships of UC07 (diagram R6)", width_cm=16, max_h_cm=7.5)
figure("vp/png/R7.png", "Detailed use case diagram: order fulfilment (diagram R7)", width_cm=16, max_h_cm=9)
figure("vp/png/R8.png", "Detailed use case diagram: reviews, promotions and reports (diagram R8)", width_cm=16, max_h_cm=11)

h2("1.21. Use Case Specifications")
p("A diagram shows that a use case exists; the specification says what happens inside it. I specified the six "
  "central use cases in full, the ones of the purchase path that the prototype implements and that Chapter 2 draws "
  f"as activity diagrams. Table {nt()} is the specification of UC07, the most important one. The business rules "
  "of Table 1.7 and the acceptance tests are also kept in the specification file of the project (docs/SPEC.md), so "
  "that the code and the tests cite the same rule numbers.", keep=True)
table("Use case specification UC07 Place Order / Checkout", [
    ["Item", "Description"],
    ["Use case name", "Place Order / Checkout (UC07), including Validate Cart (UC21)"],
    ["Primary actor", "Customer"],
    ["Supporting actors", "Payment Provider (through the extension UC08)"],
    ["Goal", "Purchase the selected products and receive a confirmed order"],
    ["Trigger", "Customer selects Checkout"],
    ["Preconditions", "The customer is logged in; the cart has at least one line"],
    ["Postconditions", "The order and its lines are stored with the prices of checkout; stock is reserved; the cart is empty; the order is PLACED (cash on delivery) or PENDING_PAYMENT (card)"],
    ["Main flow", "1. Customer opens checkout. 2. System validates the cart (UC21): price, status and stock of every line. 3. Customer chooses a delivery address and a payment method. 4. System shows the subtotal, the VIP discount, the shipping fee and the total (BR04). 5. Customer confirms. 6. System, in one transaction, validates the cart again, creates the order and its lines, reserves the stock (BR05) and empties the cart. 7. Cash on delivery: the order is PLACED and the confirmation is shown. Card: UC08 continues with the order PENDING_PAYMENT."],
    ["Alternative flows", "A1 A product is unavailable or not in stock: confirmation is blocked, the line is marked. A2 No address or an address of another customer: refused (BR06). A3 A price changed since the page was shown: the lines take the current price and the customer confirms the new total (BR03)."],
    ["Exceptions", "The order cannot be stored: the transaction is rolled back, nothing is reserved and the cart is unchanged"],
    ["Business rules", "BR03 to BR06; an order is never marked paid without an approved provider result (BR07, in UC08)"],
    ["Priority", "Must Have"],
], [3.2, 12.8], size=10.5)
p("Writing the specification again for the prototype changed one decision of Assignment 02. The old main flow "
  "created the order after the payment. FR14 asks that the provider's result is recorded \"against the correct "
  "order\", which needs an order reference before the provider is called, and the stock must be held while the "
  "customer types the card data. The order is therefore created first, in state PENDING_PAYMENT, and it becomes PAID "
  "only after an approved result, which keeps the original rule of A4.")

# the other five central use cases, in the same form
exec(compile(open(os.path.join(HERE, "uc_specs.py"), encoding="utf-8").read(), "uc_specs.py", "exec"))

p("Two more use cases of the implemented scope are simpler and are specified briefly: login, which every role "
  "needs, and stock maintenance by the warehouse staff.", keep=True)


def spec(title, rows):
    table(title, [["Item", "Description"]] + rows, [3.2, 12.8], size=10)


spec("Use case specification UC02 Login", [
    ["Actors", "Customer, Sales Staff, Warehouse Staff"],
    ["Pre / postconditions", "The account exists / a session holds the user's id and role; the start page of the role is open"],
    ["Main flow", "1. The user enters email and password. 2. The system checks the account (customer or staff) and the password hash. 3. The system starts a new session and opens the role's start page."],
    ["Alternative flows", "A1 Wrong email or password: one generic message that does not tell which of the two was wrong."],
    ["Rules", "Passwords stored only as hashes; a new session id at login (NFR03, NFR04)"],
])
spec("Use case specification UC15 Manage Inventory", [
    ["Actors", "Warehouse Staff"],
    ["Pre / postconditions", "The staff member is logged in with the warehouse role / the new stock quantity is stored"],
    ["Main flow", "1. The warehouse staff opens the stock list, lowest stock first. 2. The staff sets a new quantity. 3. The system stores it."],
    ["Alternative flows", "A1 A negative or non-numeric quantity: refused, the stored value is unchanged."],
    ["Rules", "Stock never becomes negative (BR12), also checked by the database; staff role required (BR13)"],
])
