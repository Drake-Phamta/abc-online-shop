package __Design.vn.ptit.ecom.model.customer;

public class Address {
	private int id;
	private int customerId;
	private String recipientName;
	private String phone;
	private String houseNumber;
	private String street;
	private String district;
	private String city;
	private boolean isDefault;

	public String oneLine() {
		throw new UnsupportedOperationException();
	}
}