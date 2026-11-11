# -*- coding: utf-8 -*-
"""Design model (exported from the Visual Paradigm project) against the code.

Inputs
  docs/evidence/design_model.tsv   package, class, kind, name, parameter types, type[, parameter names]
                                   (written by the VP plugin from the design classes of the project)
  docs/evidence/seq_messages.tsv   diagram, number, sender class, receiver class, label, is return
                                   (the messages of the design sequence diagrams), optional
  app/target/classes               compiled Java classes (run "mvn -q compile" first), read with javap
  app/src/main/resources/static/js/view/*.js   the view classes

Checks
  every design class exists in its package (nested classes count: OrderService$Checkout is "Checkout")
  every attribute exists as a field of the same type, every operation as a method with the same name,
  parameter types and return type (simple names; generic arguments are compared too)
  every view operation exists in the JS class with the same number of parameters
  every call message of a design sequence names an operation of the receiver's design class and of the code
Prints one line per problem and a summary; exit code = number of problems.
"""
import csv
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TSV = ROOT / "docs" / "evidence" / "design_model.tsv"
SEQ = ROOT / "docs" / "evidence" / "seq_messages.tsv"
CLASSES = ROOT / "app" / "target" / "classes"
VIEWS = ROOT / "app" / "src" / "main" / "resources" / "static" / "js" / "view"


def simple(t):
    """'java.util.List<vn.ptit.ecom.dao.OrderDAO$OrderSummary>' -> 'List<OrderSummary>'."""
    t = re.sub(r"[\w.]+\$", "", t)            # outer classes of nested ones
    t = re.sub(r"\b(?:[a-z_]\w*\.)+", "", t)  # package prefixes
    return t.replace(" ", "")


def raw(t):
    return simple(t).split("<")[0]


def javap_package(pkg):
    """{simple class name: {"kind", "fields": {name: type}, "methods": {name: [(params, return)]}}}"""
    folder = CLASSES / Path(*pkg.split("."))
    # relative paths from the classes folder: the Java tools read arguments in the ANSI code page, which cannot hold
    # the Vietnamese letters of the course folder name
    files = sorted(str(p.relative_to(CLASSES)) for p in folder.glob("*.class"))
    out = subprocess.run(["javap", "-p"] + files, capture_output=True, text=True, encoding="utf-8", cwd=CLASSES).stdout
    classes, cur = {}, None
    for line in out.splitlines():
        line = line.strip()
        m = re.match(r"(?:public |protected |private )?(?:abstract |static |final |sealed )*(class|interface|enum) ([\w.$]+)", line)
        if m:
            name = m.group(2).split(".")[-1].split("$")[-1]
            cur = classes.setdefault(name, {"kind": m.group(1), "fields": {}, "methods": defaultdict(list)})
            if "extends java.lang.Record" in line:
                cur["kind"] = "record"
            if "extends java.lang.Enum" in line:
                cur["kind"] = "enum"
            continue
        if cur is None or not line.endswith(";") or "lambda$" in line or "access$" in line:
            continue
        sig = re.sub(r" throws .*;$", ";", line)
        mm = re.match(r"(?:(?:public|protected|private|static|final|abstract|synchronized|native|default|transient|volatile) )*"
                      r"(?:<.*?> )?(.+?) ([\w$]+)\((.*)\);$", sig)
        if mm:
            params = [simple(p) for p in split_params(mm.group(3))]
            cur["methods"][mm.group(2)].append((params, simple(mm.group(1))))
            continue
        mf = re.match(r"(?:(?:public|protected|private|static|final|transient|volatile) )*(.+?) ([\w$]+);$", sig)
        if mf:
            cur["fields"][mf.group(2)] = simple(mf.group(1))
    return classes


def split_params(s):
    """split on commas outside <...>."""
    parts, depth, buf = [], 0, ""
    for ch in s:
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        parts.append(buf.strip())
    return parts


def same_type(design, code):
    if not design:
        return True   # the design leaves the type open (e.g. void operations)
    d, c = simple(design), simple(code)
    if d == c or raw(d) == raw(c) and ("<" not in d or "<?>" in d):
        return True
    return d.replace("...", "[]") == c.replace("...", "[]")


def js_views():
    views = {}
    for f in sorted(VIEWS.glob("*.js")):
        text = f.read_text(encoding="utf-8")
        cls = re.search(r"export class (\w+)", text)
        if not cls:
            continue
        methods = {}
        for i, line in enumerate(text.splitlines(), 1):
            m = re.match(r"\s{2,4}(?:async\s+)?(\w+)\s*\(([^)]*)\)\s*\{", line)
            if m and m.group(1) not in ("if", "for", "while", "switch", "catch", "constructor"):
                params = [p.strip() for p in m.group(2).split(",") if p.strip()]
                methods[m.group(1)] = (params, f"{f.relative_to(ROOT).as_posix()}:{i}")
        views[cls.group(1)] = methods
    return views


