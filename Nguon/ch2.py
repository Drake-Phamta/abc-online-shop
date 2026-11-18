# -*- coding: utf-8 -*-
# CHAPTER 2. ANALYSIS  (the Analysis file vp/1_Analysis.vpp: class diagram, activity diagrams, context diagram)

chapter("Analysis")
p("This chapter is the Analysis file of the project, vp/1_Analysis.vpp. The models are kept in three Visual "
  "Paradigm files, Analysis, Data Model and Design, and each file adds to the one before: Chapter 4 is the Data "
  "Model file and Chapter 5 the Design file. The Analysis file starts from the requirements, business rules and use "
  "cases of Chapter 1 and holds three kinds of model. Section 2.1 is the class diagram, the business concepts and how "
  "they are related; Section 2.2 the activity diagrams of the central use cases; Section 2.3 the context diagram, the "
  "boundary of the system and the information that crosses it. Analysis models say what the shop must know and do, "
  "not how a program stores or computes it, so they have no types, keys, screens or tables.")

# ======================================================================= 2.1
h2("2.1. Class Diagram")
p("The use cases of Section 1.20 supply the business concepts. This section names each concept, its attributes "
  "and its relationships. The analysis classes carry business meaning only: their attributes have no identifiers, "
  "no foreign keys and no types, and the diagram contains no controller, service or data access class. I first built "
  "the diagram in Test 01 from a given list of nineteen classes and corrected it after the lecturer's feedback on "
  f"Product. Figure {nf()}, on the landscape page after Table {nt(2)}, is the result: twenty classes, every association "
  "with its multiplicities and a name that reads as a sentence, such as Customer places Order. The diagram uses "
  "inheritance where one concept has several kinds: BookDetail, LaptopDetail, PhoneDetail and ApparelDetail are "
  "subclasses of Product (generalization), each with the attributes of its own kind, and Customer and Payment have "
  "two subclasses each.")

h3("2.1.1. Classes, Attributes and Responsibilities")
p("The twenty classes fall into four groups. The **customer group** describes who buys and who works in the shop. "
  "Customer is a registered buyer with a first, middle and last name, an email address, a phone number, a date of "
  "birth and a password, and Address is a delivery address of a customer, who can have several. CustomerVIP and "
  "CustomerNew are two kinds of customer: a VIP has a level, a discount rate and reward points, a new customer has a "
  "registration date and a welcome voucher. Staff is the account of a sales or a warehouse employee; it has no "
  "relationship to the other classes, because staff members act on orders and stock and do not own any of them.")
p("The **shopping group** describes what a customer intends to buy and what they bought. Cart is the customer's open "
  "basket and CartItem one line of it, with a quantity and the cart price, the price shown while the customer is "
  "still shopping. Order is created at checkout with a date, a status, a payment method and the amounts of the bill "
  "(subtotal, discount, shipping fee and total), and OrderItem is one line of it with the product name, the quantity "
  "and the unit price actually charged. OrderEvent records each status of an order with the time and the actor who "
  "caused it, because UC09 shows the history of an order. The **fulfilment group** describes what happens after "
  "checkout. Shipping is one delivery with a carrier, a tracking number, a fee, a status and the shipping and "
  "delivery dates. Payment records the method, an amount, a status and a date, and it is either PayCash (cash "
  "received and change given) or PayCredit (card holder, last four digits, expiry date and the token of the payment "
  "provider).")
p("The **product group** describes what the shop sells. Category is a tree (a category is the parent of its "
  "sub-categories) with a name, a slug for the address of its page and a detail kind that says which kind of product "
  "the category holds. Product keeps what every product has: SKU, name, brand, price, stock quantity, status and "
  "description. Every product of a book, laptop, phone or apparel category is one of four kinds, and BookDetail, "
  "LaptopDetail, PhoneDetail and ApparelDetail specialize Product: each kind is a Product and adds the attributes of "
  "its kind, such as the author of a book or the processor of a laptop. Apparel covers clothes and shoes, which "
  f"share size, colour and material. Table {nt()} lists every class with the attributes and operations of the "
  "figure.", keep=True)
