package vn.ptit.ecom.model.cart;

/** A finding of the cart validation (UC21); blocking issues stop the checkout (UC07 A1). */
public record CartIssue(int productId, String productName, Kind kind, long oldPrice, long newPrice, int available) {

    public enum Kind {
        PRICE_CHANGED(false), UNAVAILABLE(true), NOT_ENOUGH_STOCK(true);

        private final boolean blocking;
        Kind(boolean blocking) { this.blocking = blocking; }
        public boolean isBlocking() { return blocking; }
    }

    public String message() {
        return switch (kind) {
            case PRICE_CHANGED -> productName + ": price changed from " + oldPrice + " to " + newPrice + " VND.";
            case UNAVAILABLE -> productName + " is no longer sold.";
            case NOT_ENOUGH_STOCK -> productName + ": only " + available + " left in stock.";
        };
    }
}
