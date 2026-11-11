package __Design.vn.ptit.ecom.service;

import __Design.vn.ptit.ecom.dao.Database;
import __Design.vn.ptit.ecom.integration.CardProvider;

public class PaymentService {
	private Database db;
	private CardProvider provider;

	public PaymentResult pay(int orderId, int customerId, CardData card) {
		throw new UnsupportedOperationException();
	}
}