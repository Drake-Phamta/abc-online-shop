package __Design.vn.ptit.ecom.model.product;

public class PhoneDetail extends Product {
	private String _os;
	private int _storageGb;
	private Integer _cameraMp;
	private double _screenInch;
	private Integer _batteryMah;
	private int _warrantyMonths;

	public DetailKind kind() {
		throw new UnsupportedOperationException();
	}

	public List<Spec> specs() {
		throw new UnsupportedOperationException();
	}
}