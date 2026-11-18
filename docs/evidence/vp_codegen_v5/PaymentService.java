package __Design.vn.ptit.ecom.service;

import __Design.vn.ptit.ecom.dao.Database;
import __Design.vn.ptit.ecom.integration.CardProvider;

public class PaymentService {
	private Database _db;
	private CardProvider _provider;

	public PaymentResult pay(int aOrderId, int aCustomerId, CardData aCard) {
		throw new UnsupportedOperationException();
	}
}