# -*- coding: utf-8 -*-
"""From each message of the design sequences (G5, G6, G7, G9) to the code: the line where the sender makes the call
and the line where the receiver's method is declared. Input: docs/evidence/seq_messages.tsv (exported from
vp/3_Design.vpp by the VP plugin), the Java sources, the JavaScript views and the router static/js/app.js.

    python tools/seq_to_code.py            prints every message with the code lines found (to check them by eye)
    python tools/seq_to_code.py --html F   also writes the table into F between the markers
                                           <!-- seq-to-code:start --> and <!-- seq-to-code:end -->

How a call site is found: the sender is executing the method that it received last in the same diagram; the call
is searched in that method's body, in the order the code runs, including the body of a private helper of the same
class at the line where the helper is called (SearchService.search reads the catalogue in activeProducts). A call
from one view to another goes through the router (this.app.go("pay/..") -> app.js -> PaymentForm.showPayment). An
HTTP message is the api(...) call with the view's controller path. run(daos) from Database is the lambda that the
service passed to inTransaction. A label without "(" is a note or a user action. Exit code = number of call
messages without a code line.
"""
import argparse
import csv
import html
import re
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TSV = ROOT / "docs" / "evidence" / "seq_messages.tsv"
JAVA = ROOT / "app" / "src" / "main" / "java"
STATIC = ROOT / "app" / "src" / "main" / "resources" / "static" / "js"
VIEW = STATIC / "view"
ROUTER = STATIC / "app.js"
FIGURES = {"G5": ("5.9", 96), "G6": ("5.10", 97), "G7": ("5.11", 98), "G9": ("5.12", 99)}
MOD = r"(?:(?:public|private|protected|static|final|abstract|default|synchronized)\s+)*"
NOT_METHODS = {"if", "for", "while", "switch", "catch", "return", "new", "try", "synchronized", "else", "do", "throw"}


def build_files():
    out = {}
    for f in sorted(JAVA.rglob("*.java")):
        for m in re.finditer(r"\b(?:class|interface|record|enum)\s+(\w+)", f.read_text(encoding="utf-8")):
            out.setdefault(m.group(1), f)
    for f in sorted(VIEW.glob("*.js")):
        out.setdefault(f.stem, f)
    return out


FILES = build_files()


@lru_cache(maxsize=None)
def lines_of(f):
    return tuple(f.read_text(encoding="utf-8").splitlines())


def decl_name(line, js):
    """The method or constructor declared on this line, or None."""
    if js:
        m = re.match(r"\s*(?:static\s+)?(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{", line)
    else:
        m = (re.match(r"\s*" + MOD + r"(?:record|class)\s+(\w+)\s*\(", line)
             or re.match(r"\s*" + MOD + r"(?:<[^>]+>\s+)?[\w.<>\[\],? ]+?\s+(\w+)\s*\(", line)
             or re.match(r"\s*(?:public|private|protected)\s+(\w+)\s*\(", line))
        # a statement such as "Order o = Order.place(" or "return db.inTransaction(" is a call, not a declaration
        if m and re.search(r"\b(?:return|new|throw)\b|=", line.split("(")[0].replace("<", " ").split(m.group(1))[0]):
            return None
    if m and m.group(1) not in NOT_METHODS:
        return m.group(1)
    return None


def find_decl(cls, name):
    f = FILES.get(cls)
    if not f:
        return None
    js = f.suffix == ".js"
    for i, line in enumerate(lines_of(f), 1):
        if decl_name(line, js) == name:
            return f, i
    return None


def body_range(f, start):
    """Lines start..end of the block that opens on line start (brace counting; strings and comments ignored)."""
    ls = lines_of(f)
    depth, opened = 0, False
    for i in range(start - 1, len(ls)):
        s = re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//.*$', "", ls[i])
        depth += s.count("{") - s.count("}")
        opened = opened or "{" in s
        if opened and depth <= 0:
            return start, i + 1
        if not opened and s.rstrip().endswith(";"):
            return start, i + 1
    return start, len(ls)


def enclosing(f, line_no):
    """The method whose body contains line_no."""
    js = f.suffix == ".js"
    best = None
    for i, line in enumerate(lines_of(f), 1):
        if i > line_no:
            break
        n = decl_name(line, js)
        if n:
            a, b = body_range(f, i)
            if a <= line_no <= b:
                best = n  # the innermost (last) declaration that still contains the line
    return best


