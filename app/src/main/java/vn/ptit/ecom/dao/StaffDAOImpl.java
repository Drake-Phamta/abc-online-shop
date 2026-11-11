package vn.ptit.ecom.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Optional;
import vn.ptit.ecom.model.customer.Account;
import vn.ptit.ecom.model.customer.Role;

class StaffDAOImpl implements StaffDAO {
    private final Connection connection;

    StaffDAOImpl(Connection connection) {
        this.connection = connection;
    }

    @Override
    public Optional<Account> findAccount(String email) throws SQLException {
        try (PreparedStatement ps = Jdbc.prepare(connection, "SELECT * FROM staff WHERE lower(email) = lower(?)", email);
             ResultSet rs = ps.executeQuery()) {
            if (!rs.next()) return Optional.empty();
            return Optional.of(new Account(Role.valueOf(rs.getString("role")), rs.getInt("staff_id"),
                    rs.getString("full_name"), rs.getString("password_hash")));
        }
    }
}
