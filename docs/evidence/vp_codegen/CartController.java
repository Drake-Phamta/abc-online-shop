package __Design.vn.ptit.ecom.controller;

import __Design.vn.ptit.ecom.service.CartService;

public class CartController {
	private CartService carts;

	public CartView viewCart(HttpSession session) {
		throw new UnsupportedOperationException();
	}

	public CartView addItem(AddItem req, HttpSession session) {
		throw new UnsupportedOperationException();
	}

	public CartView changeQuantity(int productId, ChangeQuantity req, HttpSession session) {
		throw new UnsupportedOperationException();
	}

	public CartView removeItem(int productId, HttpSession session) {
		throw new UnsupportedOperationException();
	}
}