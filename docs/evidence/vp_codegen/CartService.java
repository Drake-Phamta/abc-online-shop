package __Design.vn.ptit.ecom.service;

import __Design.vn.ptit.ecom.dao.Database;
import __Design.vn.ptit.ecom.model.cart.Cart;

public class CartService {
	private Database db;

	public Cart cart(int customerId) {
		throw new UnsupportedOperationException();
	}

	public Cart addItem(int customerId, int productId, int quantity) {
		throw new UnsupportedOperationException();
	}

	public Cart changeQuantity(int customerId, int productId, int quantity) {
		throw new UnsupportedOperationException();
	}

	public Cart removeItem(int customerId, int productId) {
		throw new UnsupportedOperationException();
	}
}