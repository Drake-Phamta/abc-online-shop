package __Design.vn.ptit.ecom.dao;

public interface ProductDAO {

	public List<Category> categories();

	public List<Product> search(String aKeyword, String aCategorySlug, Sort aSort);

	public Optional<Product> findById(int aId);

	public Map<Integer__Product> findByIds(Collection<Integer> aIds);

	public boolean reserveStock(int aProductId, int aQuantity);

	public void releaseStock(int aProductId, int aQuantity);

	public void updateStock(int aProductId, int aQuantity);

	public List<Product> listForStock();
}