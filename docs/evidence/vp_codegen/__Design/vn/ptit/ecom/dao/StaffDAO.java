package __Design.vn.ptit.ecom.dao;

public interface StaffDAO {

	public Optional<Account> findAccount(String email);
}