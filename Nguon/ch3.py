# -*- coding: utf-8 -*-
# CHAPTER 3. AI IN E-COMMERCE (V4): the AI search of ABC Online Shop, analysed with the lecturer's notes
# "Integrating AI into E-Commerce Systems" (business problem -> requirements -> AI and data requirements -> AI
# component -> integration), designed in Chapter 4 (G0, G1, G8, G9) and built in Chapter 5. Specification:
# docs/SPEC.md section 6. Diagrams AI1 to AI4 of vp/ABC_Online_Shop_V4.vpp.

chapter("AI in E-commerce")
p("The lecturer's notes on AI in e-commerce start from one sentence that I used as the plan of this chapter: the "
  "important question is not which algorithm to use, but what business problem AI solves, where it belongs in the "
  "system, what data it needs and how it works with the rest of the information system. The notes give the chain "
  "business problem, business requirement, functional requirement, AI requirement, data requirement, AI component "
  "and system integration, and a list of fourteen results for a student analysis. This chapter follows that chain "
  "for ABC Online Shop. It ends with an AI component that Chapter 4 designs and Chapter 5 builds into the same shop, "
  "so the AI part goes through the same path from requirement to tested code as the rest of the system.")
p("Earlier in the semester I built two separate AI prototypes in Python: a product recommender in Assignment 02 "
  "and a multimodal search service in Assignment 06. They taught me the techniques, but they worked on their own "
  "small catalogues and had nothing to do with the shop's database, orders or users. For this version I started "
  "again from the shop's own problems and its own data.")

# ------------------------------------------------------------------------------------------------ 3.1
h2("3.1. Where AI Can Help ABC Online Shop")
p("The notes list the usual places for AI in an e-commerce system: search, recommendation, customer service, "
  "fraud prevention, demand forecasting, segmentation, review analysis and pricing. For each of them I asked three "
  "questions. Which business activity of Chapter 1 does it serve? Could a business rule do the same job? Does the "
  "shop already have the data the component would learn from? The last question decided most of the answers, "
  "because the analysis class model of Chapter 4 (Figure 4.1) and the demo database tell exactly what data exists: "
  "28 products in 10 categories with their detail attributes, descriptions and pictures, three customers, four "
  "orders and no reviews.", keep=True)
table("AI candidates for ABC Online Shop, checked against the shop's data", [
    ["AI component", "Business activity", "Can a rule do it?", "Data the shop has now", "Decision"],
    ["AI search (text, voice, photo)", "Product browsing and search (SN02, FR05)", "No: synonyms, misspellings, natural phrases and photos are open-ended", "Yes: names, categories, detail values, descriptions, images", "Selected"],
    ["Recommendation", "Product browsing, cross-selling", "Partly: \"same category\" is a rule", "Little: four orders, so mostly cold start", "Later, when orders exist"],
    ["Customer-service chatbot", "Order tracking, questions", "Order status is a lookup, not AI", "No conversation data; answers about orders need access control", "Rejected for now"],
    ["Fraud detection", "Payment", "Partly: limits and Luhn check exist (BR07)", "No labelled fraud; a false alarm blocks a customer", "Rejected"],
    ["Demand forecasting", "Inventory, supply", "Reorder at a threshold is a rule", "No sales history", "Rejected"],
    ["Customer segmentation", "Promotions, reporting", "VIP is a rule (total spent)", "Three customers", "Rejected"],
    ["Review sentiment analysis", "Reviews", "No", "No reviews (UC10 not implemented)", "Rejected"],
    ["Dynamic pricing", "Promotions", "Price changes are a staff decision", "No demand data; fairness risk", "Rejected"],
], [3.0, 3.1, 3.5, 3.9, 2.6], size=9.5)
p("The table also shows the point the notes make in their section on rules versus AI: much of what looks "
  "intelligent in a shop is a rule. A VIP discount, a reorder level or a refused negative stock (BR12) need no "
  "learning. AI is needed where the input is open-ended and the system must estimate rather than decide: a customer "
  "can describe the same pair of shoes in hundreds of ways, or just take a photo of it.")