table("The twenty analysis classes with their attributes and responsibilities", [
    ["Class", "Attributes", "Operations"],
    ["Category", "name, slug, detailKind", "-"],
    ["Product", "sku, name, brand, price, stockQuantity, status, description", "isAvailable(quantity), updateStock(quantity)"],
    ["BookDetail", "author, publisher, pages, language", "-"],
    ["LaptopDetail", "cpu, ramGb, storageGb, screenInch, warrantyMonths", "-"],
    ["PhoneDetail", "os, storageGb, cameraMp, screenInch, batteryMah, warrantyMonths", "-"],
    ["ApparelDetail", "sizeLabel, color, material", "-"],
    ["Customer", "firstName, middleName, lastName, email, phone, dateOfBirth, passwordHash, createdAt", "discountRate()"],
    ["CustomerVIP / CustomerNew", "vipLevel, discountRate, rewardPoints / registeredDate, welcomeVoucher", "discountRate() / -"],
    ["Address", "recipientName, phone, houseNumber, street, district, city, isDefault", "oneLine()"],
    ["Staff", "fullName, email, passwordHash, role", "-"],
    ["Cart / CartItem", "createdAt, updatedAt / quantity, cartPrice", "addItem(product, quantity), validate(), calcTotal() / subTotal()"],
    ["Order / OrderItem", "orderDate, status, paymentMethod, subtotal, discount, shippingFee, totalAmount / productName, quantity, unitPrice", "place(customer, cart, address, method), changeStatus(status), cancel() / subTotal()"],
    ["OrderEvent", "status, occurredAt, actor, note", "-"],
    ["Payment / PayCash / PayCredit", "method, amount, status, paymentDate / cashReceived, changeAmount / cardHolder, cardLast4, expiry, providerToken", "refund() / - / -"],
    ["Shipping", "carrier, trackingNumber, shippingFee, status, shippedDate, deliveredDate", "markDelivered()"],
], [3.6, 7.0, 5.4], size=9)
p("What changed since Test 01 deserves its own paragraph, because it shows how a remark about the data reached the "
  "class model. In Test 01 the product group was Book, Electronics (with Laptop and Mobile), Clothes and Shoes. Each "
  "repeated productId, price and stockQuantity, none was the parent of the others, and a cart line or an order line "
  "had to point to one of four unrelated classes, which the {xor} constraint of Test 01 expressed. The lecturer's "
  "feedback was that the details of different kinds of products should not all be kept in one Product, that "
  "products should be classified by a category, and that the kinds of products should inherit from Product. I "
  "followed it in three moves. Product keeps only the common data, Category is a class of its own, and each set of "
  "kind attributes is a subclass of Product. Clothes and Shoes had the same attributes except the material, so they "
  "became one ApparelDetail. Electronics disappeared as a class: grouping laptops and smartphones is now data, a "
  "parent category, and not structure.")
p("The effect on the rest of the model is larger than the change itself. A cart line and an order line refer to "
  "exactly one Product, so the {xor} rule is no longer needed: the four kinds inherit from Product, and a line that "
  "refers to a Product can refer to any of them. A new category with an existing kind needs no new class and, later, "
  "no new table. Price and stock are declared once, in Product, so a question about price or stock does not have to "
  "look at six classes. I considered keeping the six unrelated classes and adding Category beside them, and rejected "
  "it, because it would have left price and stock repeated six times and the {xor} in place.")
p("Two attributes deserve a comment. CartItem.cartPrice and OrderItem.unitPrice look like duplicates, but they mean "
  "different things: the cart price may still change with a promotion, while the order price is a historical fact, "
  "the price the customer actually paid. The second one is the card of PayCredit. In Test 01 the class had a "
  "cardNumber. A10 has cardLast4 and providerToken instead, because the payment activity of Section 2.2 settles that "
  "the card is seen by the provider and not by the shop.")

