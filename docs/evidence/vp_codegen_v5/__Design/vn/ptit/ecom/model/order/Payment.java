package __Design.vn.ptit.ecom.model.order;

public abstract class Payment {
	private Integer _id;
	private long _amount;
	private Status _status;
	private LocalDateTime _paymentDate;

	public abstract String method();

	public boolean isSuccessful() {
		throw new UnsupportedOperationException();
	}
}