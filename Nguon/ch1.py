# -*- coding: utf-8 -*-
# CHAPTER 1. REQUIREMENT DETERMINATION  (built on Assignment 01 and the requirement part of Assignment 02)

chapter("Requirement Determination")
p("Requirement determination answers two questions before any diagram is drawn: what is wrong with the way the "
  "business handles its information today, and what exactly a new system must do about it. In this chapter I "
  "follow the order I used in Assignment 01 and Assignment 02: first I investigate ABC Online Shop as a business "
  "(context, stakeholders, activities, information and problems), then I fix the scope and boundary of the system, "
  "and only then do I write requirements, prioritize them, check their quality and trace them back to the "
  "problems they are supposed to solve.")

h2("1.1. Requirements in the Development Life Cycle")
p("In the classic life cycle [2], requirement determination is the first activity of the "
  "analysis phase. Its output "
  "is the input of everything else: analysts build use cases and class models from it, designers choose an "
  "architecture that can satisfy it, programmers implement it and testers write test cases against it. An error "
  "made here is therefore the most expensive kind of error, because it is copied into every later artifact. When "
  "I wrote the code for Design 01 at the end of September, I could still see decisions that came from the very "
  "first table of Assignment 01, for example the decision that the shop records a payment status but does not "
  "execute card transactions itself.")
p("The course distinguishes three levels that are easy to mix up. A **business need** describes what the "
  "organization wants to achieve (for example, management needs timely sales information). A **requirement** "
  "describes a capability or a quality the system must have to meet that need (the system shall generate sales "
  "reports from current order data). A **design decision** describes how the requirement is met (a reporting "
  "service reads the order table every night). Requirement determination stops at the second level. Whenever I "
  "caught myself writing about tables, screens or programming languages in this phase, I moved the sentence to a "
  "note for the design chapter.")
p("A second distinction is between functional and non-functional requirements [3]. Functional requirements say what "
  "the system does: register a customer, validate a cart, record a shipment status. Non-functional requirements "
  "say how well it must do it: response time, availability, security, maintainability. Both kinds must be "
  "testable. A requirement that cannot be checked by a test or an inspection is only a wish, and Section 1.14 shows "
  "three wishes from my first draft and how I rewrote them.")

h2("1.2. Investigation Approach")
p("ABC Online Shop is a course case, not a real company, so I could not interview its employees. I treated the "
  "case description as the main source and applied the investigation techniques of the course to it as far as "
  "they make sense. Table 1.1 lists the techniques I considered, what each one would contribute in a real project "
  "and how I used it here. Being explicit about this matters: several statements in the requirements are "
  "assumptions derived from the case, and a real project would have to confirm them with the shop's staff before "
  "treating them as agreed requirements.", keep=True)
table("Fact-finding techniques considered for ABC Online Shop", [
    ["Technique", "What it gives in a real project", "How I applied it in the course"],
    ["Document analysis", "Existing forms, reports, order slips, policies", "Main source: the case description and the brief of each assignment"],
    ["Interviews", "Goals, problems and exceptions in the words of each role", "Simulated by writing one need statement per stakeholder (Table 1.6)"],
    ["Observation", "How work is really done, including workarounds", "Not possible; replaced by walking through the order lifecycle step by step"],
    ["Questionnaires", "Opinions of many customers at low cost", "Not used; noted as a way to validate NFR05 (usability) later"],
    ["Joint workshop", "Shared agreement on scope and priorities", "Replaced by the MoSCoW table and the scope list reviewed with classmates"],
    ["Prototyping", "Early feedback on screens and AI behavior", "Used for the AI features: the recommender and the search prototype"],
], [3.3, 6.2, 6.5], size=10.5)
p("The investigation then follows a fixed sequence that keeps every later statement traceable: business context, "
  "stakeholders and activities, information, current problems, and finally scope and objectives. Each step uses the "
  "result of the step before it, so a problem in Section 1.6 always points to an activity in Section 1.3 and to the "
  "information it damages in Section 1.5.")

h2("1.3. Business Context and Activities")
p("ABC Online Shop is a medium-sized business-to-consumer retailer. Customers browse products, put items into a "
  "shopping cart, place orders, pay, receive deliveries and may later write reviews. Behind this customer journey "
  "the shop maintains products and categories, customer records, stock, promotions and reports, and it exchanges "
  "information with three external parties: suppliers, a payment provider and a shipping provider. The case does "
  "not name a product specialization, so I kept the product domain generic; later, when the AI prototypes needed "
  "concrete data, I created small catalogues of shoes, bags, clothes and computer accessories.")
