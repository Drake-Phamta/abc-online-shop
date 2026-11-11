package vn.ptit.ecom.model.order;

/** A line of an order; unitPrice and productName are the values at checkout (historical facts). */
public record OrderItem(Integer id, int productId, String productName, int quantity, long unitPrice) {

    public long subTotal() { return unitPrice * quantity; }
}
