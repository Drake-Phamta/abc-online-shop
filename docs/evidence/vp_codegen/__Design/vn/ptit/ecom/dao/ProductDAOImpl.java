package __Design.vn.ptit.ecom.dao;

public class ProductDAOImpl implements ProductDAO {
	private Connection connection;

	public List<Category> categories() {
		throw new UnsupportedOperationException();
	}

	public List<Product> search(String keyword, String categorySlug, Sort sort) {
		throw new UnsupportedOperationException();
	}

	public Optional<Product> findById(int id) {
		throw new UnsupportedOperationException();
	}

	public Map<Integer__Product> findByIds(Collection<Integer> ids) {
		throw new UnsupportedOperationException();
	}

	public boolean reserveStock(int productId, int quantity) {
		throw new UnsupportedOperationException();
	}

	public void releaseStock(int productId, int quantity) {
		throw new UnsupportedOperationException();
	}

	public void updateStock(int productId, int quantity) {
		throw new UnsupportedOperationException();
	}

	public List<Product> listForStock() {
		throw new UnsupportedOperationException();
	}
}