package vn.ptit.ecom.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import vn.ptit.ecom.model.cart.Cart;
import vn.ptit.ecom.model.cart.CartItem;

class CartDAOImpl implements CartDAO {
    private final Connection connection;

    CartDAOImpl(Connection connection) {
        this.connection = connection;
    }

    @Override
    public Cart findOrCreate(int customerId) throws SQLException {
        Integer cartId = null;
        try (PreparedStatement ps = Jdbc.prepare(connection, "SELECT CartId FROM Cart WHERE CustomerId = ?", customerId);
             ResultSet rs = ps.executeQuery()) {
            if (rs.next()) cartId = rs.getInt(1);
        }
        if (cartId == null) {
            String now = Jdbc.ts(LocalDateTime.now());
            cartId = Jdbc.insert(connection, "INSERT INTO Cart (CustomerId, CreatedAt, UpdatedAt) VALUES (?, ?, ?)",
                    customerId, now, now);
        }
        List<CartItem> items = new ArrayList<>();
        String sql = "SELECT ci.Quantity, ci.CartPrice, p.*, c.ParentId, c.Name AS category_name, c.Slug, c.DetailKind "
                + "FROM CartItem ci JOIN Product p ON p.ProductId = ci.ProductId "
                + "JOIN Category c ON c.CategoryId = p.CategoryId WHERE ci.CartId = ? ORDER BY ci.CartItemId";
        try (PreparedStatement ps = Jdbc.prepare(connection, sql, cartId); ResultSet rs = ps.executeQuery()) {
            while (rs.next())
                items.add(new CartItem(ProductDAOImpl.map(rs), rs.getInt("Quantity"), rs.getLong("CartPrice")));
        }
        return new Cart(cartId, customerId, items);
    }

    @Override
    public void save(Cart cart) throws SQLException {
        Jdbc.update(connection, "DELETE FROM CartItem WHERE CartId = ?", cart.getId());
        for (CartItem i : cart.getItems())
            Jdbc.update(connection, "INSERT INTO CartItem (CartId, ProductId, Quantity, CartPrice) VALUES (?, ?, ?, ?)",
                    cart.getId(), i.getProduct().getId(), i.getQuantity(), i.getCartPrice());
        Jdbc.update(connection, "UPDATE Cart SET UpdatedAt = ? WHERE CartId = ?", Jdbc.ts(LocalDateTime.now()), cart.getId());
    }

    @Override
    public void clear(Cart cart) throws SQLException {
        Jdbc.update(connection, "DELETE FROM CartItem WHERE CartId = ?", cart.getId());
        Jdbc.update(connection, "UPDATE Cart SET UpdatedAt = ? WHERE CartId = ?", Jdbc.ts(LocalDateTime.now()), cart.getId());
    }
}
