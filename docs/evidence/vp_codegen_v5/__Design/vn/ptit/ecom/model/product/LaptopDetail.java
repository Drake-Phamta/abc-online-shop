package __Design.vn.ptit.ecom.model.product;

public class LaptopDetail extends Product {
	private String _cpu;
	private int _ramGb;
	private int _storageGb;
	private double _screenInch;
	private int _warrantyMonths;

	public DetailKind kind() {
		throw new UnsupportedOperationException();
	}

	public List<Spec> specs() {
		throw new UnsupportedOperationException();
	}
}