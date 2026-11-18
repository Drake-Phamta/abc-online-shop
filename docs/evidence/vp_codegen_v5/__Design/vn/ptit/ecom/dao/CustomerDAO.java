package __Design.vn.ptit.ecom.dao;

public interface CustomerDAO {

	public Optional<Account> findAccount(String aEmail);

	public Optional<Customer> findById(int aId);

	public List<Address> addresses(int aCustomerId);

	public Optional<Address> address(int aAddressId);
}