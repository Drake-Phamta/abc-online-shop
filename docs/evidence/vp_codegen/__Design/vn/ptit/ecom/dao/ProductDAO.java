package __Design.vn.ptit.ecom.dao;

public interface ProductDAO {

	public List<Category> categories();

	public List<Product> search(String keyword, String categorySlug, Sort sort);

	public Optional<Product> findById(int id);

	public Map<Integer__Product> findByIds(Collection<Integer> ids);

	public boolean reserveStock(int productId, int quantity);

	public void releaseStock(int productId, int quantity);

	public void updateStock(int productId, int quantity);

	public List<Product> listForStock();
}