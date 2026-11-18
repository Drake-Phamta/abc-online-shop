package __Design.vn.ptit.ecom.controller;

import __Design.vn.ptit.ecom.service.CatalogService;

public class ProductController {
	private CatalogService _catalog;

	public List<CategoryNode> categories() {
		throw new UnsupportedOperationException();
	}

	public List<ProductCard> search(String aQ, String aCategory, Sort aSort) {
		throw new UnsupportedOperationException();
	}

	public ProductPage product(int aId) {
		throw new UnsupportedOperationException();
	}

	public List<StockRow> stock(HttpSession aSession) {
		throw new UnsupportedOperationException();
	}

	public StockRow updateStock(int aId, StockChange aChange, HttpSession aSession) {
		throw new UnsupportedOperationException();
	}
}