package __Design.vn.ptit.ecom.model.customer;

public class Customer {
	private int id;
	private String email;
	private String phone;
	public FullName fullName;

	public BigDecimal discountRate() {
		throw new UnsupportedOperationException();
	}

	public String kindLabel() {
		throw new UnsupportedOperationException();
	}
}