package __Design.vn.ptit.ecom.model.order;

public class PayCredit extends Payment {
	private String cardHolder;
	private String cardLast4;
	private String expiry;
	private String providerToken;

	public String method() {
		throw new UnsupportedOperationException();
	}
}