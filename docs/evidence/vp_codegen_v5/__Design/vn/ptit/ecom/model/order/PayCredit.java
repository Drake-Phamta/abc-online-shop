package __Design.vn.ptit.ecom.model.order;

public class PayCredit extends Payment {
	private String _cardHolder;
	private String _cardLast4;
	private String _expiry;
	private String _providerToken;

	public String method() {
		throw new UnsupportedOperationException();
	}
}