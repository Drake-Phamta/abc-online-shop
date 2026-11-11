package __Design.vn.ptit.ecom.model.cart;

public class CartIssue {
	private int productId;
	private String productName;
	private Kind kind;
	private long oldPrice;
	private long newPrice;
	private int available;

	public String message() {
		throw new UnsupportedOperationException();
	}
}