# ------------------------------------------------------------------------------------------------ 3.2
h2("3.2. Selecting the AI Component")
p("I selected AI search for five reasons. First, its business problem is real in the current system: the keyword "
  "search of UC04 matches only substrings of the name, brand and category, so \"red sneakers\", \"macbok\", "
  "\"laptop under 10 million\" or the author \"orwell\" return nothing (Section 3.12 measures this: 23 of 30 "
  "realistic queries find no product at all). Second, it needs only data the shop already keeps, so there is no "
  "cold start: a product is searchable the moment it is in the catalogue. Third, a rule cannot do the job, as Table "
  "3.1 explains. Fourth, its errors are cheap and visible: a weak result list is seen at once by the customer, who "
  "can rephrase, and the keyword search remains as a fallback; a wrong fraud alarm or a wrong price is much more "
  "harmful. Fifth, it continues the course: Assignment 06 asked for exactly this kind of service, with text, voice "
  "and image input and the principle \"different inputs, common query representation, retrieval, ranking, results\".")
p("Recommendation was the closest second choice. I did not take it because with four orders a model based on "
  "behaviour cannot be evaluated, and a content-based recommender would only repeat what the search already knows "
  "about each product. It is the natural next AI component once the shop has a few months of orders, and the "
  "search index of this chapter can be reused for its content-based part.")

# ------------------------------------------------------------------------------------------------ 3.3
h2("3.3. Business Problem and Requirements")
p("Written in business terms, before any technique, the problem and the requirement are:")
table("Business problem and business requirement of the AI search", [
    ["Item", "ABC Online Shop"],
    ["Business problem", "Customers who do not type the exact product name find nothing, and a customer who finds nothing leaves. Chapter 1 asks for more: stakeholder need SN02 \"browse and search the catalogue efficiently\" and FR05 (Must) \"let customers search the product catalogue\"."],
    ["Business objective", "More searches that end at a product page or in the cart (search success rate); fewer searches without result."],
    ["Business requirement", "The shop helps customers find the right product in one search, whether they type, speak or show a photo."],
], [3.6, 12.4], size=10.5)
p("The business requirement becomes seven functional requirements. They extend FR05 and are numbered FR-S so that "
  "they do not clash with the identifiers of Chapter 1; docs/SPEC.md, the tests and the code use the same numbers.",
  keep=True)
table("Functional requirements of the AI search", [
    ["ID", "The system shall", "Use case (Figure 3.1)"],
    ["FR-S1", "interpret a free-text query: related words, spelling mistakes, price limits such as \"under 10 million\"", "Interpret Query"],
    ["FR-S2", "rank the ACTIVE products by their relevance to the query", "Rank and Explain Results"],
    ["FR-S3", "show how the query was understood and why each result matched", "Rank and Explain Results"],
    ["FR-S4", "accept a spoken query, turned into text in the browser and correctable before it is sent", "Search by Voice"],
    ["FR-S5", "accept a photo and return the products whose pictures look most alike", "Search by Photo"],
    ["FR-S6", "fall back to the keyword search when the AI search finds nothing", "Fall Back to Keyword Search"],
    ["FR-S7", "keep the search index in step with the catalogue", "UC04 (precondition)"],
], [1.5, 10.3, 4.2], size=10.5, center_cols=(0,))

# ------------------------------------------------------------------------------------------------ 3.4
h2("3.4. AI Requirements and Data Requirements")
p("The AI requirement states the behaviour expected from the component, not its algorithm: for a query q and every "
  "product p the component estimates a relevance score s(q, p), and the result is the list of the k products "
  "with the highest scores. For a text query the score compares the words of the query with the words of the "
  "product, as in the vector space model of information retrieval [8]; for a photo it compares two pictures.", keep=True)
eq([r("s(q, p) = "), frac(r("q · p"), r("‖q‖ ‖p‖")), r(",   result = top-k products by s(q, p)")], "3.1")
p(f"The notes separate what the analysis must fix from what belongs to the implementation. Table {next_tab()} applies that "
  "separation to the search. The right column was decided only in Chapter 5, and could change without touching "
  "any requirement on the left.", keep=True)
