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
        try (PreparedStatement ps = Jdbc.prepare(connection, "SELECT * FROM Customer WHERE lower(Email) = lower(?)", email);
             ResultSet rs = ps.executeQuery()) {
            if (!rs.next()) return Optional.empty();
            return Optional.of(new Account(Role.CUSTOMER, rs.getInt("CustomerId"), name(rs).display(),
                    rs.getString("PasswordHash")));
        }
    }

    @Override
    public Optional<Customer> findById(int customerId) throws SQLException {
        String sql = "SELECT c.*, v.VipLevel, v.DiscountRate, v.RewardPoints, n.RegisteredDate, n.WelcomeVoucher "
                + "FROM Customer c LEFT JOIN CustomerVIP v ON v.CustomerId = c.CustomerId "
                + "LEFT JOIN CustomerNew n ON n.CustomerId = c.CustomerId WHERE c.CustomerId = ?";
        try (PreparedStatement ps = Jdbc.prepare(connection, sql, customerId); ResultSet rs = ps.executeQuery()) {
            if (!rs.next()) return Optional.empty();
            int id = rs.getInt("CustomerId");
            FullName name = name(rs);
            String email = rs.getString("Email"), phone = rs.getString("Phone");
            if (Jdbc.intOrNull(rs, "VipLevel") != null)
                return Optional.of(new CustomerVIP(id, name, email, phone, rs.getInt("VipLevel"),
                        rs.getBigDecimal("DiscountRate"), rs.getInt("RewardPoints")));
            if (rs.getString("RegisteredDate") != null)
                return Optional.of(new CustomerNew(id, name, email, phone,
                        java.time.LocalDate.parse(rs.getString("RegisteredDate")), rs.getString("WelcomeVoucher")));
            return Optional.of(new Customer(id, name, email, phone));
        }
    }

    @Override
    public List<Address> addresses(int customerId) throws SQLException {
        List<Address> out = new ArrayList<>();
        try (PreparedStatement ps = Jdbc.prepare(connection,
                "SELECT * FROM Address WHERE CustomerId = ? ORDER BY IsDefault DESC, AddressId", customerId);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) out.add(address(rs));
        }
        return out;
    }

    @Override
    public Optional<Address> address(int addressId) throws SQLException {
        try (PreparedStatement ps = Jdbc.prepare(connection, "SELECT * FROM Address WHERE AddressId = ?", addressId);
             ResultSet rs = ps.executeQuery()) {
            return rs.next() ? Optional.of(address(rs)) : Optional.empty();
        }
    }

    private static FullName name(ResultSet rs) throws SQLException {
        return new FullName(rs.getString("FirstName"), rs.getString("MiddleName"), rs.getString("LastName"));
    }

    private static Address address(ResultSet rs) throws SQLException {
        return new Address(rs.getInt("AddressId"), rs.getInt("CustomerId"), rs.getString("RecipientName"),
                rs.getString("Phone"), rs.getString("HouseNumber"), rs.getString("Street"), rs.getString("District"),
                rs.getString("City"), rs.getInt("IsDefault") == 1);
    }
}
