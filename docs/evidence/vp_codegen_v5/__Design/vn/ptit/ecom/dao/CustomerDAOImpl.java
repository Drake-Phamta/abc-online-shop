package __Design.vn.ptit.ecom.dao;

public class CustomerDAOImpl implements CustomerDAO {
	private Connection _connection;

	public Optional<Account> findAccount(String aEmail) {
		throw new UnsupportedOperationException();
	}

	public Optional<Customer> findById(int aId) {
		throw new UnsupportedOperationException();
	}

	public List<Address> addresses(int aCustomerId) {
		throw new UnsupportedOperationException();
	}

	public Optional<Address> address(int aAddressId) {
		throw new UnsupportedOperationException();
	}
}