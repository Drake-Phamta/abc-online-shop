package __Design.vn.ptit.ecom.model.order;

public class OrderItem {
	private Integer id;
	private int productId;
	private String productName;
	private int quantity;
	private long unitPrice;

	public long subTotal() {
		throw new UnsupportedOperationException();
	}
}