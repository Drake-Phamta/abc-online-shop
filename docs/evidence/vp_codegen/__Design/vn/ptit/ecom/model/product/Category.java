package __Design.vn.ptit.ecom.model.product;

public class Category {
	private int id;
	private Integer parentId;
	private String name;
	private String slug;
	private DetailKind detailKind;

	public boolean isLeaf() {
		throw new UnsupportedOperationException();
	}
}