package __Design.vn.ptit.ecom.model.order;

public class OrderItem {
	private Integer _id;
	private int _productId;
	private String _productName;
	private int _quantity;
	private long _unitPrice;

	public long subTotal() {
		throw new UnsupportedOperationException();
	}
}