package vn.ptit.ecom.model.product;

/** Which detail table a leaf category's products use (category.detail_kind). */
public enum DetailKind {
    BOOK("book_detail"),
    LAPTOP("laptop_detail"),
    PHONE("phone_detail"),
    APPAREL("apparel_detail");

    private final String table;

    DetailKind(String table) { this.table = table; }

    public String table() { return table; }
}
