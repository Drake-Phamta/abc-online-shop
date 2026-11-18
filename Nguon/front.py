# -*- coding: utf-8 -*-
# Front matter: cover, abstract, abbreviations, table of contents, introduction.

# ---------------------------------------------------------------- cover
p("POSTS AND TELECOMMUNICATIONS INSTITUTE OF TECHNOLOGY", bold=True, size=14, align=C, after=0, before=10)
p("Course: Information Systems Analysis and Design", size=13, align=C, after=0)
p("─" * 22, size=12, align=C, after=60)
p("COURSE ESSAY", bold=True, size=15, align=C, after=14)
p("FROM REQUIREMENTS TO CODE", bold=True, size=22, align=C, after=6)
p("Analysis and Design of the ABC Online Shop with AI-Assisted Search", italic=True, size=15, align=C, after=90)
for label, value in (("Student", "Phạm Tuấn Anh"), ("Student ID", "B23DCDT018"), ("Class", "04"),
                     ("Version", "V5")):
    para = p("", align=L, indent=5.2, after=2)
    runs(para, f"{label}:", bold=True)
    runs(para, f"\t{value}")
    para.paragraph_format.tab_stops.add_tab_stop(Cm(8.3))
p("Hanoi, November 2026", align=C, before=120, size=13)

# ---------------------------------------------------------------- abstract
unnumbered("ABSTRACT")
p("This essay follows one information system, the ABC Online Shop, through the six parts of the course essay: "
  "requirement determination, analysis, the use of artificial intelligence in e-commerce, the data model, design and "
  "code. I did not start from a blank page. Over the semester I investigated the shop (Assignment 01), wrote its requirements "
  "and use cases (Assignment 02), modeled its data, behavior and structure (Assignment 03 and Test 01), turned the "
  "analysis classes into a layered design (Design 01) and built two small AI prototypes in Python (Assignments 02 "
  "and 06). For this version I kept the models in three Visual Paradigm files, Analysis, Data Model and Design, each "
  "adding to the one before, revised the product classes after the lecturer's feedback, let Visual Paradigm generate "
  "the data model, the database and the code skeleton from the classes, and implemented the purchase chain and an AI search as one running application that follows the design class for "
  "class. The essay puts these pieces in order, explains the reasoning behind each artifact, and shows where a "
  "decision taken in one phase constrained the next one.")
p("The main results are a requirements baseline of 14 stakeholder needs, 28 functional and 10 non-functional "
  "requirements traced to 21 use cases, with seven more requirements for the AI search; 30 diagrams in three Visual "
  "Paradigm files, from the use cases to the design sequences; a data model of 20 tables that Visual Paradigm "
  "generated from the class diagram with Synchronize to Entity Relationship Diagram, and the database generated "
  "from it; a design of 80 classes in three layers, 72 in Java and 8 view classes in the browser; and a Java application that implements "
  "nine use cases of the purchase chain and the AI search on that database. Two scripts check that every design "
  "class, attribute and operation exists in the code, and that the code contains everything the Instant Generator "
  "wrote from the model; 24 unit and integration tests, 36 API checks and 30 end-to-end checks in a browser pass. "
  "On 30 labelled queries the AI search puts a relevant product first for 29 of them (hit@1 0.97, against 0.23 for "
  "the keyword search), and on 84 test photos it finds the right product first in 93% of cases and always among the "
  "first three. I also report what the AI search cannot do, because the honest limits are part of the analysis.")
p("Keywords: requirements engineering, use case, UML, data modeling, ORM, model-driven code generation, DAO, MVC, "
  "three-layer architecture, AI search, TF-IDF, image similarity, Spring Boot.", italic=True)

# ---------------------------------------------------------------- abbreviations
h2("Abbreviations")
table(None, [
    ["Abbreviation", "Meaning"],
    ["AI", "Artificial intelligence"],
    ["API", "Application programming interface"],
    ["BCE", "Boundary, control, entity (robustness stereotypes of the objects in sequence diagrams)"],
    ["CRUD", "Create, read, update, delete"],
    ["DAO", "Data access object"],
    ["DDL", "Data definition language (the CREATE TABLE part of SQL)"],
    ["ERD", "Entity relationship diagram"],
    ["FR / NFR", "Functional / non-functional requirement"],
    ["MoSCoW", "Must, Should, Could, Won't have (prioritization scheme)"],
    ["MRR", "Mean reciprocal rank (search quality measure)"],
    ["MVC", "Model, view, controller"],
    ["ORM", "Object-relational mapping (classes stored as tables)"],
    ["REST", "Representational state transfer (HTTP API style)"],
    ["SN", "Stakeholder need"],
    ["SQL", "Structured Query Language"],
    ["TF-IDF", "Term frequency, inverse document frequency"],
    ["UC", "Use case"],
    ["UML", "Unified Modeling Language"],
    ["VP", "Visual Paradigm, the modeling tool used for all diagrams"],
], [3.5, 12.5], size=11)

# ---------------------------------------------------------------- contents
page_break()
p("CONTENTS", bold=True, size=16, align=L, after=10)
toc()

