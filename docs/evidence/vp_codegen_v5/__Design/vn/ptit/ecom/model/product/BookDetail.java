package __Design.vn.ptit.ecom.model.product;

public class BookDetail extends Product {
	private String _author;
	private String _publisher;
	private Integer _pages;
	private String _language;

	public DetailKind kind() {
		throw new UnsupportedOperationException();
	}

	public List<Spec> specs() {
		throw new UnsupportedOperationException();
	}
}