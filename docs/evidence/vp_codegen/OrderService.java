package __Design.vn.ptit.ecom.service;

import __Design.vn.ptit.ecom.dao.Database;
import __Design.vn.ptit.ecom.model.order.Order;

public class OrderService {
	private Database db;

	public Checkout checkout(int customerId) {
		throw new UnsupportedOperationException();
	}

	public Order placeOrder(int customerId, int addressId, PaymentMethod method, Long expectedTotal) {
		throw new UnsupportedOperationException();
	}

	public List<OrderSummary> ordersOf(int customerId) {
		throw new UnsupportedOperationException();
	}

	public List<OrderSummary> allOrders() {
		throw new UnsupportedOperationException();
	}

	public OrderDetails details(int orderId, Integer customerId) {
		throw new UnsupportedOperationException();
	}

	public OrderDetails cancel(int orderId, Integer customerId, Actor actor, String actorName) {
		throw new UnsupportedOperationException();
	}

	public OrderDetails process(int orderId, String staffName) {
		throw new UnsupportedOperationException();
	}
}