package __Design.vn.ptit.ecom.model.customer;

public class Customer {
	private int _id;
	private String _email;
	private String _phone;
	public FullName _fullName;

	public BigDecimal discountRate() {
		throw new UnsupportedOperationException();
	}

	public String kindLabel() {
		throw new UnsupportedOperationException();
	}
}