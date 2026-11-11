package __Design.vn.ptit.ecom.model.product;

public class Product {
	private int id;
	private String sku;
	private String name;
	private String brand;
	private long price;
	private int stockQuantity;
	private String description;
	private String imageFile;
	private Status status;
	public Category category;
	public ProductDetail detail;

	public boolean isAvailable(int quantity) {
		throw new UnsupportedOperationException();
	}

	public void updateStock(int quantity) {
		throw new UnsupportedOperationException();
	}
}