p("The shop's objectives, as I read them from the case, are to process orders accurately and quickly, to keep its "
  "business information consistent, to give customers reliable availability and order status, and to give "
  "management timely sales and inventory information. Table 1.2 lists the eleven business activities that serve "
  "these objectives.", keep=True)
table("Major business activities of ABC Online Shop", [
    ["Activity", "Role in the business"],
    ["Product and category management", "Maintain descriptions, categories, prices and availability used by customers and staff"],
    ["Customer management", "Maintain registration, contact and account information needed for service and orders"],
    ["Product browsing", "Present product and category information so customers can search and compare"],
    ["Shopping cart", "Collect selected products and quantities temporarily before the order"],
    ["Order processing", "Turn a purchase decision into an order and coordinate stock, payment, fulfilment and status"],
    ["Payment management", "Exchange payment requests and results with the external payment provider"],
    ["Inventory management", "Keep stock quantities and update them when products are reserved, sold or replenished"],
    ["Shipping management", "Send delivery information to the shipping provider and track the returned status"],
    ["Promotion management", "Maintain promotions and apply their conditions consistently"],
    ["Review management", "Collect and manage customer feedback after a purchase"],
    ["Reporting", "Consolidate sales, order and stock information for management"],
], [5.2, 10.8], size=10.5)
p("These activities are not independent. Figure 1.1 is the high-level business process. In Assignment 01 I drew it "
  "as a chain of eight boxes; for this version I modelled it in Visual Paradigm as a BPMN collaboration [12], because a "
  "chain of boxes cannot show who does each step or where the shop waits for a partner. Each participant is a pool: "
  "the customer, the shop with one lane per role, and the payment and shipping providers, drawn as black boxes "
  "because only their messages matter to the shop. Sequence flows (solid) stay inside a pool, message flows (dashed, "
  "with a small circle at the sender) cross between pools: the customer's order starts the shop's process, the "
  "payment provider answers the payment request, and the shipping provider reports the delivery status, which the "
  "shop passes on to the customer. The dotted data associations are the reporting path of Assignment 01: updating "
  "the stock writes the order and stock records, and the manager's reporting reads them. Reporting is a process of "
  "its own with its own start event, so a report shows the stock after every order, not only at the end of the day.")
landscape()
figure("vp/png/B1.png", "High-level business process of ABC Online Shop as a BPMN collaboration: pools, lanes, sequence flows and message flows (diagram B1)", width_cm=25.5, max_h_cm=15.5)
portrait()
p("Order processing is the activity with the most connections: it reads product, price, promotion and stock data, "
  "writes order and payment records, and hands work to the warehouse and to the shipping provider. When I later "
  "chose which use cases to specify in detail (Chapter 2), I started from this activity for exactly that reason.")

h2("1.4. Stakeholder Analysis")
p("A stakeholder is anyone who uses the system, provides information to it or is affected by its results. I "
  "classified the stakeholders as internal (people inside the shop) or external (customers and partner "
  "organizations). Table 1.3 lists them with their role and their main interest; Figure 1.2 is the stakeholder map, "
  "drawn with the motivation elements of ArchiMate [13]: a stakeholder is associated with the concern (driver) it has, "
  "and an influence arrow shows that one concern depends on another.", keep=True)
table("Stakeholders, roles and interests", [
    ["Stakeholder", "Type", "Role", "Main interest"],
    ["Customer", "External", "Browses, buys, pays, tracks orders, writes reviews", "Correct product and stock data, reliable payment, clear delivery status"],
    ["Administrator", "Internal", "Maintains catalogue, promotions and reviews", "Controlled, efficient maintenance of accurate data"],
    ["Sales Staff", "Internal", "Handles orders and customer records", "Complete, current customer, order and payment data"],
    ["Warehouse Staff", "Internal", "Manages stock and prepares orders", "Accurate quantities, clear picking needs, timely updates"],
    ["Manager", "Internal", "Monitors performance and decides", "Timely sales, stock and exception information"],
    ["Supplier", "External", "Provides products and supply data", "Clear replenishment information"],
    ["Payment Provider", "External", "Processes electronic payments", "Correct requests, unambiguous result exchange"],
    ["Shipping Provider", "External", "Delivers and returns shipment status", "Correct recipient data and status exchange"],
], [3.0, 1.9, 5.3, 5.8], size=10.5)
figure("vp/png/B2.png", "Stakeholder map in ArchiMate notation: internal and external stakeholders and the concerns they share (diagram B2)", width_cm=16, max_h_cm=10)
p("The map in Assignment 01 only placed the stakeholders around the shop. Drawing their concerns showed what the "
  "table alone hides: eight stakeholders share only two kinds of operational information, accurate product, price "
  "and stock data, and the current status of orders, payments and deliveries. The manager's concern, timely sales "
  "and stock information, is not a third source at all; the influence arrows show that it is built from the other "
  "two. The stakeholders therefore depend on each other through shared information. Warehouse staff can only pick an "
  "order if the order record is correct; sales staff can only "
  "answer a customer if the payment and shipping status are current; the manager's report is only as good as all "
  "of these records together. A weakness in one source of information therefore hurts several stakeholders at once, "
  "and this observation became the core argument for an integrated system rather than a set of separate tools.")
