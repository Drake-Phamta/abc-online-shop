package __Design.vn.ptit.ecom.model.order;

public abstract class Payment {
	private Integer id;
	private long amount;
	private Status status;
	private LocalDateTime paymentDate;

	public abstract String method();

	public boolean isSuccessful() {
		throw new UnsupportedOperationException();
	}
}