table("AI requirements of the analysis and the implementation choices made later", [
    ["Analysis phase (this chapter)", "Implementation phase (Chapter 5)"],
    ["Objective: rank products by relevance to the customer's query", "Vector space model with TF-IDF weights learned from the catalogue; cosine score"],
    ["Inputs: text up to 200 characters, a spoken query, a photo up to 5 MB", "Speech to text by the browser; JPEG or PNG decoded in memory"],
    ["Output: up to 12 products, each with a score and its reasons", "Reasons built from the words that contributed most to the score"],
    ["Understand related words and misspellings", "A lexicon kept by the sales staff; Damerau-Levenshtein distance [10] to the catalogue words"],
    ["Compare photos with product pictures", "Colour histogram of the object [11], edge directions and silhouette; cosine per feature"],
    ["Response time: text under 300 ms, photo under 1 s", "Indexes built once and kept in memory, rebuilt when the catalogue changes"],
    ["Explainable, private, available without AI", "Reasons on every result; photos never stored; keyword fallback"],
], [8.0, 8.0], size=10)
p(f"The data requirement follows from the AI requirement. The notes ask eight questions about the data; Table {next_tab()} "
  "answers them for the shop. The most important answer is the first: the search needs nothing that the shop does "
  "not already store, which is also why it can be built and measured now.", keep=True)
table("Data requirements of the AI search", [
    ["Question", "Answer for ABC Online Shop"],
    ["What data is required?", "Product name, brand, category and its parent, the detail values of the product's kind (author, processor, colour, material...), description, price, status; the product picture"],
    ["Where does it come from?", "Tables product, category, book_detail, laptop_detail, phone_detail, apparel_detail (Chapter 4); the image folder of the shop"],
    ["Is it available?", "Yes, for all 28 products of the demo data"],
    ["Is it reliable?", "Kept by staff in the catalogue (UC11); the same data the product page shows"],
    ["How often is it updated?", "When the catalogue changes; the index follows at the next search (FR-S7)"],
    ["How much history exists?", "None is needed: the search learns from the catalogue, not from customer behaviour"],
    ["Privacy constraints?", "Queries and photos may contain personal data: processed in memory, not stored, not linked to the customer (rule AI05)"],
    ["What if data is missing?", "A product without a picture is not found by photo but still by text; a word the catalogue does not use is corrected or ignored"],
], [4.2, 11.8], size=10)

# ------------------------------------------------------------------------------------------------ 3.5
h2("3.5. Use Cases of the AI Search")
p(f"Figure {next_fig()} refines UC04 Browse / Search Products of Chapter 2 for the AI search. Searching by text, by "
  "voice and by photo are three kinds of the same goal, finding a product, so they specialize UC04 through a "
  "generalization, and UC04 Search Products is abstract (its name is in italics): every search is one of the three. "
  "I first drew voice and photo as extends of UC04 and changed it when I checked the diagram against the code. An "
  "extend adds optional behaviour to a base use case that is complete without it, while these three ways replace "
  "one another; and the base included Interpret Query, which a search by photo never runs, because a photo has no "
  "words to interpret. Now Rank and Explain Results is included by UC04 and inherited by every kind of search, and "
  "Interpret Query is included only by Search by Text and Search by Voice. Fall Back to Keyword Search stays an "
  "extend: it runs only under a condition, at the extension point \"nothing found\" after a typed or spoken query. "
  "The Speech Recognition Service is a secondary actor of Search by Voice: the browser sends it the spoken query and "
  "gets text back. The Sales Staff maintain the search lexicon, the list of related words that the interpretation "
  "uses; this is the human control the notes ask for, and in the prototype it is still a list in the code.", keep=True)
landscape()
F_AI1 = figure("vp/png/AI1.png", "AI search use cases: the abstract UC04 with its three kinds of search (generalization), included and extending use cases (diagram AI1)", width_cm=23.5, max_h_cm=14.5)
portrait()
p("The main flow and the alternative flows are those of UC04 in docs/SPEC.md: the customer types or speaks a query "
  "or uploads a photo; the system interprets the text, ranks the ACTIVE products and shows the understood query with "
  "the reasons of every result; if nothing is found the keyword search runs, and if that is empty too, the page "
  "says so and links back to all products. I kept the AI search inside UC04 instead of making it a new use case "
  "because the goal of the customer is the same, finding a product; only the way of reaching it changes, which is "
  f"exactly what the generalization of Figure {F_AI1} says.")

