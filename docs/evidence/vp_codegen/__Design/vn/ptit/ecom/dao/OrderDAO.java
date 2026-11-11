package __Design.vn.ptit.ecom.dao;

public interface OrderDAO {

	public void insert(Order order);

	public Optional<Order> findById(int id);

	public List<OrderSummary> findByCustomer(int customerId);

	public List<OrderSummary> findAll();

	public void saveProgress(Order order);
}