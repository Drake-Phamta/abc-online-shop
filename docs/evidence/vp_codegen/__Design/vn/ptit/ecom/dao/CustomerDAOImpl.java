package __Design.vn.ptit.ecom.dao;

public class CustomerDAOImpl implements CustomerDAO {
	private Connection connection;

	public Optional<Account> findAccount(String email) {
		throw new UnsupportedOperationException();
	}

	public Optional<Customer> findById(int id) {
		throw new UnsupportedOperationException();
	}

	public List<Address> addresses(int customerId) {
		throw new UnsupportedOperationException();
	}

	public Optional<Address> address(int addressId) {
		throw new UnsupportedOperationException();
	}
}