# ------------------------------------------------------------------------------------------------ 3.6
h2("3.6. Context and Data Flow")
p("The notes show the context of an AI-enabled shop with the AI services inside the system boundary, and add that "
  f"AI should be decomposed inside the system rather than treated as an external process. Figure {next_fig()} follows this. "
  "Compared with the context diagram of Chapter 1, two external entities have new flows: the Speech Recognition "
  "Service, which turns a spoken query into text, and the Sales Staff, who send lexicon changes and labelled "
  "queries and receive the search evaluation. The search itself is not an entity of its own.", keep=True)
landscape()
F_AI2 = figure("vp/png/AI2.png", "Context diagram of the AI-enabled shop (diagram AI2)", width_cm=24, max_h_cm=6)
F_AI3 = figure("vp/png/AI3.png", "Data flow of the AI search: processes 2.1 to 2.5 and their data stores (diagram AI3)", width_cm=24, max_h_cm=8.4)
portrait()
p(f"Figure {F_AI3} opens the search, which is process 2 \"Browse and search the catalogue\" of the level 1 DFD in "
  "Chapter 2. Process 2.1 takes the query, sends a spoken query to the speech service and interprets the text with "
  "the related words of store D9. Process 2.2 ranks the products by text with the word weights of store D8 and "
  "returns them with their reasons; process 2.3 does the same for a photo with the image features. Process 2.4 "
  "builds both indexes from the catalogue (D2) and the product images (D7), and process 2.5 lets the sales staff "
  "maintain the lexicon. The data flow is the one of the notes' recommendation example, data, features, model, "
  "ranked products, applied to search: the indexes are the features, and they are computed from the catalogue, "
  "not from customer behaviour.")

# ------------------------------------------------------------------------------------------------ 3.7
h2("3.7. The AI Component in the Shop")
p(f"Figure {next_fig()} places the AI component among the parts of the shop, as the notes' decomposition does. The AI "
  "search has three parts: query understanding, text ranking and photo matching. The web UI uses it with a text, a "
  "spoken text or a photo, and it reads products, details and images from the catalogue. It does not call the "
  "cart, the orders or the payments, and nothing in those parts depends on it. That is the practical meaning of "
  "\"AI is an enhancement\": if the AI component were removed, the shop would still sell, with the keyword search "
  "in its place.", keep=True)
landscape()
F_AI4 = figure("vp/png/AI4.png", "The AI component inside the shop: its three parts and the parts of the shop it works with (diagram AI4)", width_cm=23, max_h_cm=10.5)
p(f"Table {next_tab()} is the specification of the component in the form the notes propose: one row per question that an "
  "analyst must be able to answer before the component is designed.", keep=True)
table("Specification of the AI search component", [
    ["Item", "AI search of ABC Online Shop"],
    ["Business problem", "Customers who do not type the exact name find nothing and leave"],
    ["Business objective", "Higher search success rate, fewer searches without result"],
    ["AI function", "Ranking: relevance score s(q, p) for every ACTIVE product, top k returned (equation 3.1)"],
    ["Input / output", "Text, spoken text or photo / up to 12 products (6 for a photo) with score and reasons, and the understood query"],
    ["Data source", "Catalogue tables and product images (Table 3.5)"],
    ["System component", "AI search, inside the business logic of the shop, behind the search service"],
    ["Interaction", "Web UI (search box, voice dialog, photo button); catalogue for products and images"],
    ["Performance", "Better than the keyword search on the labelled queries; text under 300 ms, photo under 1 s"],
    ["Update", "Index rebuilt from the catalogue when the catalogue changes (FR-S7)"],
    ["Human role", "Sales staff keep the lexicon and check the labelled queries before a change goes live"],
    ["Risk", "Wrong or missing results, unfair ranking, private photos, crafted input (Section 3.11)"],
    ["Evaluation", "Hit@1, recall@5, MRR, zero-result rate, photo accuracy, latency; later search success and conversion (Section 3.12)"],
], [3.6, 20.4], size=10)
portrait()

