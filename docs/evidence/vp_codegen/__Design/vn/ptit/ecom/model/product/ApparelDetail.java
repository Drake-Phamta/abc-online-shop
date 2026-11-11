package __Design.vn.ptit.ecom.model.product;

public class ApparelDetail implements ProductDetail {
	private String sizeLabel;
	private String color;
	private String material;

	public DetailKind kind() {
		throw new UnsupportedOperationException();
	}

	public List<Spec> specs() {
		throw new UnsupportedOperationException();
	}
}