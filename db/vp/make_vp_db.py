# -*- coding: utf-8 -*-
"""Builds a real SQLite database file from the DDL that Visual Paradigm generated (Tools > DB > Generate Database,
SQLite) and, with --open, shows it in DB Browser for SQLite (read-only).

    python db/vp/make_vp_db.py                 tables of db/vp/vp_ddl.sql + the seed data -> db/vp/vp_ddl.db
    python db/vp/make_vp_db.py --empty         the tables only, as VP wrote them
    python db/vp/make_vp_db.py --ddl <file>    another DDL file, e.g. the one just generated to the Desktop
                                               -> db/vp/vp_ddl_live.db
    python db/vp/make_vp_db.py --open          then open the file in DB Browser for SQLite, on the table Orders

The tables are exactly the statements of the DDL file; nothing is added by hand (the business rules of
db/schema.sql are not in it). SQLite adds the table sqlite_sequence itself, because the keys are AUTOINCREMENT.
While DB Browser shows db/vp/vp_ddl.db, Windows does not let the file be replaced: the file already built from the
same DDL is then shown again. The .db files are generated and not kept in git.
"""
import argparse
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DDL = HERE / "vp_ddl.sql"
SEED = HERE.parent / "seed.sql"
OUT = HERE / "vp_ddl.db"


def find_db_browser():
    names = [os.environ.get("DB_BROWSER", "")]
    for base in (os.environ.get("LOCALAPPDATA", ""), os.environ.get("ProgramFiles", ""), os.environ.get("ProgramFiles(x86)", "")):
        if base:
            names.append(os.path.join(base, "Programs", "DB Browser for SQLite", "DB Browser for SQLite.exe"))
            names.append(os.path.join(base, "DB Browser for SQLite", "DB Browser for SQLite.exe"))
    names.append(shutil.which("sqlitebrowser") or "")
    return next((n for n in names if n and os.path.isfile(n)), None)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ddl", type=Path, default=DDL, help="DDL file written by VP (default: db/vp/vp_ddl.sql)")
    ap.add_argument("--empty", action="store_true", help="do not load the seed data")
    ap.add_argument("--open", action="store_true", help="open the result in DB Browser for SQLite")
    args = ap.parse_args()

    ddl = args.ddl.read_text(encoding="utf-8", errors="replace")
    default = args.ddl.resolve() == DDL
    out = OUT if default else HERE / "vp_ddl_live.db"
    tmp = out.with_suffix(".tmp")
    print(f"DDL: {args.ddl}")

    def build(with_seed):
        """A fresh database file with the DDL (and the seed data); the connection is closed if anything fails."""
        if tmp.exists():
            tmp.unlink()
        con = sqlite3.connect(tmp)
        try:
            con.execute("PRAGMA foreign_keys = ON")
            con.executescript(ddl)
            if with_seed:
                con.executescript(SEED.read_text(encoding="utf-8"))
            con.commit()
        except sqlite3.Error:
            con.close()
            raise
        return con

    try:
        con = build(False)
    except sqlite3.Error as err:
        print(f"the DDL does not run in SQLite: {err}")
        print("(a DDL generated from the practice file before the hand edits has the table Order, an SQL keyword, and"
              " key columns such as CategoryCategoryId; use the DDL generated from vp/2_DataModel.vpp)")
        if tmp.exists():
            tmp.unlink()
        return 1
    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    fks = sum(len(con.execute(f'PRAGMA foreign_key_list("{t}")').fetchall()) for t in tables)
    cols = sum(len(con.execute(f'PRAGMA table_info("{t}")').fetchall()) for t in tables)
    print(f"created {len(tables)} tables, {cols} columns, {fks} foreign keys")
    if not args.empty:
        con.close()
        try:
            con = build(True)
            rows = {t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in tables}
            bad = con.execute("PRAGMA foreign_key_check").fetchall()
            print(f"seed data loaded: {sum(rows.values())} rows, foreign key violations: {len(bad)}")
            print("  " + ", ".join(f"{t} {n}" for t, n in rows.items()))
        except sqlite3.Error as err:
            print(f"seed data not loaded ({err}): the column names differ from db/seed.sql; the tables are kept empty")
            con = build(False)
    con.close()
    try:
        os.replace(tmp, out)
    except PermissionError:
        tmp.unlink()
        if default and not args.empty and out.exists():
            print(f"{out.name} is open in DB Browser; it was built from the same DDL, so it is shown as it is")
        else:
            print(f"{out.name} is open in another program (DB Browser?): close that window and run this again")
            return 1
    print(f"database file: {out}")

    if args.open:
        exe = find_db_browser()
        if not exe:
            print("DB Browser for SQLite not found (set DB_BROWSER to its .exe); open the file above with any SQLite viewer")
            return 1
        table = "Orders" if "Orders" in tables else (tables[0] if tables else "")
        subprocess.Popen([exe, "-R", "-t", table, str(out)], close_fds=True)
        print(f"opened in DB Browser for SQLite (read-only), table {table}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
