package __Design.vn.ptit.ecom.model.product;

public class Product {
	private int _id;
	private String _sku;
	private String _name;
	private String _brand;
	private long _price;
	private int _stockQuantity;
	private String _description;
	private String _imageFile;
	private Status _status;
	public Category _category;

	public boolean isAvailable(int aQuantity) {
		throw new UnsupportedOperationException();
	}

	public void updateStock(int aQuantity) {
		throw new UnsupportedOperationException();
	}

	public DetailKind kind() {
		throw new UnsupportedOperationException();
	}

	public List<Spec> specs() {
		throw new UnsupportedOperationException();
	}
}