def main():
    rows = [r for r in csv.reader(TSV.read_text(encoding="utf-8").splitlines(), delimiter="\t") if r and not r[0].startswith("#")]
    problems, checked = [], defaultdict(int)
    design = defaultdict(lambda: {"kind": "", "attributes": {}, "operations": defaultdict(list)})
    for r in rows:
        r += [""] * (7 - len(r))
        pkg, cls, kind, name, ptypes, typ, pnames = r[:7]
        d = design[(pkg, cls)]
        if kind == "class":
            d["kind"] = name or "class"
        elif kind == "attribute":
            d["attributes"][name] = typ
        elif kind == "operation":
            d["operations"][name].append((ptypes, typ, pnames))
    code = {}
    views = js_views()
    for (pkg, cls), d in design.items():
        if pkg.endswith(".view"):
            js = views.get(cls)
            if js is None:
                problems.append(f"view class {cls} missing in {VIEWS.relative_to(ROOT).as_posix()}")
                continue
            for op, sigs in d["operations"].items():
                checked["view operations"] += 1
                if op not in js:
                    problems.append(f"{cls}.{op}() missing in the JS view")
                    continue
                for ptypes, _, pnames in sigs:
                    n_design = len(pnames.split(",")) if pnames else (ptypes.count(",") + 1 if ptypes else None)
                    n_code = len(js[op][0])
                    if n_design is not None and n_design != n_code:
                        problems.append(f"{cls}.{op}: design has {n_design} parameters, {js[op][1]} has {n_code}")
            continue
        if pkg not in code:
            code[pkg] = javap_package(pkg)
        c = code[pkg].get(cls)
        checked["classes"] += 1
        if c is None:
            problems.append(f"class {pkg}.{cls} not found in the compiled code")
            continue
        if d["kind"] == "interface" and c["kind"] != "interface":
            problems.append(f"{cls} is an interface in the design but a {c['kind']} in the code")
        if d["kind"] == "enumeration" and c["kind"] != "enum":
            problems.append(f"{cls} is an enumeration in the design but a {c['kind']} in the code")
        for a, typ in d["attributes"].items():
            checked["attributes"] += 1
            if a not in c["fields"]:
                # enum literals and record components are fields too; an attribute may also be a derived getter
                if a in c["methods"] or ("get" + a[0].upper() + a[1:]) in c["methods"] or ("is" + a[0].upper() + a[1:]) in c["methods"]:
                    continue
                problems.append(f"{cls}.{a} : attribute not found in the code")
            elif typ and not same_type(typ, c["fields"][a]):
                problems.append(f"{cls}.{a} : design type {typ}, code type {c['fields'][a]}")
        for op, sigs in d["operations"].items():
            for ptypes, typ, _ in sigs:
                checked["operations"] += 1
                if op not in c["methods"]:
                    problems.append(f"{cls}.{op}({ptypes}) : operation not found in the code")
                    continue
                want = split_params(ptypes) if ptypes else []   # "Map<Integer,BufferedImage>" is one parameter
                match = [m for m in c["methods"][op] if len(m[0]) == len(want) and all(same_type(w, g) for w, g in zip(want, m[0]))]
                if not match:
                    got = " | ".join(f"({', '.join(p)}) : {rt}" for p, rt in c["methods"][op])
                    problems.append(f"{cls}.{op}({ptypes}) : parameters differ, code has {got}")
                elif typ and not any(same_type(typ, m[1]) for m in match):
                    problems.append(f"{cls}.{op}({ptypes}) : design returns {typ}, code returns {match[0][1]}")
    # sequence messages: the receiver's design class (and its code) must have the called operation
    if SEQ.exists():
        by_class = defaultdict(set)
        for (pkg, cls), d in design.items():
            by_class[cls] |= set(d["operations"])
        for r in csv.reader(SEQ.read_text(encoding="utf-8").splitlines(), delimiter="\t"):
            if not r or r[0].startswith("#"):
                continue
            diagram, number, sender, receiver, label, is_return = r[:6]
            if is_return == "true" or receiver not in by_class:
                continue   # returns and messages to actors / external systems
            m = re.search(r"(?:^|: )(\w+)\(", label)
            if not m:
                continue   # plain event, e.g. "click Add to cart" sent to a view
            checked["sequence calls"] += 1
            if m.group(1) == receiver:
                continue   # constructor call, e.g. CardData(holder, number, expiry, cvv)
            if m.group(1) not in by_class[receiver] and m.group(1) in by_class.get("Work", set()):
                # Database.inTransaction(work) calls back Work.run(daos); the Work is the lambda written in the
                # service, so the diagrams send run(daos) to the service lifeline. Accept it only when the service
                # really passes a lambda to inTransaction.
                src = next((ROOT / "app" / "src" / "main" / "java").rglob(f"{receiver}.java"), None)
                if src and "inTransaction(" in src.read_text(encoding="utf-8"):
                    continue
            if m.group(1) not in by_class[receiver]:
                problems.append(f"{diagram} message {number} '{label}': {receiver} has no operation {m.group(1)}")
    # the AI package depends on nothing else of the application (G0, G1, G8): Document in, Hit out
    for f in sorted((ROOT / "app" / "src" / "main" / "java" / "vn" / "ptit" / "ecom" / "ai").glob("*.java")):
        checked["ai files without application imports"] += 1
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.startswith("import vn.ptit.ecom."):
                problems.append(f"ai/{f.name} imports {line[7:].rstrip(';')}: the AI package must not depend on the application")
    for p in problems:
        print("FAIL " + p)
    print("checked " + ", ".join(f"{v} {k}" for k, v in checked.items()))
    print(f"{len(problems)} problems" if problems else "design and code agree")
    return len(problems)


if __name__ == "__main__":
    sys.exit(min(main(), 100))