p("I also decided early which stakeholders are actors of the future system. Customers, administrators, sales "
  "staff, warehouse staff and managers interact with it directly. The payment and shipping providers interact with "
  "it as external systems. The supplier was the uncertain case: in a small shop supply information often arrives by "
  "e-mail and is typed in by staff. I kept the supplier as an actor that provides supply information (UC19 in "
  "Chapter 2) because the case lists supply coordination as a business activity, but I marked the related "
  "requirement FR28 as Should Have rather than Must Have.")

h2("1.5. Information Analysis")
p("An information system exists to produce, store and exchange information, so after the people and activities I "
  "listed the information itself. I grouped it by what happens to it:")
dash("**Produced**: order confirmations, payment records, order status updates, shipping notifications, sales and "
     "inventory reports, management summaries.")
dash("**Consumed**: product and category data, customer details, cart contents, stock availability, payment "
     "results, shipment status, promotions, reviews and supplier information.")
dash("**Stored**: customer, product and category records, carts, orders, payment status, inventory, shipments, "
     "promotions, reviews and reporting data.")
dash("**Exchanged across the boundary**: registration and login data, order and payment requests, payment results, "
     "delivery data, shipment status, supply data and reports.")
p("Table 1.4 is the information catalogue. Its value is in the second and third columns: almost every information "
  "item is maintained by one role but used by several others, which is the situation in which separate "
  "spreadsheets drift apart.", keep=True)
table("Information catalogue", [
    ["Information", "Maintained by", "Used by", "Purpose"],
    ["Product / category", "Administrator, staff", "Customer, sales staff, system", "Browsing, search, ordering, catalogue upkeep"],
    ["Customer", "Customer, authorized staff", "Sales staff, order, shipping", "Account, ordering, contact, delivery"],
    ["Shopping cart", "Customer, system", "Customer, order process", "Hold selected products before checkout"],
    ["Order", "Customer, system", "Sales, warehouse, payment, shipping, manager", "Confirmation, fulfilment, tracking"],
    ["Inventory", "Warehouse staff, system", "Customer functions, order, warehouse, manager", "Availability check and stock control"],
    ["Payment", "Payment provider, system", "Order, sales staff, customer, reports", "Confirm transaction result"],
    ["Shipment", "Shipping provider, system", "Customer, sales staff, manager", "Delivery and status tracking"],
    ["Promotion", "Administrator", "Customer, cart and order, reports", "Communicate and apply promotions"],
    ["Review", "Customer", "Administrator, customers, manager", "Feedback and product evaluation"],
    ["Sales / inventory reports", "System", "Manager, warehouse staff", "Monitoring and decision support"],
], [3.2, 3.6, 4.6, 4.6], size=10.5)

h2("1.6. Current Problems")
p("The case describes seven problems. When I first read them they looked like a list of unrelated complaints. "
  "Writing the likely cause next to each one (Table 1.5) showed that they share three root causes: information is kept in separate places, many updates are made by "
  "hand, and data is maintained inconsistently. Figure 1.3 is the problem tree that summarizes this "
  "reasoning: three root causes at the bottom, one central problem in the middle and three groups of consequences "
  "at the top. Each box is an ArchiMate assessment, the result of analysing a state of affairs, and each arrow is an "
  "influence that reads \"contributes to\".", keep=True)