def methods_of(f):
    js = f.suffix == ".js"
    return {n: i for i, line in enumerate(lines_of(f), 1) if (n := decl_name(line, js))}


def run_order(f, method):
    """The lines of method in the order they run. A call of a helper is followed by the lines of the helper (one
    level): a method of the same file (SearchService.activeProducts), or a static method of another class of the
    service package (OrderService.load, called by PaymentService.pay). Each item is (file, line, helper or None,
    line of the helper call or None)."""
    d = find_decl_in_file(f, method)
    if not d:
        return []
    a, b = body_range(f, d)
    own = methods_of(f)
    out = []
    for i in range(a + 1, b + 1):
        out.append((f, i, None, None))
        if f.suffix != ".java":
            continue
        line = lines_of(f)[i - 1]
        for h in re.findall(r"(?<![\w.$])(\w+)\(", line):
            if h in own and h != method and h not in NOT_METHODS:
                ha, hb = body_range(f, own[h])
                out.extend((f, j, h, i) for j in range(ha + 1, hb + 1))
        for cls, h in re.findall(r"(?<![\w.$])([A-Z]\w+)\.(\w+)\(", line):
            g = FILES.get(cls)
            if g and g != f and "/service/" in g.as_posix():
                hd = find_decl_in_file(g, h)
                if hd and re.search(r"\bstatic\b", lines_of(g)[hd - 1]):
                    ha, hb = body_range(g, hd)
                    out.extend((g, j, f"{cls}.{h}", i) for j in range(ha + 1, hb + 1))
    return out


def implementations(cls, name):
    """For an interface: the declaration of name in each class that implements it (CartDAOImpl, SimulatedCardProvider)."""
    f = FILES.get(cls)
    if not f or not re.search(r"\binterface\s+" + cls + r"\b", "\n".join(lines_of(f))):
        return []
    out = []
    for g in sorted(set(FILES.values())):  # one file can declare several types (FILES has a key for each)
        if g.suffix == ".java" and g != f and re.search(r"\bimplements\s+(?:\w+\s*,\s*)*" + cls + r"\b", "\n".join(lines_of(g))):
            i = find_decl_in_file(g, name)
            if i:
                out.append((g, i))
    return out


def find_decl_in_file(f, name):
    js = f.suffix == ".js"
    for i, line in enumerate(lines_of(f), 1):
        if decl_name(line, js) == name:
            return i
    return None


@lru_cache(maxsize=None)
def routes():
    """route -> (view variable, method) from the switch of the router: case "pay": ... this.paymentForm.showPayment("""
    out = {}
    for i, line in enumerate(lines_of(ROUTER), 1):
        m = re.search(r'case\s+"(\w+)"\s*:(.*)', line)
        if m:
            for form, meth in re.findall(r"this\.(\w+Form)\.(\w+)\(", m.group(2)):
                out.setdefault((form[0].upper() + form[1:], meth), (m.group(1), i))
    return out


def controller_path(f):
    m = re.search(r'this\.controller\s*=\s*"([^"]+)"', "\n".join(lines_of(f)))
    return m.group(1) if m else None


def http_pattern(sender_file, verb, path):
    prefix = controller_path(sender_file)
    if prefix and path.startswith(prefix):
        rest = path[len(prefix):]
        rest_rx = "".join(r"\$\{[^}]+\}" if p.startswith("{") else re.escape(p) for p in re.split(r"(\{[^}]*\})", rest) if p)
        target = r"this\.controller\s*[,)]" if not rest else r"`\$\{this\.controller\}" + rest_rx
        return r'api\("' + verb + r'",\s*' + target
    return re.escape(path)


def rel(f):
    return f.relative_to(ROOT).as_posix()


def first_match(order, start, rx, skip_name, js):
    for k in range(start, len(order)):
        g, i, helper, at = order[k]
        line = lines_of(g)[i - 1]
        if rx.search(line) and decl_name(line, js) != skip_name:
            return k, g, i, helper, at
    return None


