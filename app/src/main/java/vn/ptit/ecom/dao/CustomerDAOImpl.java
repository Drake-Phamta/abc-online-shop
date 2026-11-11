package vn.ptit.ecom.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import vn.ptit.ecom.model.customer.Account;
import vn.ptit.ecom.model.customer.Address;
import vn.ptit.ecom.model.customer.Customer;
import vn.ptit.ecom.model.customer.CustomerNew;
import vn.ptit.ecom.model.customer.CustomerVIP;
import vn.ptit.ecom.model.customer.FullName;
import vn.ptit.ecom.model.customer.Role;

class CustomerDAOImpl implements CustomerDAO {
    private final Connection connection;

    CustomerDAOImpl(Connection connection) {
        this.connection = connection;
    }

    @Override
    public Optional<Account> findAccount(String email) throws SQLException {
        try (PreparedStatement ps = Jdbc.prepare(connection, "SELECT * FROM customer WHERE lower(email) = lower(?)", email);
             ResultSet rs = ps.executeQuery()) {
            if (!rs.next()) return Optional.empty();
            return Optional.of(new Account(Role.CUSTOMER, rs.getInt("customer_id"), name(rs).display(),
                    rs.getString("password_hash")));
        }
    }

    @Override
    public Optional<Customer> findById(int customerId) throws SQLException {
        String sql = "SELECT c.*, v.vip_level, v.discount_rate, v.reward_points, n.registered_date, n.welcome_voucher "
                + "FROM customer c LEFT JOIN customer_vip v ON v.customer_id = c.customer_id "
                + "LEFT JOIN customer_new n ON n.customer_id = c.customer_id WHERE c.customer_id = ?";
        try (PreparedStatement ps = Jdbc.prepare(connection, sql, customerId); ResultSet rs = ps.executeQuery()) {
            if (!rs.next()) return Optional.empty();
            int id = rs.getInt("customer_id");
            FullName name = name(rs);
            String email = rs.getString("email"), phone = rs.getString("phone");
            if (Jdbc.intOrNull(rs, "vip_level") != null)
                return Optional.of(new CustomerVIP(id, name, email, phone, rs.getInt("vip_level"),
                        rs.getBigDecimal("discount_rate"), rs.getInt("reward_points")));
            if (rs.getString("registered_date") != null)
                return Optional.of(new CustomerNew(id, name, email, phone,
                        java.time.LocalDate.parse(rs.getString("registered_date")), rs.getString("welcome_voucher")));
            return Optional.of(new Customer(id, name, email, phone));
        }
    }

    @Override
    public List<Address> addresses(int customerId) throws SQLException {
        List<Address> out = new ArrayList<>();
        try (PreparedStatement ps = Jdbc.prepare(connection,
                "SELECT * FROM address WHERE customer_id = ? ORDER BY is_default DESC, address_id", customerId);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) out.add(address(rs));
        }
        return out;
    }

    @Override
    public Optional<Address> address(int addressId) throws SQLException {
        try (PreparedStatement ps = Jdbc.prepare(connection, "SELECT * FROM address WHERE address_id = ?", addressId);
             ResultSet rs = ps.executeQuery()) {
            return rs.next() ? Optional.of(address(rs)) : Optional.empty();
        }
    }

    private static FullName name(ResultSet rs) throws SQLException {
        return new FullName(rs.getString("first_name"), rs.getString("middle_name"), rs.getString("last_name"));
    }

    private static Address address(ResultSet rs) throws SQLException {
        return new Address(rs.getInt("address_id"), rs.getInt("customer_id"), rs.getString("recipient_name"),
                rs.getString("phone"), rs.getString("house_number"), rs.getString("street"), rs.getString("district"),
                rs.getString("city"), rs.getInt("is_default") == 1);
    }
}