table("Current problems, likely causes and consequences", [
    ["Problem", "Likely cause", "Business consequence"],
    ["Inconsistent product information", "Details kept by different staff or in different files", "Conflicting information, time spent on corrections, lower trust"],
    ["Outdated inventory information", "Stock changes updated manually or late", "Orders for unavailable products, cancellations, manual exceptions"],
    ["Manual order processing", "Steps need staff intervention instead of one flow", "Slow, error-prone processing; order states differ by department"],
    ["Unclear order status", "Order, payment, warehouse and shipping status not synchronized", "Customers cannot get reliable status and call staff instead"],
    ["Manual sales reporting", "Data collected and combined by hand", "Late reports with reconciliation errors"],
    ["Fragmented customer information", "Customer records stored in several places", "Duplicates and outdated contact data"],
    ["Limited real-time management information", "Separated data, manual consolidation", "Managers see problems late and decide late"],
], [4.0, 5.6, 6.4], size=10.5)
figure("vp/png/B3.png", "Problem tree in ArchiMate notation: root causes, central problem and consequences (diagram B3)", width_cm=16, max_h_cm=10)
p("The tree changed how I wrote the requirements. Instead of answering each symptom separately (a better report "
  "here, a status screen there), the requirements aim at the root causes: one shared source of data and automated "
  "updates triggered by business events. Most of the functional requirements in Section 1.10 can be read as "
  "\"when event X happens, the system updates record Y\", and that is a direct consequence of the problem tree.")

h2("1.7. Scope, Boundary and Context")
p("With the problems understood, the next decision is how much of the business the system should cover. I "
  "separated the decision into scope (what the system does) and boundary (what it does not do and leaves to "
  "others). The scope includes customer accounts, the product catalogue with browsing, search and cart, order "
  "management and status tracking, inventory information, promotions, reviews and reporting. Payment and shipping "
  "are inside the scope only as **status integration**: the system sends requests and records results, but the "
  "payment provider executes the transaction and the shipping provider moves the parcel.")
p("Outside the boundary are the payment provider's transaction processing, the shipping provider's logistics, the "
  "supplier's own systems and any activity that does not serve the listed information needs. People are outside "
  "the software boundary too, even when they use the system every day. Figure 1.4 shows the context diagram: the "
  "system is one process, surrounded by eight external entities, the four staff roles and the customer on one side "
  "and the three partner organizations on the other, with one named data flow in each direction. My Assignment 01 "
  "version had six entities with one combined Administrator / Staff. Drawing it again as a level 0 data flow "
  "diagram, the starting point of the level 1 DFD in Section 2.7, showed that the administrator, the sales staff and "
  "the warehouse staff exchange different data with the system (catalogue updates, order status changes, stock "
  "updates), so the combined entity became three.")
landscape()
figure("vp/png/R1.png", "Context diagram (level 0 data flow diagram) with the external entities and their data flows", width_cm=26.5, max_h_cm=14)
portrait()
p("The boundary looked like a formality at the time, but it saved work later. Because card processing is outside "
  "the boundary, the payment use case in Chapter 2 only sends a request and records a status, the Payment class in "
  "Chapter 4 has no card-handling logic, and the security requirement NFR03 is about access to order data, not about "
  "card encryption. A wider boundary would have pulled a whole payment-security analysis into a course project.")

h2("1.8. System Objectives")
p("The last step of the investigation turns the problem tree into objectives. I wrote seven, each tied to at least "
  "one problem, so that the requirements that follow can be checked against them:")
num(1, "Keep one consistent source of product, customer, order, inventory, payment-status and shipment data.")
num(2, "Keep stock availability synchronized with orders and warehouse activity.")
num(3, "Coordinate validation, availability checking, payment status and fulfilment in one order flow.")
num(4, "Give customers and staff accurate order, payment and shipping status without manual checking.")
num(5, "Integrate with the payment and shipping providers while keeping their internal processing outside.")
num(6, "Produce sales, inventory and order reports directly from current operational data.")
num(7, "Support controlled promotion and review management linked to products, customers and orders.")

h2("1.9. From Stakeholders to Needs")
p("Assignment 02 continued from here. Before writing \"the system shall\" statements I wrote one need per "
  "stakeholder interest, each with the business basis that justifies it. This intermediate layer is easy to skip, "
  "but it is what makes traceability possible: a requirement without a need behind it is either gold-plating or a "
  "need I forgot to write down. Table 1.6 lists the fourteen stakeholder needs.", keep=True)
table("Stakeholder needs (Assignment 02)", [
    ["ID", "Stakeholder", "Need", "Business basis"],
    ["SN01", "Customer", "Accurate product, price, category and availability before purchase", "Inconsistent product data; outdated stock"],
    ["SN02", "Customer", "Browse and search the catalogue efficiently", "Product browsing"],
    ["SN03", "Customer", "Keep selected products and quantities before checkout", "Shopping cart"],
    ["SN04", "Customer", "Place an order through a controlled checkout and get confirmation", "Manual order processing"],
    ["SN05", "Customer", "Reliable payment information linked to the right order", "Payment coordination"],
    ["SN06", "Customer", "See current order and delivery status without asking staff", "Unclear order status"],
    ["SN07", "Customer", "Give product feedback after purchase", "Review management"],
    ["SN08", "Administrator", "Maintain consistent product, category, promotion and review data", "Inconsistent maintenance"],
    ["SN09", "Sales Staff", "Use central customer and order data to process orders", "Manual processing; fragmented customers"],
    ["SN10", "Warehouse Staff", "Access and update accurate stock data", "Outdated inventory"],
    ["SN11", "Manager", "Timely sales, inventory, order and operational information", "Manual, slow reporting"],
    ["SN12", "Payment Provider", "Correct payment requests; unambiguous status return", "Payment integration"],
    ["SN13", "Shipping Provider", "Correct delivery data; status return", "Shipping integration"],
    ["SN14", "Supplier", "Provide product and replenishment information for recording", "Supply coordination"],
], [1.4, 2.9, 7.0, 4.7], size=10, center_cols=(0,))