def resolve(rows):
    result, missing = {}, 0
    current = {}   # lifeline -> method of its current activation
    cursor = {}    # (lifeline, method) -> (position in run_order, pattern) of the last call found
    last_tx = {}   # lifeline -> (file, line) of its last inTransaction call (where the lambda starts)
    for diagram, num, sender, receiver, label, ret in rows:
        g = diagram.split()[0]
        if g not in FIGURES:
            continue
        if g not in result:
            result[g] = (diagram, [])
            current.clear(); cursor.clear(); last_tx.clear()
        e = {"num": int(num), "sender": sender, "receiver": receiver, "label": label, "note": "", "call": None,
             "via": None, "router": None, "decl": None, "impl": [], "lambda": False}
        result[g][1].append(e)
        if ret == "true":
            e["note"] = "return"
            continue
        m = re.search(r"(\w+)\s*\(", label)
        if not m:
            e["note"] = "user" if sender == "Customer" else "note"
            continue
        name = m.group(1)
        http = re.match(r"(GET|POST|PUT|PATCH|DELETE)\s+(\S+?):\s", label)
        lam = name == "run" and sender == "Database"

        # declaration on the receiver's side
        if lam:
            e["decl"], e["lambda"] = last_tx.get(receiver), True
        else:
            e["decl"] = find_decl(receiver, name)
            e["impl"] = implementations(receiver, name)

        # call site on the sender's side
        if sender != "Customer":
            f = FILES.get(sender)
            js = f is not None and f.suffix == ".js"
            decl_line = lines_of(e["decl"][0])[e["decl"][1] - 1] if e["decl"] else ""
            if http:
                pattern = http_pattern(f, http.group(1), http.group(2))
            elif lam:
                pattern = r"\.run\("
            elif re.match(r"\s*" + MOD + r"(?:record|class)\s+" + name + r"\b", decl_line):
                pattern = r"new\s+" + name + r"\("
            else:
                pattern = r"(?<![\w$])" + name + r"\("
            rx = re.compile(pattern)
            meth = current.get(sender)
            found = None
            if f and not meth:
                # the sender reacts to the user (no method received yet): its whole file, with a specific pattern;
                # the method that contains the call becomes its current method
                for i, line in enumerate(lines_of(f), 1):
                    if rx.search(line) and decl_name(line, js) != name:
                        meth = current[sender] = enclosing(f, i)
                        order = run_order(f, meth)
                        k = next((k for k, o in enumerate(order) if o[0] == f and o[1] == i), 0)
                        found = (k, f, i, None, None)
                        break
            elif f:
                order = run_order(f, meth)
                pos, last_pat = cursor.get((sender, meth), (0, None))
                start = pos + 1 if last_pat == pattern else pos
                found = first_match(order, start, rx, name, js)
                if not found and js and receiver in FILES and FILES[receiver].suffix == ".js":
                    r = routes().get((receiver, name))
                    if r:
                        found = first_match(order, start, re.compile(r"this\.app\.go\(`" + re.escape(r[0]) + r"/"), name, js)
                        if found:
                            e["router"] = (ROUTER, r[1])
            if found:
                k, gf, i, helper, at = found
                cursor[(sender, meth)] = (k, pattern)
                e["call"] = (gf, i)
                if helper:
                    e["via"] = (helper, at)
                if name == "inTransaction":
                    last_tx[sender] = (gf, i)
        if not lam:
            # a new activation of the receiver: its calls are searched from the start of the method again
            current[receiver] = name
            cursor.pop((receiver, name), None)
        if not e["decl"] or (sender != "Customer" and not e["call"]):
            missing += 1
    return result, missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", type=Path)
    args = ap.parse_args()
    rows = [r for r in csv.reader(open(TSV, encoding="utf-8"), delimiter="\t") if r and not r[0].startswith("#")]
    result, missing = resolve(rows)
    for g, (diagram, entries) in result.items():
        print(f"\n=== {diagram}")
        for e in entries:
            if e["note"] == "return":
                continue
            head = f"{e['num']:>2} {e['sender']} -> {e['receiver']}: {e['label']}"
            if e["note"]:
                print(f"{head}   [{e['note']}]")
                continue
            print(head)
            for kind in ("call", "router", "decl", "impl"):
                locs = e[kind] if kind == "impl" else ([e[kind]] if e[kind] else [])
                for f, i in locs:
                    extra = ""
                    if kind == "call":
                        extra = f" in {enclosing(f, i)}" + (f" (helper {e['via'][0]} called on line {e['via'][1]})" if e["via"] else "")
                    if kind == "decl" and e["lambda"]:
                        extra = " (the lambda passed to inTransaction)"
                    print(f"     {kind:6} {f.name}:{i}{extra}  | {lines_of(f)[i - 1].strip()[:105]}")
                if not locs and kind in ("call", "decl") and not (kind == "call" and e["sender"] == "Customer"):
                    print(f"     {kind:6} NOT FOUND")
    print(f"\n{missing} call messages without a code line")
    if args.html:
        write_html(args.html, result)
    return missing


