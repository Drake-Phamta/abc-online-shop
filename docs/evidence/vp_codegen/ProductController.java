package __Design.vn.ptit.ecom.controller;

import __Design.vn.ptit.ecom.service.CatalogService;

public class ProductController {
	private CatalogService catalog;

	public List<CategoryNode> categories() {
		throw new UnsupportedOperationException();
	}

	public List<ProductCard> search(String q, String category, Sort sort) {
		throw new UnsupportedOperationException();
	}

	public ProductPage product(int id) {
		throw new UnsupportedOperationException();
	}

	public List<StockRow> stock(HttpSession session) {
		throw new UnsupportedOperationException();
	}

	public StockRow updateStock(int id, StockChange change, HttpSession session) {
		throw new UnsupportedOperationException();
	}
}