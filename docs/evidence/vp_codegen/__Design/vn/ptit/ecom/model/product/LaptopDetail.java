package __Design.vn.ptit.ecom.model.product;

public class LaptopDetail implements ProductDetail {
	private String cpu;
	private int ramGb;
	private int storageGb;
	private double screenInch;
	private int warrantyMonths;

	public DetailKind kind() {
		throw new UnsupportedOperationException();
	}

	public List<Spec> specs() {
		throw new UnsupportedOperationException();
	}
}