# ------------------------------------------------------------------------------------------------ 3.8
h2("3.8. Input and Output Specification")
table("Inputs and outputs of the AI search", [
    ["Direction", "Item", "Specification", "Rule"],
    ["Input", "Text query", "1 to 200 characters, any language the lexicon knows (English, Vietnamese with or without accents)", "AI06"],
    ["Input", "Spoken query", "Turned into text by the browser's speech recognition; the customer sees and can correct the text before it is sent", "FR-S4"],
    ["Input", "Photo", "One JPEG or PNG file up to 5 MB, checked by its first bytes before it is decoded", "AI06"],
    ["Output", "Understood query", "Terms, related words, corrected words, price limits, \"cheaper first\"", "AI02"],
    ["Output", "Results", "Up to 12 products (6 for a photo), each with its card data, a relevance score and up to three reasons", "AI02"],
    ["Output", "Mode", "AI search, photo search, or keyword search when the fallback was used", "AI04"],
], [2.0, 3.0, 9.4, 1.6], size=10, center_cols=(0, 3))

# ------------------------------------------------------------------------------------------------ 3.9
h2("3.9. Non-functional Requirements for the AI")
p("The notes list accuracy, latency, availability, explainability, fairness and privacy as the additional "
  f"non-functional requirements of AI. Table {next_tab()} gives the target for each and the place where the system meets "
  "it. Accuracy is stated relative to the keyword search, because with 28 products an absolute number says little; "
  "the search must be measurably better than what the shop already has.", keep=True)
table("Non-functional requirements of the AI search", [
    ["Quality", "Requirement", "How it is met and checked"],
    ["Accuracy", "MRR and recall@5 higher than the keyword search on the labelled queries; photo top-1 accuracy at least 0.8", "tests/search_eval.py (Section 3.12)"],
    ["Latency", "Text search under 300 ms, photo search under 1 s on the demo machine", "Server time in every answer (tookMs), measured by the evaluation"],
    ["Availability", "The shop sells without the AI search", "Keyword fallback (AI04); the AI component is called only by the search service"],
    ["Explainability", "Every result shows why it matched; the page shows how the query was understood", "Rule AI02, checked by the end-to-end test"],
    ["Fairness", "No product or brand is favoured by the ranking itself", "Only query words count; no brand boost; out-of-stock rule AI07 is the only business adjustment"],
    ["Privacy", "Photos and spoken queries are not kept", "Rule AI05: processed in memory, never written to disk or to the log"],
], [2.6, 6.6, 6.8], size=10)

# ------------------------------------------------------------------------------------------------ 3.10
h2("3.10. Failure, Fallback and Human Control")
p("The notes put AI design into one line: prediction plus fallback plus human control. For the search the "
  f"prediction is the ranking; Table {next_tab()} lists what can go wrong and what the system does then.", keep=True)
table("Failures of the AI search and the fallback for each", [
    ["Failure", "Effect", "Response"],
    ["Words the catalogue does not use", "No result", "Related words, spelling correction, then the keyword search (AI04); the page says which search produced the results"],
    ["Low-quality or unrelated photo", "Unrelated products", "Results under a similarity threshold are not shown; the page shows the similarity of each result"],
    ["No speech recognition in the browser, or no network for it", "The voice button cannot listen", "The dialog says so and keeps a text box; typing works the same way"],
    ["Catalogue changed after the index was built", "Results out of date", "The index is rebuilt before the next search; prices and stock of the results are always read fresh"],
    ["Product out of stock", "First result cannot be bought", "In a text search its relevance counts 20 % less (AI07); a photo search keeps it, so the customer learns that it is out of stock"],
], [4.2, 3.4, 8.4], size=10)
p("Human control has two places. The sales staff own the lexicon: they decide that a sneaker is a kind of shoe, "
  "that \"giay\" means shoe, and that \"burgundy\" is a shade of red. A wrong entry would change the results of many "
  "queries, so a change is checked against the labelled queries before it goes live (Section 3.12). The second "
  "place is the AI07 rule, which is a business decision about ranking and not something the model learned: whether "
  "a product that cannot be bought should still come first is a question for the shop, not for an algorithm.")

