package __Design.vn.ptit.ecom.model.cart;

import java.util.Vector;

public class Cart {
	private int _id;
	private int _customerId;
	public Vector<CartItem> _items = new Vector<CartItem>();

	public CartItem addItem(Product aProduct, int aQuantity) {
		throw new UnsupportedOperationException();
	}

	public void setQuantity(int aProductId, int aQuantity) {
		throw new UnsupportedOperationException();
	}

	public void removeItem(int aProductId) {
		throw new UnsupportedOperationException();
	}

	public List<CartIssue> validate() {
		throw new UnsupportedOperationException();
	}

	public long calcTotal() {
		throw new UnsupportedOperationException();
	}

	public boolean isEmpty() {
		throw new UnsupportedOperationException();
	}
}