h3("2.1.2. Relationships")
p("Choosing the kind of each relationship is where an analysis class diagram says the most about the business. "
  f"Table {nt()} gives every relationship its kind, its multiplicity and the reason behind it. Read the multiplicity "
  "column from left to right; for example \"1 to 0..*\" between Customer and Order means that one customer places "
  "zero or more orders and every order belongs to exactly one customer.", keep=True)
T_REL = table("Relationships of the analysis class diagram", [
    ["Relationship", "Kind", "Multiplicity", "Reason"],
    ["Customer has Address", "Association", "1 to 0..*", "A new account has no address until its first order; an address belongs to one customer"],
    ["Customer owns Cart", "Association", "1 to 0..1", "A customer has at most one open cart; a cart always has its owner"],
    ["Customer places Order", "Association", "1 to 0..*", "A customer places any number of orders; each order has one customer"],
    ["Cart contains CartItem", "Composition", "1 to 0..*", "Lines live only inside their cart; an empty cart is allowed"],
    ["Order includes OrderItem", "Composition", "1 to 1..*", "Lines live only inside their order; an order without lines cannot exist"],
    ["Order records OrderEvent", "Composition", "1 to 1..*", "Every order has at least its first event; the history lives and dies with the order"],
    ["Product is put in CartItem, is sold in OrderItem", "Association", "1 to 0..*", "Each line refers to exactly one product; a product may be in no line"],
    ["Category classifies Product", "Association", "1 to 0..*", "Every product is in one category; a new category may be empty"],
    ["Category is parent of Category", "Association", "0..1 to 0..*", "A tree: a category has at most one parent"],
    ["Order is shipped by Shipping", "Association", "1 to 0..1", "One shipment per order, which does not exist before dispatch"],
    ["Order is paid by Payment", "Association", "1 to 0..*", "No payment yet for cash on delivery, later one or several, declined ones included"],
    ["Shipping is delivered to Address; Address receives Order", "Association", "1 to 0..* each", "A shipment and an order each go to one address; an old delivery keeps its address"],
    ["BookDetail, LaptopDetail, PhoneDetail, ApparelDetail to Product", "Generalization", "-", "Each kind of product is a Product and adds the attributes of its kind; the category of a product says which kind it is"],
    ["CustomerVIP, CustomerNew to Customer; PayCash, PayCredit to Payment", "Generalization", "-", "Each subclass is a kind of its parent and adds its own attributes"],
], [4.8, 2.5, 2.3, 6.4], size=9.5)
def mark_notes(fig, notes):
    """The meaning of the numbered marks of a figure, printed small under it (on the same page)."""
    p(f"The numbers in Figure {fig} mean:", size=10.5, after=1, keep=True, align=L)
    for n, text in enumerate(notes, 1):
        para = p(f"{n}  {text}", size=10.5, after=0, align=L)
        para.paragraph_format.left_indent = Cm(0.6)
        para.paragraph_format.first_line_indent = Cm(-0.4)


landscape()
F_A10 = figure("docs/evidence/marked/A10_marked.png", "Analysis class diagram of ABC Online Shop: business concepts with their attributes, operations, multiplicities and relationship names (diagram A10, twenty classes)", width_cm=25.5, max_h_cm=12)
mark_notes(F_A10, [
    "BookDetail, LaptopDetail, PhoneDetail and ApparelDetail are subclasses of Product (generalization): each keeps only the attributes of its kind.",
    "Product keeps what every kind shares; as an analysis class it has no types and no identifier.",
    "Category is a class of its own and a tree (is parent of); its detailKind says which subclass its products have.",
    "CustomerNew and CustomerVIP are the two kinds of Customer; only a VIP has a discount rate (BR04).",
    "Payment is abstract (italic name): a payment is always PayCash or PayCredit, and PayCredit keeps the last four digits and a token, never the card number (BR07).",
])
portrait()