# ---------------------------------------------------------------- introduction
unnumbered("INTRODUCTION")
p("Most of what I learned in this course came from one recurring case: ABC Online Shop, a medium-sized retailer "
  "that sells consumer products online and coordinates its work with suppliers, a payment provider and a shipping "
  "provider. Each assignment asked for a different view of that shop. Written as one essay, they become a single path from a business problem to a running program, and the interesting part is the "
  "joints between the steps. A requirement that was written vaguely in week two turns into an ambiguous use case, "
  "then into a class with no clear responsibility, and finally into code that nobody can test. A requirement that "
  "was written well can be followed all the way down.")
p("The essay has six chapters, in the order of the lecturer's board: requirements, analysis, AI, data model, "
  "design and code, and each chapter is built on the artifacts I produced during the semester. Table 1 shows where "
  "the material comes from. Every diagram is a Visual Paradigm diagram. The models are kept in three files, "
  "vp/1_Analysis.vpp, vp/2_DataModel.vpp and vp/3_Design.vpp, and each file adds to the one before; every number "
  "comes from a program I ran, and every code excerpt is copied "
  "from the source files. Where I changed my mind after a submission, I say so in the text instead of quietly "
  "correcting the old artifact.", keep=True)
table("Chapters of the essay and the course work they build on", [
    ["Chapter", "Main question", "Built on"],
    ["1. Requirement Determination", "What problem does the shop have, what must the system do about it, and for whom?", "Assignment 01 (investigation), Assignment 02 (requirements, actors, use cases and their specifications)"],
    ["2. Analysis", "Which concepts, flows and boundary does the problem contain?", "Test 01 (class diagram), Assignment 02 (activities), Assignment 01 (context); the Analysis file"],
    ["3. AI in E-commerce", "Where does AI help the shop, and how do we know it helps?", "The lecturer's notes on integrating AI into e-commerce; Assignments 02 and 06 (Python prototypes); the AI search built into the shop"],
    ["4. Data Model", "Which tables must store the classes, and how does the database come from them?", "Assignment 03 (data model); the Data Model file, with the tables generated by Synchronize and the database by Generate Database"],
    ["5. Design", "How do the classes become software components in layers?", "Design 01 (four design steps, DAO, MVC), Assignment 06 (three-layer architecture); the Design file and the code skeleton generated by Instant Generator"],
    ["6. Code", "Does the design survive contact with a compiler and a test suite?", "The Spring Boot application of the purchase chain and the AI search, its tests and the evaluation of the search"],
], [3.6, 6.4, 6.0], size=10.5)
p("Three conventions are used throughout. First, requirement and use case identifiers (SN, FR, NFR, UC) are the ones fixed "
  "in Assignment 02, so a reader can follow FR14 from the requirements table in Chapter 1 to the payment use case in "
  "Section 1.21 and the payment classes in Chapter 5. Second, the essay is written in the first person, because many "
  "sections explain choices I made and alternatives I rejected; a design rationale written in the passive voice "
  "tends to hide exactly the part that is worth reading. Third, a blue bar in the left margin marks every paragraph, "
  "heading and caption that is new or changed since version V4, which I presented on 12 November 2026; a figure or "
  "table that only received a new number is not marked. Table 2 lists the changes and the reason for each.", keep=True)
table("Changes since version V4 (12 November 2026)", [
    ["Change", "Where", "Reason"],
    ["The models are kept in three Visual Paradigm files, Analysis, Data Model and Design, each adding to the one before", "Introduction; Chapters 2, 4 and 5", "the order of the lecturer's board"],
    ["The four kinds of product are subclasses of Product (inheritance), like the kinds of customer and of payment", "Section 2.1 (Figure 2.1); Sections 4.1 and 4.2.2; Figure 6.2", "the lecturer's feedback of 12 November"],
    ["The data model is generated from the class diagram by Synchronize, not drawn, and the tables keep the names that VP gives them", "Sections 4.1 and 4.2.1 (Figures 4.2 to 4.4)", "evaluation item 2: Data Model → DB"],
    ["Data Model → DB: the table of what Generate Database writes; the rules added by hand", "Sections 4.3 and 5.3", "evaluation item 2"],
    ["Class design as the analysis classes plus their methods; layers; code generated from the layered model", "Sections 5.1, 5.2 and 5.5", "evaluation items 3 and 4"],
    ["Business rules BR01 to BR13 and the states of an order", "Section 1.10", "the rules were cited before they were defined"],
    ["One general use case diagram, then the detailed ones", "Section 1.20", "two overview diagrams were hard to tell apart"],
    ["Why each attribute is stored, and which data is not stored", "Sections 4.2.3 and 4.2.4", "every column needs a reason"],
    ["The code next to the screen it produces, with numbered marks", "Section 6.8 (Figures 6.2 to 6.7)", "evaluation item 5: Code + Demo"],
    ["Removed: the business process and ArchiMate views, the data flow diagram, the analysis sequences and the separate conceptual, logical and physical ERDs", "former Chapters 1, 2 and 4", "not on the board; the generated data model replaces the three ERD levels"],
], [7.4, 4.6, 4.0], size=10)
p("The AI chapter sits in the middle on purpose. AI features such as recommendation and image search are often "
  "presented as separate products. In this essay they are treated as one more set of requirements: they have "
  "stakeholders, use cases, components and tests like every other part of the shop.")
