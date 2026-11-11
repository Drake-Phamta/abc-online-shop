package __Design.vn.ptit.ecom.model.product;

public class BookDetail implements ProductDetail {
	private String author;
	private String publisher;
	private Integer pages;
	private String language;

	public DetailKind kind() {
		throw new UnsupportedOperationException();
	}

	public List<Spec> specs() {
		throw new UnsupportedOperationException();
	}
}