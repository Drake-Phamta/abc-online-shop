# -*- coding: utf-8 -*-
# Conclusion and references.

unnumbered("CONCLUSION")
p("This essay followed ABC Online Shop from a list of business complaints to running code. Requirement "
  "determination reduced seven problems to three root causes and produced 14 stakeholder needs, 28 functional and "
  "10 non-functional requirements with priorities, acceptance criteria and traceability, and 21 use cases with the "
  "specifications of the six central ones. The Analysis file holds the class diagram of twenty business classes, "
  "with the four kinds of product as subclasses of Product, the activity diagrams of the central use cases and the "
  "context diagram. The AI chapter treated the AI search as a component of the information system like any other: "
  "it has stakeholders, use cases, a data flow, rules, risks and a measured quality (hit@1 of 0.97 against 0.23 for "
  "the keyword search on 30 labelled queries, and 93% of 84 test photos found first). The Data Model file added "
  "types, identifiers, multiplicities, role names, «ORM Persistable» and Table per subclass to the same classes, and "
  "Visual Paradigm generated from them the data model of 20 tables with Synchronize to Entity Relationship Diagram "
  "and the database with Generate Database. The Design file carried the classes into 80 classes in three layers (72 "
  "in Java, 8 in the browser), revised the database with the rules a data model cannot hold, and generated the code "
  "skeleton with the Instant Generator; the code implements nine use cases of the purchase chain and the AI search on "
  "that database and passes 24 unit and integration tests, 36 API checks and 30 end-to-end checks in a browser.")
p("Three lessons stand out for me. The first is that most problems are cheapest to fix where they are created: a "
  "requirement with a trigger and a fit criterion (FR09, FR16) travelled through every later phase without trouble, "
  "while the vague first drafts of Section 1.15 would have produced vague classes and untestable code. The second "
  "is that the models check each other, and that the check can be automated. The class model found the product "
  "problem that the use cases hid; a script that compares the design classes with the compiled code found an "
  "operation the code never called and a business rule repeated in a screen; the code that Visual Paradigm generated "
  "from the model found navigable compositions and a type name that pointed to the wrong class; and the end-to-end "
  "run found a page that a slow request could replace. None of these would have been found by looking at one model "
  "alone. The third is the lesson of the lecturer's notes on AI in e-commerce: an AI-enabled shop is a complete "
  "information system, not only a model. In the AI search the ranking itself is a small part, and the parts that "
  "decide whether the feature is trustworthy are ordinary analysis and design: who may see which data, what happens "
  "when the model is wrong or unavailable, how the customer sees why a product was found, and how the result is "
  "measured.")
p("If I had another month, I would implement the remaining use cases (registration, reviews, promotions and "
  "reports) in the same three layers, move the database to PostgreSQL with full-text search, connect a real "
  "payment provider through the CardProvider interface with a record of every request, and give the photo search a "
  "learned image model behind the same ImageIndex interface, measured on the same 84 photos and then on search "
  "success and conversion with real customers. The structure built during this semester should make each of those "
  "changes a local one, and that, more than any single diagram, is what I take away from the course.")
unnumbered("REFERENCES")
refs = [
    "Tran Dinh Que, Information System Analysis and Design: assignment briefs 01, 02, 03 and 06, Test 01, the "
    "appendix \"From Analysis to Design\" and the notes \"Integrating AI into E-Commerce Systems: Analysis Phase\", "
    "Posts and Telecommunications Institute of Technology, 2026.",
    "A. Dennis, B. H. Wixom and R. M. Roth, Systems Analysis and Design, 7th ed. Hoboken, NJ: Wiley, 2018.",
    "I. Sommerville, Software Engineering, 10th ed. Boston: Pearson, 2015.",
    "C. Larman, Applying UML and Patterns: An Introduction to Object-Oriented Analysis and Design and Iterative "
    "Development, 3rd ed. Upper Saddle River, NJ: Prentice Hall, 2004.",
    "Object Management Group, OMG Unified Modeling Language (OMG UML), Version 2.5.1, 2017.",
    "M. Fowler, Patterns of Enterprise Application Architecture. Boston: Addison-Wesley, 2002.",
    "D. Alur, J. Crupi and D. Malks, Core J2EE Patterns: Best Practices and Design Strategies, 2nd ed. Upper Saddle "
    "River, NJ: Prentice Hall, 2003.",
    "G. Salton and C. Buckley, \"Term-weighting approaches in automatic text retrieval,\" Information Processing & "
    "Management, vol. 24, no. 5, pp. 513-523, 1988.",
    "C. D. Manning, P. Raghavan and H. Schütze, Introduction to Information Retrieval. Cambridge: Cambridge "
    "University Press, 2008.",
    "F. J. Damerau, \"A technique for computer detection and correction of spelling errors,\" Communications of the "
    "ACM, vol. 7, no. 3, pp. 171-176, 1964.",
    "M. J. Swain and D. H. Ballard, \"Color indexing,\" International Journal of Computer Vision, vol. 7, no. 1, "
    "pp. 11-32, 1991.",
    "VMware, Spring Boot Reference Documentation, version 3.2, 2024.",
]
for i, ref in enumerate(refs, 1):
    para = p(f"[{i}] {ref}", size=12, align=J, after=3)
    para.paragraph_format.left_indent = Cm(0.8)
    para.paragraph_format.first_line_indent = Cm(-0.8)
