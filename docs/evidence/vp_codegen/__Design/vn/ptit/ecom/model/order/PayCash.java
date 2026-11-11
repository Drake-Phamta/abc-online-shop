package __Design.vn.ptit.ecom.model.order;

public class PayCash extends Payment {
	private long cashReceived;
	private long changeAmount;

	public String method() {
		throw new UnsupportedOperationException();
	}
}