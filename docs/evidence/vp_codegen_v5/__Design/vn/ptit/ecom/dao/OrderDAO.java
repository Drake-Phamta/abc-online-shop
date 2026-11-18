package __Design.vn.ptit.ecom.dao;

public interface OrderDAO {

	public void insert(Order aOrder);

	public Optional<Order> findById(int aId);

	public List<OrderSummary> findByCustomer(int aCustomerId);

	public List<OrderSummary> findAll();

	public void saveProgress(Order aOrder);
}