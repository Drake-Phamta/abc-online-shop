package __Design.vn.ptit.ecom.model.customer;

public class Address {
	private int _id;
	private int _customerId;
	private String _recipientName;
	private String _phone;
	private String _houseNumber;
	private String _street;
	private String _district;
	private String _city;
	private boolean _isDefault;

	public String oneLine() {
		throw new UnsupportedOperationException();
	}
}