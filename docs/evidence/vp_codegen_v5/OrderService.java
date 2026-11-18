package __Design.vn.ptit.ecom.service;

import __Design.vn.ptit.ecom.dao.Database;
import __Design.vn.ptit.ecom.model.order.Order;

public class OrderService {
	private Database _db;

	public Checkout checkout(int aCustomerId) {
		throw new UnsupportedOperationException();
	}

	public Order placeOrder(int aCustomerId, int aAddressId, PaymentMethod aMethod, Long aExpectedTotal) {
		throw new UnsupportedOperationException();
	}

	public List<OrderSummary> ordersOf(int aCustomerId) {
		throw new UnsupportedOperationException();
	}

	public List<OrderSummary> allOrders() {
		throw new UnsupportedOperationException();
	}

	public OrderDetails details(int aOrderId, Integer aCustomerId) {
		throw new UnsupportedOperationException();
	}

	public OrderDetails cancel(int aOrderId, Integer aCustomerId, Actor aActor, String aActorName) {
		throw new UnsupportedOperationException();
	}

	public OrderDetails process(int aOrderId, String aStaffName) {
		throw new UnsupportedOperationException();
	}
}