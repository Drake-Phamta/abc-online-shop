package __Design.vn.ptit.ecom.controller;

import __Design.vn.ptit.ecom.service.CartService;

public class CartController {
	private CartService _carts;

	public CartView viewCart(HttpSession aSession) {
		throw new UnsupportedOperationException();
	}

	public CartView addItem(AddItem aReq, HttpSession aSession) {
		throw new UnsupportedOperationException();
	}

	public CartView changeQuantity(int aProductId, ChangeQuantity aReq, HttpSession aSession) {
		throw new UnsupportedOperationException();
	}

	public CartView removeItem(int aProductId, HttpSession aSession) {
		throw new UnsupportedOperationException();
	}
}