package __Design.vn.ptit.ecom.service;

import __Design.vn.ptit.ecom.dao.Database;

public class ShippingService {
	private Database _db;

	public OrderDetails ship(int aOrderId, String aCarrier, String aTrackingNumber, String aStaffName) {
		throw new UnsupportedOperationException();
	}

	public OrderDetails deliver(int aOrderId, String aStaffName) {
		throw new UnsupportedOperationException();
	}
}