h2("1.10. Functional Requirements")
p("Each functional requirement is one \"The system shall ...\" sentence with one actor and one observable result, so "
  "that it can be tested on its own. I grouped them by business area and gave each a MoSCoW priority. Table 1.7 "
  "lists all twenty-eight; the wording is shortened slightly to fit the table, the full sentences are in Assignment "
  "02.", keep=True)
table("Functional requirements FR01 to FR28", [
    ["ID", "Area", "The system shall ...", "Priority"],
    ["FR01", "Account", "let customers register an account with the required customer information", "Must"],
    ["FR02", "Account", "let registered customers log in before account-specific functions", "Must"],
    ["FR03", "Account", "let authenticated customers view and update their own profile", "Should"],
    ["FR04", "Product", "present current product and category information for browsing", "Must"],
    ["FR05", "Product", "let customers search the product catalogue", "Must"],
    ["FR06", "Product", "show product details, price, applicable promotion and current availability", "Must"],
    ["FR07", "Cart", "let customers add selected products and quantities to a cart", "Must"],
    ["FR08", "Cart", "let customers change quantities or remove products before checkout", "Must"],
    ["FR09", "Cart", "validate cart items against current product, price, promotion and stock at checkout", "Must"],
    ["FR10", "Order", "let a customer submit a checkout request with cart and delivery information", "Must"],
    ["FR11", "Order", "create a uniquely identifiable order and show confirmation on success", "Must"],
    ["FR12", "Order", "let customers view the status and history of their own orders", "Must"],
    ["FR13", "Order", "let authorized sales staff view and update order-processing status", "Must"],
    ["FR14", "Payment", "send a payment request and record the returned status against the correct order", "Must"],
    ["FR15", "Inventory", "check stock availability before an order is confirmed", "Must"],
    ["FR16", "Inventory", "update stock after confirmed orders and authorized warehouse changes", "Must"],
    ["FR17", "Shipping", "send required order and delivery information to the shipping provider", "Must"],
    ["FR18", "Shipping", "record the returned shipment status and show it to relevant users", "Must"],
    ["FR19", "Promotion", "let administrators create, update, activate and deactivate promotions", "Could"],
    ["FR20", "Promotion", "apply an eligible promotion when its conditions are met", "Could"],
    ["FR21", "Review", "let customers submit a review linked to a purchased product", "Should"],
    ["FR22", "Review", "let administrators view and manage submitted reviews", "Could"],
    ["FR23", "Reporting", "generate sales reports from current order data", "Must"],
    ["FR24", "Reporting", "generate inventory reports from current stock data", "Should"],
    ["FR25", "Reporting", "generate order and operational-status reports for management", "Should"],
    ["FR26", "Administration", "let administrators maintain product and category records", "Must"],
    ["FR27", "Customer", "let authorized sales staff maintain customer records", "Should"],
    ["FR28", "Supplier", "record product and replenishment information from suppliers", "Should"],
], [1.4, 2.4, 10.4, 1.8], size=10, center_cols=(0, 3))
p("Two requirements took more thought than the others. FR09 (validate the cart at checkout) exists because a cart "
  "can live for days while prices, promotions and stock change; without FR09, the order would silently use stale "
  "data, which is precisely the \"outdated inventory\" problem. FR14 is written carefully around the boundary: it "
  "sends a request and records a status, and it says \"against the correct order\" because a payment result that "
  "cannot be matched to its order is worse than no result at all.")

h2("1.11. Non-functional Requirements")
p("Non-functional requirements were the hardest part to write well, because the natural first version of each one "
  "is an adjective (fast, secure, reliable). I forced every NFR to contain a measurable condition or a checkable "
  "rule. Table 1.8 lists the ten NFRs.", keep=True)
