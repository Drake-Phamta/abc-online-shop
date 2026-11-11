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
                     ("Version", "V4")):
    para = p("", align=L, indent=5.2, after=2)
    runs(para, f"{label}:", bold=True)
    runs(para, f"\t{value}")
    para.paragraph_format.tab_stops.add_tab_stop(Cm(8.3))
p("Hanoi, November 2026", align=C, before=120, size=13)

# ---------------------------------------------------------------- abstract
unnumbered("ABSTRACT")
p("This essay follows one information system, the ABC Online Shop, through the five activities of the course: "
  "requirement determination, analysis, the use of artificial intelligence in e-commerce, design and coding. I did "
  "not start from a blank page. Over the semester I investigated the shop (Assignment 01), wrote its requirements "
  "and use cases (Assignment 02), modeled its data, behavior and structure (Assignment 03 and Test 01), turned the "
  "analysis classes into a layered design (Design 01) and built two small AI prototypes in Python (Assignments 02 "
  "and 06). For this version I redrew every model in one Visual Paradigm project, revised the data model after the "
  "lecturer's feedback on products, let Visual Paradigm generate the database and the code skeleton from the models, "
  "and implemented the purchase chain and an AI search as one running application that follows the design class for "
  "class. The essay puts these pieces in order, explains the reasoning behind each artifact, and shows where a "
  "decision taken in one phase constrained the next one.")
p("The main results are a requirements baseline of 14 stakeholder needs, 28 functional and 10 non-functional "
  "requirements traced to 21 use cases, with seven more requirements for the AI search; 42 diagrams in one Visual "
  "Paradigm project, from a BPMN business process to the design sequences; a data model carried from 20 conceptual "
  "entities to a database of 20 tables that Visual Paradigm generated from the physical model; a design of 81 "
  "classes in three layers, 73 in Java and 8 view classes in the browser; and a Java application that implements "
  "nine use cases of the purchase chain and the AI search on that database. Two scripts check that every design "
  "class, attribute and operation exists in the code, and that the code contains everything the Instant Generator "
  "wrote from the model; 24 unit and integration tests, 36 API checks and 30 end-to-end checks in a browser pass. "
  "On 30 labelled queries the AI search puts a relevant product first for 29 of them (hit@1 0.97, against 0.23 for "
  "the keyword search), and on 84 test photos it finds the right product first in 93% of cases and always among the "
  "first three. I also report what the AI search cannot do, because the honest limits are part of the analysis.")
p("Keywords: requirements engineering, BPMN, use case, UML, data modeling, model-driven code generation, DAO, MVC, "
  "three-layer architecture, AI search, TF-IDF, image similarity, Spring Boot.", italic=True)

# ---------------------------------------------------------------- abbreviations
h2("Abbreviations")
table(None, [
    ["Abbreviation", "Meaning"],
    ["AI", "Artificial intelligence"],
    ["API", "Application programming interface"],
    ["BCE", "Boundary, control, entity (robustness stereotypes of the objects in sequence diagrams)"],
    ["BPMN", "Business Process Model and Notation"],
    ["CRUD", "Create, read, update, delete"],
    ["DAO", "Data access object"],
    ["DDL", "Data definition language (the CREATE TABLE part of SQL)"],
    ["DFD", "Data flow diagram"],
    ["ERD", "Entity relationship diagram"],
    ["FR / NFR", "Functional / non-functional requirement"],
    ["MoSCoW", "Must, Should, Could, Won't have (prioritization scheme)"],
    ["MRR", "Mean reciprocal rank (search quality measure)"],
    ["MVC", "Model, view, controller"],
    ["PK / FK", "Primary key / foreign key"],
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
p("The essay has five chapters, one for each activity named in the essay brief, and each chapter is built on the "
  "artifacts I produced during the semester. Table 1 shows where the material comes from. Every diagram is a Visual "
  "Paradigm diagram of one project (vp/ABC_Online_Shop_V4.vpp), redrawn for this version so that the models of "
  "all phases share the same elements; every number comes from a program I ran, and every code excerpt is copied "
  "from the source files. Where I changed my mind after a submission, I say so in the text instead of quietly "
  "correcting the old artifact.", keep=True)
table("Chapters of the essay and the course work they build on", [
    ["Chapter", "Main question", "Built on"],
    ["1. Requirement Determination", "What problem does the shop have, and what must the system do about it?", "Assignment 01 (investigation), Assignment 02 (requirements); business process, stakeholder map and problem tree redrawn in BPMN and ArchiMate"],
    ["2. Analysis", "Which actors, behaviors, data and classes does the problem contain?", "Assignment 02 (use cases, activities), Assignment 03 (DFD, sequence, class and data models), Test 01"],
    ["3. AI in E-commerce", "Where does AI help the shop, and how do we know it helps?", "The lecturer's notes on integrating AI into e-commerce; Assignments 02 and 06 (Python prototypes); the AI search built into the shop"],
    ["4. Design", "How do the analysis classes become software components?", "Design 01 (four design steps, DAO, MVC), Assignment 06 (three-layer architecture); database and code skeleton generated by Visual Paradigm"],
    ["5. Code", "Does the design survive contact with a compiler and a test suite?", "The Spring Boot application of the purchase chain and the AI search, its tests and the evaluation of the search"],
], [3.6, 6.4, 6.0], size=10.5)
p("Two conventions are used throughout. First, requirement and use case identifiers (SN, FR, NFR, UC) are the ones fixed "
  "in Assignment 02, so a reader can follow FR14 from the requirements table in Chapter 1 to the payment use case in "
  "Chapter 2 and the payment classes in Chapter 4. Second, the essay is written in the first person, because many "
  "sections explain choices I made and alternatives I rejected; a design rationale written in the passive voice "
  "tends to hide exactly the part that is worth reading.")
p("The AI chapter sits in the middle on purpose. AI features such as recommendation and image search are often "
  "presented as separate products. In this essay they are treated as one more set of requirements: they have "
  "stakeholders, use cases, components and tests like every other part of the shop.")
