package __Design.vn.ptit.ecom.model.cart;

import __Design.vn.ptit.ecom.model.product.Product;

public class CartItem {
	private int _quantity;
	private long _cartPrice;
	public Product _product;

	public long subTotal() {
		throw new UnsupportedOperationException();
	}
}