table("Non-functional requirements NFR01 to NFR10", [
    ["ID", "Category", "Requirement", "Priority"],
    ["NFR01", "Performance", "95% of normal product searches return results within 3 s with up to 200 concurrent users", "Must"],
    ["NFR02", "Performance", "95% of order-status requests return within 3 s with up to 200 concurrent users", "Should"],
    ["NFR03", "Security", "Authenticated access is required before customers view or change profile or order data", "Must"],
    ["NFR04", "Security", "Administrative, sales, warehouse and management functions are restricted to authorized roles", "Must"],
    ["NFR05", "Usability", "Browse/search, cart, checkout and order tracking are each reachable within three navigation actions", "Should"],
    ["NFR06", "Availability", "The customer-facing service reaches 99.5% monthly availability, excluding announced maintenance", "Should"],
    ["NFR07", "Reliability", "Confirmed orders and recorded payment/shipment status survive a restart or recoverable failure", "Must"],
    ["NFR08", "Scalability", "NFR01 and NFR02 still hold when catalogue size and concurrent users double", "Should"],
    ["NFR09", "Maintainability", "Major functional areas are separable so a change in one does not require unrelated changes", "Should"],
    ["NFR10", "Data integrity", "Order confirmation is blocked when product, quantity, price, stock, delivery or payment linkage data is missing or invalid", "Must"],
], [1.5, 2.7, 10.0, 1.8], size=10, center_cols=(0, 3))
p("NFR09 deserves a comment because it looked weak at first: \"separable\" is hard to measure. I kept it because it "
  "can be checked by inspection, and in Chapter 5 it became automated checks. The shop application is checked against "
  "its three-layer design class by class, and the same check fails if a class of the AI package imports any other "
  "part of the application, which are concrete, repeatable checks of exactly this requirement.")

h2("1.12. Requirement Cards and Acceptance Criteria")
p("A one-line requirement is good for a table but too short for the people who must build and test it. For the "
  "requirements on the order path I kept a fuller record, a requirement card, with the attributes that the course "
  "recommends: source, rationale, fit criterion, dependencies and status. Table 1.9 is the card for FR09, the "
  "requirement that caused the most discussion.", keep=True)
table("Requirement card for FR09 Validate cart at checkout", [
    ["Attribute", "Value"],
    ["Statement", "The system shall validate cart items against current product, price, promotion and stock information when checkout begins."],
    ["Source", "SN04 (controlled checkout), SN01 (accurate availability); problem \"outdated inventory information\""],
    ["Rationale", "A cart may live for days. Prices, promotions and stock change in the meantime; the order must be built from current data, not from the data seen when the item was added."],
    ["Fit criterion", "For a cart containing a product whose stock is now lower than the cart quantity, checkout stops and the customer is asked to change the cart; no order is created."],
    ["Priority", "Must have"],
    ["Dependencies", "FR06 (current price and availability), FR15 (stock check), NFR10 (data integrity)"],
    ["Use case", "UC21 Validate Cart, included by UC07 Place Order / Checkout"],
    ["Status", "Agreed in Assignment 02; implemented as Cart.validate(), which asks each product whether it is available and takes over changed prices (Chapters 4 and 5); tested by validationTakesOverChangedPrices and placingNeedsAnOwnAddressAndEnoughStock (Chapter 5)"],
], [3.3, 12.7], size=10.5)
p("The fit criterion is the most useful line on the card. It turns the requirement into something a tester can try "
  "and a programmer can aim at. I wrote acceptance criteria in the Given, When, Then form for the other Must Have "
  "requirements of the order path; Table 1.10 shows six of them. Each one has at least one negative case, because "
  "most defects in order processing hide in the paths where something is missing or invalid.", keep=True)
table("Acceptance criteria for key requirements", [
    ["Req.", "Given", "When", "Then"],
    ["FR11", "a valid cart and accepted payment status", "the customer confirms the order", "an order with a new unique id is stored and a confirmation is shown"],
    ["FR12", "customer C001 is logged in; order O002 belongs to customer C002", "C001 asks for order O002", "the result is empty (\"not found\"); the same request from C002 returns O002"],
    ["FR14", "an order waiting for payment", "the provider returns \"declined\"", "the payment status is recorded as failed and the order is not marked paid"],
    ["FR15", "a product with stock 1 and a cart with quantity 2", "checkout starts", "confirmation is blocked and the customer is asked to change the quantity"],
    ["FR16", "a confirmed order for 2 units of a product with stock 10", "the order is confirmed", "the recorded stock becomes 8; it never becomes negative"],
    ["NFR10", "an order without delivery address", "the customer tries to confirm", "the system refuses and names the missing field"],
], [1.4, 4.6, 4.1, 5.9], size=10, center_cols=(0,))
p("Writing these criteria had a side effect on the analysis. The criterion for FR12 forced me to decide what "
  "happens when a customer asks for someone else's order. The answer, \"not found\" rather than \"forbidden\", does "
  "not reveal that the order exists, and the same rule reappeared a few weeks later in the order search of "
  "Assignment 06, where a customer can only find his or her own orders.")

