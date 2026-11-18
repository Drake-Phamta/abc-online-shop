package __Design.vn.ptit.ecom.model.product;

public class Category {
	private int _id;
	private Integer _parentId;
	private String _name;
	private String _slug;
	private DetailKind _detailKind;

	public boolean isLeaf() {
		throw new UnsupportedOperationException();
	}
}