h3("2.1.3. Design Decisions Visible in the Model")
dash("**Checkout is a responsibility, not an association.** An association between Cart and Order would claim that "
     "every order remembers the cart it came from, which is not true: the cart is emptied after checkout. The "
     "operation Order.place(customer, cart, address, method) says exactly what happens: during checkout the cart is "
     "used to create the order.")
dash("**An order keeps its own copy of what was bought.** OrderItem keeps the product name and the unit price of "
     "the moment of purchase, so a later change of a price or a name in the catalogue does not alter a past purchase "
     "(BR03). The Order refers to the Address of the customer that it goes to (BR06).")
dash("**A product has one category and at most one kind.** The attributes of a kind sit in its subclass, so Product "
     "keeps only what every product has, and a product of a category without its own attributes is a plain Product.")

# ======================================================================= 2.2
h2("2.2. Activity Diagram")
p("Each of the central use cases specified in Section 1.21 that changes data has one activity diagram: UC06, UC07, "
  "UC08, UC09 and UC14. UC04, the search, reads data only; its flow is the subject of Chapter 3. The lanes show who "
  "acts, and the diamonds show where the flow splits, with the condition of each branch written on its flow "
  "([blocking issue], [no blocking issue]) and the decision node itself left unnamed, which is the UML way.")

h3("2.2.1. Manage Shopping Cart")
p(f"Figure {nf()} is the activity of UC06. A guest is sent to the login first, a product that is not for sale or a "
  "quantity above stock is refused with the reason, and the two branches [already in the cart] and [new product] "
  "meet again in a merge node before the cart is saved. Every loop back also ends in a merge node, never directly on "
  "an action: in UML an action with two incoming flows waits for both (an implicit join), so the customer who "
  "updates the cart could never open checkout again.")
figure("vp/png/A1.png", "Manage Shopping Cart (UC06) activity diagram", width_cm=16, max_h_cm=21.5)

h3("2.2.2. Place Order / Checkout")
p(f"Figure {nf()} is the activity of UC07. The customer lane holds what the customer does, the Shop System lane what "
  "the system does. Its four decisions are the alternative flows of the UC07 specification in Section 1.21: a "
  "blocking issue sends the customer back to the cart, a changed price is taken over before the totals are shown, a "
  "failed transaction (total changed or a product just sold out) asks the customer to confirm again, and the payment "
  "method decides between the two endings.")
figure("vp/png/A2.png", "Place Order / Checkout (UC07) activity diagram", width_cm=16, max_h_cm=21.5)

h3("2.2.3. Make Payment")
p(f"The payment activity (Figure {nf()}) has three lanes. The system first checks the card data itself (format, "
  "Luhn check digit and expiry) and refuses invalid data before anything leaves the shop. It then checks that the "
  "order belongs to the customer and still waits for payment, and only then sends the order reference and the "
  "amount to the provider. An approved result is recorded with the last four digits and the provider's token and "
  "makes the order PAID; a declined result is recorded as well, and the order stays PENDING_PAYMENT so that the "
  "customer can try another card or give up, which cancels the order and releases the stock. Two details reach the "
  "data model: the shop keeps only the last four digits and the token, and one order can have several payments.")
landscape()
figure("vp/png/A3.png", "Make Payment (UC08) activity diagram with the customer, system and payment provider lanes", width_cm=15.9, max_h_cm=16)
portrait()

h3("2.2.4. Track Order")
p(f"The tracking activity (Figure {nf()}) starts with the customer's order list. When the customer opens an order, "
  "the system first checks that it belongs to them and answers \"not found\" otherwise, the same answer as for a "
  "missing order, so nobody can learn which order numbers exist (BR08). An own order is shown with its lines, "
  "totals, payments, shipment and status history, and an order that is not processed yet can be cancelled from "
  "there. The status history is the reason for the class OrderEvent.")