def link(loc):
    f, i = loc
    return f'<a href="../{rel(f)}#L{i}"><code>{html.escape(f.name)}:{i}</code></a>'


def write_html(path, result):
    out = ['<!-- seq-to-code:start (generated by tools/seq_to_code.py, do not edit by hand) -->',
           '<div class="lbl">Từ message của sequence sang dòng code</div>',
           '<p>Thầy có thể chỉ một message trên sequence và hỏi "dòng code nào?". Trong <code>vp/3_Design.vpp</code> '
           'mỗi message của G5, G6, G7, G9 có số thứ tự. Bảng dưới cho mỗi message là lời gọi: <b>gọi ở</b> là dòng '
           'mà lớp gửi thực hiện lời gọi, <b>định nghĩa</b> là phương thức của lớp nhận (với DAO: interface và lớp cài '
           'đặt). Trong VS Code nhấn <b>Ctrl+P</b>, gõ tên file kèm số dòng, ví dụ <code>OrderService.java:56</code>, '
           'Enter là nhảy đúng dòng. Message trả về (nét đứt) không có trong bảng. Bảng sinh bằng '
           '<code>python tools/seq_to_code.py</code> từ chính các message xuất từ VP và mã nguồn.</p>']
    for g, (diagram, entries) in result.items():
        fig, page = FIGURES[g]
        title = diagram.split(" - ", 1)[1] if " - " in diagram else diagram
        out.append(f'<details class="seq"><summary><b>{g}</b> {html.escape(title)} (Hình {fig}, tr. {page})</summary>')
        out.append('<div class="seqwrap"><table class="qa seqmap"><tr><th>#</th><th>Message</th><th>Gọi ở</th><th>Định nghĩa</th></tr>')
        for e in entries:
            if e["note"] == "return":
                continue
            msg = f'{html.escape(e["sender"])} → {html.escape(e["receiver"])}: <code>{html.escape(e["label"])}</code>'
            if e["note"]:
                text = "người dùng thao tác trên trang" if e["note"] == "user" else "ghi chú trên biểu đồ, không phải lời gọi"
                out.append(f'<tr><td>{e["num"]}</td><td>{msg}</td><td colspan="2">{text}</td></tr>')
                continue
            if e["call"]:
                call = link(e["call"]) + f' <small>trong {html.escape(enclosing(*e["call"]) or "")}'
                if e["via"]:
                    caller = FILES[e["sender"]].name
                    call += f', được gọi ở {html.escape(caller)}:{e["via"][1]}'
                call += "</small>"
                if e["router"]:
                    call += " <small>qua router</small> " + link(e["router"])
            else:
                call = "—"
            decl = link(e["decl"]) if e["decl"] else "—"
            if e["lambda"]:
                decl += " <small>lambda truyền cho inTransaction</small>"
            for impl in e["impl"]:
                decl += " <small>cài đặt</small> " + link(impl)
            out.append(f'<tr><td>{e["num"]}</td><td>{msg}</td><td>{call}</td><td>{decl}</td></tr>')
        out.append('</table></div></details>')
    out.append('<!-- seq-to-code:end -->')
    raw = path.read_bytes()
    eol = "\r\n" if b"\r\n" in raw else "\n"  # keep the line endings of the file (the repository uses LF)
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if "<!-- seq-to-code:start" not in text:
        raise SystemExit(f"markers not found in {path}")
    new = re.sub(r"<!-- seq-to-code:start.*?<!-- seq-to-code:end -->", lambda _: "\n".join(out), text, flags=re.S)
    path.write_bytes(new.replace("\n", eol).encode("utf-8"))
    print(f"table written into {path}")


if __name__ == "__main__":
    sys.exit(main())
