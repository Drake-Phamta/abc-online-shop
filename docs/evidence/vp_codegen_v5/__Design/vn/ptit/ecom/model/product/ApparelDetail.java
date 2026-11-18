package __Design.vn.ptit.ecom.model.product;

public class ApparelDetail extends Product {
	private String _sizeLabel;
	private String _color;
	private String _material;

	public DetailKind kind() {
		throw new UnsupportedOperationException();
	}

	public List<Spec> specs() {
		throw new UnsupportedOperationException();
	}
}