figure("vp/png/A4.png", "Track Order (UC09) activity diagram", width_cm=15.8, max_h_cm=16)

h3("2.2.5. Process Orders")
p(f"Order processing involves three parties, and the lanes of Figure {nf()} show the handoffs between them: the "
  "sales staff choose an order and an action, the Shop System checks that the action is allowed from the current "
  "status, and the Shipping Provider carries the parcel. A refused action ends with the allowed actions shown; "
  "process and cancel end in the system lane; ship continues with the carrier and the tracking number, the shipment "
  "record, the delivery by the carrier and the confirmation by the staff. The decision \"allowed from the current "
  "status\" is the activity form of the order state machine (BR09): one table of allowed transitions, which became "
  "the class OrderStatus in the design.")
landscape()
figure("vp/png/A5.png", "Process Orders (UC14) activity diagram: sales staff, system and shipping provider", width_cm=17.2, max_h_cm=16)
portrait()

# ======================================================================= 2.3
h2("2.3. Context Diagram")
p("Inside the software boundary lie customer accounts, the catalogue with browsing, search and the cart, order "
  "management and tracking, inventory, payment and shipping status, promotions, reviews and reports. Outside it lie "
  "the payment provider's transaction processing, the shipping provider's logistics, the supplier's own systems and "
  "the people who use the system. Payment and shipping are inside the scope only as status integration: the system "
  "sends requests and records results.")
p(f"Figure {nf()} shows the information that crosses this boundary. The system is one process, surrounded by eight "
  "external entities: the customer and the four staff roles on one side and the three partner organizations on the "
  "other, with one named data flow in each direction. My Assignment 01 version had six entities with one combined "
  "Administrator / Staff; the administrator, the sales staff and the warehouse staff exchange different data with "
  "the system (catalogue updates, order status changes, stock updates), so the combined entity became three.")
landscape()
figure("vp/png/R1.png", "System context diagram of ABC Online Shop: the system, its eight external entities and the data that crosses the boundary (diagram R1)", width_cm=26.5, max_h_cm=14)
portrait()
p(f"Table {nt()} lists the flows of each external entity, together with the use cases of Chapter 1 in which they "
  "occur.", keep=True)
table("Information flows between the system and its external entities", [
    ["External entity", "Flows into the system", "Flows out of the system", "Use cases"],
    ["Customer", "Account, search, cart and order data", "Products, confirmations, order status", "UC01 to UC10, UC20"],
    ["Administrator", "Product, category and promotion updates", "Catalogue and review lists", "UC11 to UC13"],
    ["Sales Staff", "Status changes, shipping data", "Orders to process, customer records", "UC14, UC16, UC17"],
    ["Warehouse Staff", "Stock updates", "Stock levels", "UC15"],
    ["Manager", "Report requests", "Sales, stock and order reports", "UC18"],
    ["Payment Provider", "Transaction result", "Payment request", "UC08"],
    ["Shipping Provider", "Shipment status", "Delivery information", "UC16"],
    ["Supplier", "Product and supply information", "Replenishment requests", "UC19"],
], [3.2, 4.6, 4.6, 3.6], size=10)
p("The boundary looked like a formality at the time, but it saved work later. Because card processing is outside it, "
  "the payment use case only sends a request and records a status, and the Payment class of Chapter 5 has no "
  "card-handling logic.")

h2("2.4. Chapter Summary")
p("The Analysis file holds the class diagram with twenty business classes, the activity diagrams of the five "
  "central use cases that change data, and the context diagram with eight external entities. The main lesson is that "
  "the models check each other: the class model found the product problem that the use case text hid, the activity "
  "of UC07 showed that payment is conditional, and the tracking flow asked for a status history that no class held. "
  "Chapter 4 continues the class diagram into the Data Model file, after Chapter 3 applies the same analysis to the "
  "AI feature of the shop.")
