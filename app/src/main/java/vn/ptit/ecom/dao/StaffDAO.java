package vn.ptit.ecom.dao;

import java.sql.SQLException;
import java.util.Optional;
import vn.ptit.ecom.model.customer.Account;

public interface StaffDAO {

    /** UC02: login data of a staff account (role SALES or WAREHOUSE). */
    Optional<Account> findAccount(String email) throws SQLException;
}
