# -*- coding: utf-8 -*-
"""Builds db/schema.sql, the schema of the running shop, from the DDL that Visual Paradigm generated from the data model.

Input
  db/vp/vp_ddl.sql   written by VP (Tools > DB > Generate Database, SQLite) from the ERD that Synchronize to Entity
                     Relationship Diagram generated from the class diagram of the Data Model file
  RULES below        the constraints VP cannot write because the data model holds no such rule: UNIQUE, CHECK and
                     ON DELETE CASCADE (business rules of Chapter 1)
Output
  db/schema.sql      the same tables, columns, types, NOT NULL, primary keys and foreign keys as the VP DDL, one column
                     per line, with the hand-written constraints added and marked with a comment

Run: python db/make_schema.py   (db/compare_schema.py then checks the result against the VP DDL)
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VP = ROOT / "vp" / "vp_ddl.sql"
OUT = ROOT / "schema.sql"

# column constraints added by hand: table -> {column: constraint}
CHECKS = {
    "Category": {"Slug": "UNIQUE", "DetailKind": "CHECK (DetailKind IN ('BOOK', 'LAPTOP', 'PHONE', 'APPAREL'))"},
    "Product": {"Sku": "UNIQUE", "Price": "CHECK (Price > 0)", "StockQuantity": "CHECK (StockQuantity >= 0)",
                "Status": "CHECK (Status IN ('ACTIVE', 'HIDDEN'))"},
    "BookDetail": {"Pages": "CHECK (Pages > 0)"},
    "LaptopDetail": {"RamGb": "CHECK (RamGb > 0)", "StorageGb": "CHECK (StorageGb > 0)",
                     "WarrantyMonths": "CHECK (WarrantyMonths >= 0)"},
    "PhoneDetail": {"StorageGb": "CHECK (StorageGb > 0)", "CameraMp": "CHECK (CameraMp > 0)",
                    "BatteryMah": "CHECK (BatteryMah > 0)", "WarrantyMonths": "CHECK (WarrantyMonths >= 0)"},
    "Customer": {"Email": "UNIQUE"},
    "Address": {"IsDefault": "CHECK (IsDefault IN (0, 1))"},
    "CustomerVIP": {"VipLevel": "CHECK (VipLevel BETWEEN 1 AND 3)",
                    "DiscountRate": "CHECK (DiscountRate > 0 AND DiscountRate <= 0.5)",
                    "RewardPoints": "CHECK (RewardPoints >= 0)"},
    "Staff": {"Email": "UNIQUE", "Role": "CHECK (Role IN ('SALES', 'WAREHOUSE'))"},
    "Cart": {"CustomerId": "UNIQUE"},
    "CartItem": {"Quantity": "CHECK (Quantity > 0)", "CartPrice": "CHECK (CartPrice > 0)"},
    "Orders": {"Status": "CHECK (Status IN ('PENDING_PAYMENT', 'PLACED', 'PAID', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED'))",
               "PaymentMethod": "CHECK (PaymentMethod IN ('CARD', 'COD'))", "Subtotal": "CHECK (Subtotal > 0)",
               "Discount": "CHECK (Discount >= 0)", "ShippingFee": "CHECK (ShippingFee >= 0)",
               "TotalAmount": "CHECK (TotalAmount = Subtotal - Discount + ShippingFee)"},
    "OrderItem": {"Quantity": "CHECK (Quantity > 0)", "UnitPrice": "CHECK (UnitPrice > 0)"},
    "Payment": {"Method": "CHECK (Method IN ('CARD', 'CASH'))", "Amount": "CHECK (Amount > 0)",
                "Status": "CHECK (Status IN ('APPROVED', 'DECLINED', 'REFUNDED', 'COMPLETED'))"},
    "PayCash": {"CashReceived": "CHECK (CashReceived > 0)", "ChangeAmount": "CHECK (ChangeAmount >= 0)"},
    "Shipping": {"OrderId": "UNIQUE", "TrackingNumber": "UNIQUE", "ShippingFee": "CHECK (ShippingFee >= 0)",
                 "Status": "CHECK (Status IN ('IN_TRANSIT', 'DELIVERED'))"},
}
# table constraints added by hand: one product per cart line and per order line
UNIQUES = {"CartItem": "UNIQUE (CartId, ProductId)", "OrderItem": "UNIQUE (OrderId, ProductId)"}
# delete rules added by hand: a detail row and a cart line go with their parent row
CASCADE = {("BookDetail", "ProductId"), ("LaptopDetail", "ProductId"), ("PhoneDetail", "ProductId"),
           ("ApparelDetail", "ProductId"), ("CartItem", "CartId")}


def split_top(s):
    """Split the body of a CREATE TABLE at the commas that are not inside parentheses."""
    parts, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())
    return parts


def main():
    ddl = VP.read_text(encoding="utf-8")
    out = ["-- ABC Online Shop: the schema of the running shop.",
           "-- Tables, columns, types, NOT NULL, primary keys and foreign keys are copied from db/vp/vp_ddl.sql, the DDL that",
           "-- Visual Paradigm generated (Tools > DB > Generate Database, SQLite) from the data model of vp/2_DataModel.vpp.",
           "-- Added by hand (marked \"-- rule\"): UNIQUE, CHECK and ON DELETE CASCADE, which the data model cannot express.",
           "-- Built by db/make_schema.py. Money is integer VND. Run with PRAGMA foreign_keys = ON.", ""]
    n = 0
    for m in re.finditer(r"CREATE TABLE (\w+) \((.*?)\);", ddl, re.S):
        table, body = m.group(1), m.group(2)
        lines = []
        for part in split_top(body):
            fk = re.match(r"FOREIGN KEY\((\w+)\) REFERENCES (\w+)\((\w+)\)", part)
            if fk:
                col = fk.group(1)
                text = f"FOREIGN KEY ({col}) REFERENCES {fk.group(2)} ({fk.group(3)})"
                if (table, col) in CASCADE:
                    text += " ON DELETE CASCADE  -- rule"
                lines.append(text)
                continue
            if part.startswith("PRIMARY KEY"):
                lines.append(part)
                continue
            col = part.split()[0]
            rule = CHECKS.get(table, {}).get(col)
            lines.append(part + (f" {rule}  -- rule" if rule else ""))
        if table in UNIQUES:
            lines.append(UNIQUES[table] + "  -- rule")
        # a trailing "-- comment" must not swallow the comma: put the comma before the comment
        rendered = []
        for i, l in enumerate(lines):
            comma = "," if i < len(lines) - 1 else ""
            if "  -- " in l:
                code, note = l.split("  -- ", 1)
                rendered.append(f"  {code}{comma}  -- {note}")
            else:
                rendered.append(f"  {l}{comma}")
        out.append(f"CREATE TABLE {table} (")
        out += rendered
        out.append(");")
        out.append("")
        n += 1
    OUT.write_text("\n".join(out), encoding="utf-8")
    used = sum(len(v) for v in CHECKS.values()) + len(UNIQUES) + len(CASCADE)
    print(f"{OUT.name}: {n} tables from the VP DDL, {used} hand-written constraints")


if __name__ == "__main__":
    main()
