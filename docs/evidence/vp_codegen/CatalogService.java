package __Design.vn.ptit.ecom.service;

import __Design.vn.ptit.ecom.dao.Database;
import __Design.vn.ptit.ecom.model.product.Product;

public class CatalogService {
	private Database db;

	public List<Category> categories() {
		throw new UnsupportedOperationException();
	}

	public List<Product> search(String keyword, String categorySlug, Sort sort) {
		throw new UnsupportedOperationException();
	}

	public ProductDetails product(int id) {
		throw new UnsupportedOperationException();
	}

	public List<Product> stockList() {
		throw new UnsupportedOperationException();
	}

	public Product updateStock(int productId, int quantity) {
		throw new UnsupportedOperationException();
	}
}