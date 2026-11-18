package __Design.vn.ptit.ecom.dao;

public class ProductDAOImpl implements ProductDAO {
	private Connection _connection;

	public List<Category> categories() {
		throw new UnsupportedOperationException();
	}

	public List<Product> search(String aKeyword, String aCategorySlug, Sort aSort) {
		throw new UnsupportedOperationException();
	}

	public Optional<Product> findById(int aId) {
		throw new UnsupportedOperationException();
	}

	public Map<Integer__Product> findByIds(Collection<Integer> aIds) {
		throw new UnsupportedOperationException();
	}

	public boolean reserveStock(int aProductId, int aQuantity) {
		throw new UnsupportedOperationException();
	}

	public void releaseStock(int aProductId, int aQuantity) {
		throw new UnsupportedOperationException();
	}

	public void updateStock(int aProductId, int aQuantity) {
		throw new UnsupportedOperationException();
	}

	public List<Product> listForStock() {
		throw new UnsupportedOperationException();
	}
}