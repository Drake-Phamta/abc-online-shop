package vn.ptit.ecom.model.product;

/** Which detail table a leaf category's products use (Category.DetailKind). */
public enum DetailKind {
    BOOK("BookDetail"),
    LAPTOP("LaptopDetail"),
    PHONE("PhoneDetail"),
    APPAREL("ApparelDetail");

    private final String table;

    DetailKind(String table) { this.table = table; }

    public String table() { return table; }
}
