package __Design.vn.ptit.ecom.dao;

public class OrderDAOImpl implements OrderDAO {
	private Connection _connection;

	public void insert(Order aOrder) {
		throw new UnsupportedOperationException();
	}

	public Optional<Order> findById(int aId) {
		throw new UnsupportedOperationException();
	}

	public List<OrderSummary> findByCustomer(int aCustomerId) {
		throw new UnsupportedOperationException();
	}

	public List<OrderSummary> findAll() {
		throw new UnsupportedOperationException();
	}

	public void saveProgress(Order aOrder) {
		throw new UnsupportedOperationException();
	}
}