h2("1.13. Prioritization")
p("Not every requirement can be built first. I used the MoSCoW scheme, and the deciding question for each "
  "requirement was simple: can the shop take and fulfil an order without it? Everything on the path from browsing "
  "to a confirmed, paid and shipped order is Must Have; things that make the shop better but not functional are "
  "Should or Could Have. Table 1.11 shows the result.", keep=True)
table("MoSCoW prioritization of the requirements", [
    ["Priority", "Requirements and scope decisions"],
    ["Must have", "FR01, FR02, FR04 to FR18, FR23, FR26; NFR01, NFR03, NFR04, NFR07, NFR10"],
    ["Should have", "FR03, FR21, FR24, FR25, FR27, FR28; NFR02, NFR05, NFR06, NFR08, NFR09"],
    ["Could have", "FR19, FR20, FR22 (promotion management and review moderation)"],
    ["Won't have (now)", "Payment provider's transaction execution; physical logistics; supplier's internal systems; functions not linked to any problem in Section 1.6"],
], [3.2, 12.8], size=10.5)
p("Promotions ended up as Could Have, which surprised me at first because promotions are visible to every "
  "customer. The reason is that none of the seven problems in the case is about promotions; they are a commercial "
  "feature, not a fix for the information problems that justify the project. FR23 (sales reports) is Must Have even "
  "though customers never see it, because the manager's lack of timely information is one of the root complaints.")

h2("1.14. Validating the Requirements")
p("I checked each requirement against five criteria: it has one clear actor and action, it lies inside the scope, "
  "it is feasible, it does not contradict another requirement, and it can be verified. Five requirements passed "
  "easily and serve as examples of the style. FR05 has a clear actor and action and is directly testable. FR09 "
  "defines when the check happens and what is checked. FR14 defines the exchange and the order linkage while "
  "respecting the boundary. NFR01 has a percentile, a time limit and a load condition, and NFR10 lists the invalid "
  "data that blocks confirmation, so both positive and negative tests can be written.")
p("Three candidate requirements from my first draft failed. Table 1.12 shows them with the problem and the "
  "revision. All three had the same defect: they named a quality without saying how anyone would know whether the "
  "system has it.", keep=True)
table("Problematic candidate requirements and their revisions", [
    ["Candidate", "Problem", "Revision"],
    ["The system should be user friendly.", "Vague and cannot be verified", "NFR05: each main customer function is reachable within three navigation actions"],
    ["The system shall keep inventory up to date.", "No trigger and no responsible actor", "FR16: stock is updated after confirmed orders and authorized warehouse changes"],
    ["The system shall manage payments securely.", "Mixes vague security with unclear behavior; implies processing cards ourselves", "FR14 for the request and status exchange; NFR03 and NFR04 for access control; card processing stays outside the boundary"],
], [4.3, 4.6, 7.1], size=10.5)

h2("1.15. Managing Requirement Change")
p("Requirements were not frozen after Assignment 02. Over the semester several of them changed, and I learned "
  "more from those changes than from writing the first version. Every change was handled the same way: state the "
  "trigger, decide which requirement or model changes, check the traceability table for side effects, and record the "
  "decision. Table 1.13 is the change log of the requirements and the use case model.", keep=True)
table("Change log of the requirements baseline", [
    ["When", "Change", "Trigger", "Effect on other artifacts"],
    ["Assignment 02", "UC17 Manage Customer Records added", "FR27 had no use case in the traceability check", "One more use case for Sales Staff; no class change"],
    ["Assignment 02", "Promotion requirements moved from Should to Could", "No problem in the investigation is about promotions", "Apply Promotion modeled as an optional extension of checkout"],
    ["Test 01", "Cart price and order price separated", "A cart price may change with promotions; an order price must not", "CartItem.cartPrice and OrderItem.unitPrice in Chapter 2"],
    ["Assignment 06", "Search requirements AI-R3 to AI-R7 added", "New course brief on multimodal search", "New use cases and a three-layer search component (Chapter 4)"],
    ["Assignment 06", "View Order changed from include to extend", "Viewing details is a separate goal of the customer", "Use case diagram redrawn; no code change"],
    ["Assignment 06", "Order search limited to the customer's own orders", "Privacy rule already implied by FR12", "Customer id passed into every order query"],
], [2.6, 4.3, 4.6, 4.5], size=10)
p("None of these changes was large, but each one would have been a small inconsistency if I had changed only the "
  "artifact I was working on. The cart and order price separation is a good example: it started as a remark in a "
  "class diagram, but it is really a requirement about which price the customer pays, so I recorded it here and "
  "traced it forward to the data model and the code.")

