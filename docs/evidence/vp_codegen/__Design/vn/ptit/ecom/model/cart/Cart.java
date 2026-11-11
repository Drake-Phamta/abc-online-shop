package __Design.vn.ptit.ecom.model.cart;

import java.util.Vector;

public class Cart {
	private int id;
	private int customerId;
	public Vector<CartItem> items = new Vector<CartItem>();

	public CartItem addItem(Product product, int quantity) {
		throw new UnsupportedOperationException();
	}

	public void setQuantity(int productId, int quantity) {
		throw new UnsupportedOperationException();
	}

	public void removeItem(int productId) {
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