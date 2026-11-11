package __Design.vn.ptit.ecom.controller;

import __Design.vn.ptit.ecom.service.OrderService;

public class OrderController {
	private OrderService orders;

	public Map checkout(HttpSession session) {
		throw new UnsupportedOperationException();
	}

	public Map placeOrder(PlaceOrder req, HttpSession session) {
		throw new UnsupportedOperationException();
	}

	public List<OrderSummary> myOrders(HttpSession session) {
		throw new UnsupportedOperationException();
	}

	public OrderView order(int id, HttpSession session) {
		throw new UnsupportedOperationException();
	}

	public OrderView cancelByCustomer(int id, HttpSession session) {
		throw new UnsupportedOperationException();
	}

	public List<BoardCard> board(HttpSession session) {
		throw new UnsupportedOperationException();
	}

	public OrderView process(int id, HttpSession session) {
		throw new UnsupportedOperationException();
	}

	public OrderView cancelByStaff(int id, HttpSession session) {
		throw new UnsupportedOperationException();
	}
}