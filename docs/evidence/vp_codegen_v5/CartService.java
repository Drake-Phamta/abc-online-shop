package __Design.vn.ptit.ecom.service;

import __Design.vn.ptit.ecom.dao.Database;
import __Design.vn.ptit.ecom.model.cart.Cart;

public class CartService {
	private Database _db;

	public Cart cart(int aCustomerId) {
		throw new UnsupportedOperationException();
	}

	public Cart addItem(int aCustomerId, int aProductId, int aQuantity) {
		throw new UnsupportedOperationException();
	}

	public Cart changeQuantity(int aCustomerId, int aProductId, int aQuantity) {
		throw new UnsupportedOperationException();
	}

	public Cart removeItem(int aCustomerId, int aProductId) {
		throw new UnsupportedOperationException();
	}
}