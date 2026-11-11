package __Design.vn.ptit.ecom.dao;

public interface CustomerDAO {

	public Optional<Account> findAccount(String email);

	public Optional<Customer> findById(int id);

	public List<Address> addresses(int customerId);

	public Optional<Address> address(int addressId);
}