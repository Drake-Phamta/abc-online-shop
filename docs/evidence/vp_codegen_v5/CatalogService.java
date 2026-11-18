package __Design.vn.ptit.ecom.service;

import __Design.vn.ptit.ecom.dao.Database;
import __Design.vn.ptit.ecom.model.product.Product;

public class CatalogService {
	private Database _db;

	public List<Category> categories() {
		throw new UnsupportedOperationException();
	}

	public List<Product> search(String aKeyword, String aCategorySlug, Sort aSort) {
		throw new UnsupportedOperationException();
	}

	public ProductDetails product(int aId) {
		throw new UnsupportedOperationException();
	}

	public List<Product> stockList() {
		throw new UnsupportedOperationException();
	}

	public Product updateStock(int aProductId, int aQuantity) {
		throw new UnsupportedOperationException();
	}
}