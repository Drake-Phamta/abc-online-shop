package __Design.vn.ptit.ecom.model.cart;

import __Design.vn.ptit.ecom.model.product.Product;

public class CartItem {
	private int quantity;
	private long cartPrice;
	public Product product;

	public long subTotal() {
		throw new UnsupportedOperationException();
	}
}