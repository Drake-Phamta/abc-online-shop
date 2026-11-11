package __Design.vn.ptit.ecom.dao;

public class OrderDAOImpl implements OrderDAO {
	private Connection connection;

	public void insert(Order order) {
		throw new UnsupportedOperationException();
	}

	public Optional<Order> findById(int id) {
		throw new UnsupportedOperationException();
	}

	public List<OrderSummary> findByCustomer(int customerId) {
		throw new UnsupportedOperationException();
	}

	public List<OrderSummary> findAll() {
		throw new UnsupportedOperationException();
	}

	public void saveProgress(Order order) {
		throw new UnsupportedOperationException();
	}
}