package __Design.vn.ptit.ecom.model.cart;

public class CartIssue {
	private int _productId;
	private String _productName;
	private Kind _kind;
	private long _oldPrice;
	private long _newPrice;
	private int _available;

	public String message() {
		throw new UnsupportedOperationException();
	}
}