package __Design.vn.ptit.ecom.service;

import __Design.vn.ptit.ecom.dao.Database;

public class ShippingService {
	private Database db;

	public OrderDetails ship(int orderId, String carrier, String trackingNumber, String staffName) {
		throw new UnsupportedOperationException();
	}

	public OrderDetails deliver(int orderId, String staffName) {
		throw new UnsupportedOperationException();
	}
}