# ------------------------------------------------------------------------------------------------ 3.11
h2("3.11. Risk Analysis")
table("Risks of the AI search", [
    ["Risk", "Example in this shop", "Response"],
    ["Bias", "A brand that is mentioned in many descriptions could always rank first", "Ranking by query words only; labelled queries include several brands"],
    ["Privacy", "A customer photographs a product while wearing it", "Photos processed in memory, never stored or logged (AI05)"],
    ["Wrong prediction", "\"red sneakers\" first returned burgundy boots during development", "Lexicon with broader words instead of plain synonyms; regression check with the labelled queries"],
    ["Drift", "New products bring words the lexicon does not know", "Index rebuilt from the catalogue; lexicon review by sales staff"],
    ["Cold start", "A new product has no history", "No effect: the search uses catalogue data only"],
    ["Security", "A 2 MB query string or a file disguised as a photo", "Length limit, file type checked by its first bytes, size limit (AI06)"],
    ["Lack of explanation", "A customer does not see why a product appears", "Reasons on every result, understood query on the page (AI02)"],
    ["Service failure", "Speech service unreachable during the demonstration", "Voice dialog falls back to typing; text and photo search need no external service"],
], [3.0, 6.4, 6.6], size=10)
p("The \"wrong prediction\" row is a real case. My first lexicon put sneakers, trainers and boots into one group of "
  "synonyms, and \"red sneakers\" ranked Dr. Martens boots in burgundy above the red Converse sneakers. The fix was "
  "a change of the analysis model, not a tuning trick: a boot is a kind of shoe, not a kind of sneaker, so the "
  "lexicon now has synonyms and broader words separately, and a related word stands in for the customer's word "
  "instead of adding to it.")

# ------------------------------------------------------------------------------------------------ 3.12
h2("3.12. Evaluation Metrics and Results")
p("The notes ask for evaluation on two levels. The technical level measures the ranking. For a query with a known "
  "set of relevant products I used four measures: hit@1, whether the first result is relevant; recall@5, the share "
  "of the relevant products in the first five; the reciprocal rank 1/r of the first relevant result, averaged over "
  "the queries as the mean reciprocal rank (MRR) [9]; and the zero-result rate. I did not use precision@5 because many "
  "queries have only one relevant product, so even a perfect list would score 0.2.", keep=True)
eq([r("MRR = "), frac(r("1"), r("|Q|")), r(" "), sub(r("Σ"), r("q ∈ Q")), r(" "), frac(r("1"), sub(r("rank"), r("q")))], "3.2")
p("The test set is 30 queries in tests/search/queries.json, each with the products a shop assistant would show: "
  "names, brands, misspellings, attributes, price limits, descriptions and Vietnamese. The keyword search of UC04 "
  f"and the AI search ran on the same queries against the running application; Table {next_tab()} is the output of "
  f"tests/search_eval.py (docs/evidence/search_eval.txt).", keep=True)
T_EVAL_TEXT = table("Text search on 30 labelled queries: keyword search of UC04 against the AI search", [
    ["Method", "Hit@1", "Recall@5", "MRR", "Zero-result rate", "Median time"],
    ["Keyword search (substring of name, brand, category)", "0.23", "0.23", "0.23", "0.77", "4 ms (round trip)"],
    ["AI search", "0.97", "0.97", "0.97", "0.03", "2 ms (server)"],
], [5.6, 1.6, 1.8, 1.4, 2.6, 3.0], size=10, center_cols=(1, 2, 3, 4, 5))
p("The keyword search found the right product only when the query contained a substring of the name, as in "
  "\"macbook\", \"iphone\" or \"nike\". It failed on every misspelling, every attribute (\"16gb\", \"leather\", the author "
  "\"orwell\"), every price limit and every Vietnamese query. The AI search missed one query: \"warm clothes for "
  "winter\". No product text in the catalogue says warm or winter, and nothing in the lexicon links them to wool or "
  "a jacket, so the AI search found nothing and the keyword search, as fallback, found nothing either. I left this "
  "failure in the results on purpose. Adding \"winter\" to the lexicon would make the number perfect but would only "
  "fit the model to the test; the case shows the real limit of a word-based model, which is the point where an "
  "embedding model trained on a large text corpus would help.")