h2("1.16. Traceability")
p("Traceability links each problem to the needs, requirements and use cases that address it. It answers two "
  "questions that come up again and again in later phases: why does this requirement exist, and what breaks if we "
  "drop it? Table 1.14 is the forward traceability from the problems of Section 1.6 to the use cases of Chapter 2.",
  keep=True)
table("Traceability from problems to needs, requirements and use cases", [
    ["Problem or basis", "Need", "Requirements", "Use cases"],
    ["Inconsistent product information", "SN01, SN08", "FR04, FR06, FR26", "UC04, UC05, UC11"],
    ["Outdated inventory information", "SN01, SN10", "FR15, FR16, NFR10", "UC07, UC15"],
    ["Manual order processing", "SN04, SN09", "FR09 to FR11, FR13", "UC06, UC07, UC14"],
    ["Payment and order coordination", "SN05, SN12", "FR14", "UC08"],
    ["Unclear order status", "SN06", "FR12, FR18, NFR02", "UC09"],
    ["Shipping coordination", "SN13", "FR17, FR18", "UC16"],
    ["Manual sales reporting", "SN11", "FR23", "UC18"],
    ["Limited real-time management information", "SN11", "FR24, FR25", "UC18"],
    ["Fragmented customer information", "SN09", "FR27", "UC17"],
    ["Review activity", "SN07", "FR21", "UC10"],
    ["Supply coordination", "SN14", "FR28", "UC19"],
], [5.0, 2.6, 4.4, 4.0], size=10.5)
p("Reading the table backwards is just as useful. Every requirement in the table has a business reason; the Must "
  "Have requirements that do not appear in it (FR01, FR02, FR05, FR07, FR08 and the NFRs) are the basic account, "
  "search, cart and quality functions that any shop needs regardless of the seven problems. The table also exposed one gap in my first version: FR27 (customer "
  "records) had no use case until I added UC17 Manage Customer Records, even though fragmented customer data is one "
  "of the seven problems.")

h2("1.17. Requirements for the AI Extension")
p("The AI part was added later in the semester, and I treated it with the same discipline as the core requirements. "
  "It is deliberately kept outside the core baseline: the shop must sell without it, so none of its requirements is "
  "a Must Have of the core system. Two prototypes came first, a recommender in Assignment 02 and a multimodal search "
  "in Assignment 06; for this version Chapter 3 chooses one AI component for the shop itself, AI search, and "
  f"derives its requirements from stakeholder need SN02 and FR05. Table {next_tab()} lists them; they are numbered "
  "FR-S so that they do not clash with the core identifiers, and Chapter 3 gives the AI, data and non-functional "
  "requirements behind them.", keep=True)
table("Functional requirements of the AI search (Chapter 3)", [
    ["ID", "Requirement", "Priority"],
    ["FR-S1", "Interpret a free-text query: related words, spelling mistakes, price limits such as \"under 10 million\"", "Should"],
    ["FR-S2", "Rank the ACTIVE products by their relevance to the query", "Should"],
    ["FR-S3", "Show how the query was understood and why each result matched", "Should"],
    ["FR-S4", "Accept a spoken query, turned into text in the browser and correctable before it is sent", "Could"],
    ["FR-S5", "Accept a photo and return the products whose pictures look most alike", "Could"],
    ["FR-S6", "Fall back to the keyword search when the AI search finds nothing", "Must (if FR-S1 is built)"],
    ["FR-S7", "Keep the search index in step with the catalogue", "Must (if FR-S2 is built)"],
], [1.6, 11.4, 3.0], size=10.5, center_cols=(0, 2))

h2("1.18. Chapter Summary")
p("The requirement phase produced a baseline that the rest of the essay builds on: eight stakeholders, eleven "
  "business activities, seven problems reduced to three root causes, a scope with a clear boundary around payment "
  "and shipping, fourteen needs, twenty-eight functional and ten non-functional requirements, a MoSCoW plan and a "
  "traceability table. The lesson I take from this phase is that the quality of a requirement is mostly decided by "
  "two small things: whether it names a trigger or a measurable condition, and whether it can be traced to a "
  "problem. Both are cheap to check while writing and very expensive to repair after the design is built on top.")
