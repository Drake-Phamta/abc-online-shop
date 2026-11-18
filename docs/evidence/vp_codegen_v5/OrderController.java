package __Design.vn.ptit.ecom.controller;

import __Design.vn.ptit.ecom.service.OrderService;

public class OrderController {
	private OrderService _orders;

	public Map checkout(HttpSession aSession) {
		throw new UnsupportedOperationException();
	}

	public Map placeOrder(PlaceOrder aReq, HttpSession aSession) {
		throw new UnsupportedOperationException();
	}

	public List<OrderSummary> myOrders(HttpSession aSession) {
		throw new UnsupportedOperationException();
	}

	public OrderView order(int aId, HttpSession aSession) {
		throw new UnsupportedOperationException();
	}

	public OrderView cancelByCustomer(int aId, HttpSession aSession) {
		throw new UnsupportedOperationException();
	}

	public List<BoardCard> board(HttpSession aSession) {
		throw new UnsupportedOperationException();
	}

	public OrderView process(int aId, HttpSession aSession) {
		throw new UnsupportedOperationException();
	}

	public OrderView cancelByStaff(int aId, HttpSession aSession) {
		throw new UnsupportedOperationException();
	}
}