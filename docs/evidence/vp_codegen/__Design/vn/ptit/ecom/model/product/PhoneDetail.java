package __Design.vn.ptit.ecom.model.product;

public class PhoneDetail implements ProductDetail {
	private String os;
	private int storageGb;
	private Integer cameraMp;
	private double screenInch;
	private Integer batteryMah;
	private int warrantyMonths;

	public DetailKind kind() {
		throw new UnsupportedOperationException();
	}

	public List<Spec> specs() {
		throw new UnsupportedOperationException();
	}
}