p("For photos I made three customer-like pictures of every product from its catalogue image: the middle 80 % "
  "turned by 8 degrees, a darker and blurred version, and the product cut out and placed at 70 % size on a "
  f"textured background (tests/search/make_photos.py). Table {next_tab()} shows the result.", keep=True)
T_EVAL_PHOTO = table("Photo search on 84 photos made from the 28 catalogue images", [
    ["Kind of photo", "Photos", "Top-1 accuracy", "Top-3 accuracy"],
    ["Cropped and turned", "28", "0.96", "1.00"],
    ["Darker and blurred", "28", "0.86", "1.00"],
    ["Other background", "28", "0.96", "1.00"],
    ["All", "84", "0.93", "1.00"],
], [6.0, 2.4, 3.6, 3.6], size=10, center_cols=(1, 2, 3))
p("The six photos whose product came second or third are instructive: four of them are dark photos, and in three "
  "the first result was the pink iPhone 15, whose flat, light-coloured picture is close to many darkened pictures. "
  "Colour carries 55 % of the similarity, and darkening shifts colours most. These photos come from the catalogue "
  "images, so they measure robustness to framing, light and background, not the recognition of a different photo "
  "of the same model; that would need real customer photos, which the shop does not have.")
p("Two more limits belong in an honest report. The labelled queries were written by me, and some of them, such as "
  "\"red sneakers\", also guided the lexicon during development, so the text numbers are optimistic. And 28 products "
  "make ranking easy. The business level of the notes, search success rate and conversion after a search, needs "
  "real traffic: the plan is to log whether a search ends at a product page or in the cart, without the customer's "
  "identity, and to compare the rates before and after a lexicon change.")

# ------------------------------------------------------------------------------------------------ 3.13
h2("3.13. Traceability of the AI Search")
p(f"The notes end the analysis with a traceability table from business goal to metric. Table {next_tab()} extends it to "
  "the design and the tests of the following chapters, so that the AI search can be followed like any other "
  "requirement of the shop.", keep=True)
table("Traceability of the AI search from business goal to test", [
    ["Business goal", "Requirement", "Analysis", "Design (Chapter 4)", "Code and test (Chapter 5)", "Metric"],
    ["Find products in one search", "FR-S1, FR-S2, FR-S3", "AI1, AI3 (2.1, 2.2)", "G8 QueryInterpreter, ProductIndex; G9", "SearchService.search; SearchTest AT11 to AT14", "MRR, recall@5"],
    ["Search without typing", "FR-S4", "AI1 Search by Voice", "G8 SearchForm.startVoice", "SearchForm.js; end-to-end voice check", "Searches by voice"],
    ["Search with a photo", "FR-S5", "AI1, AI3 (2.3)", "G8 ImageIndex", "SearchService.searchByPhoto; SearchTest AT15", "Photo top-1, top-3"],
    ["Never a dead end", "FR-S6, AI04", "AI1 Fall Back", "G9 alt fragment", "SearchTest AT16", "Zero-result rate"],
    ["Current results", "FR-S7", "AI3 (2.4)", "G9 opt fragment", "SearchService.indexes", "Index age"],
], [2.6, 2.2, 2.4, 3.2, 3.6, 2.0], size=9)

# ------------------------------------------------------------------------------------------------ 3.14
h2("3.14. Chapter Summary")
p("Following the lecturer's chain from business problem to AI component, I chose AI search for ABC Online Shop "
  "because it answers a measured problem of the current shop, uses only data the shop already has and fails in "
  "a cheap, visible way. The analysis produced seven functional requirements, the AI and data requirements, four "
  "native Visual Paradigm diagrams (use cases, context, data flow and the AI component), a component specification, "
  "the non-functional requirements, the failures with their fallbacks and the risks. The evaluation shows the AI "
  "search finding the right product first in 29 of 30 queries where the keyword search managed 7, and the right "
  "product among the first three for every one of 84 photos, with the limits of a small catalogue and of test data "
  "written by the developer. Chapter 4 designs the component inside the three layers, and Chapter 5 shows the code "
  "and the tests.")
