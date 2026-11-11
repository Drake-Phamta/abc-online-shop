package vn.ptit.ecom.dao;

import java.sql.SQLException;
import java.util.List;
import java.util.Optional;
import vn.ptit.ecom.model.customer.Account;
import vn.ptit.ecom.model.customer.Address;
import vn.ptit.ecom.model.customer.Customer;

public interface CustomerDAO {

    /** UC02: login data of a customer account. */
    Optional<Account> findAccount(String email) throws SQLException;

    /** The customer as Customer, CustomerVIP or CustomerNew. */
    Optional<Customer> findById(int customerId) throws SQLException;

    List<Address> addresses(int customerId) throws SQLException;

    Optional<Address> address(int addressId) throws SQLException;
}
