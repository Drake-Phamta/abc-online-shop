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
        try (PreparedStatement ps = Jdbc.prepare(connection, "SELECT cart_id FROM cart WHERE customer_id = ?", customerId);
             ResultSet rs = ps.executeQuery()) {
            if (rs.next()) cartId = rs.getInt(1);
        }
        if (cartId == null) {
            String now = Jdbc.ts(LocalDateTime.now());
            cartId = Jdbc.insert(connection, "INSERT INTO cart (customer_id, created_at, updated_at) VALUES (?, ?, ?)",
                    customerId, now, now);
        }
        List<CartItem> items = new ArrayList<>();
        String sql = "SELECT ci.quantity, ci.cart_price, p.*, c.parent_id, c.name AS category_name, c.slug, c.detail_kind "
                + "FROM cart_item ci JOIN product p ON p.product_id = ci.product_id "
                + "JOIN category c ON c.category_id = p.category_id WHERE ci.cart_id = ? ORDER BY ci.cart_item_id";
        try (PreparedStatement ps = Jdbc.prepare(connection, sql, cartId); ResultSet rs = ps.executeQuery()) {
            while (rs.next())
                items.add(new CartItem(ProductDAOImpl.map(rs), rs.getInt("quantity"), rs.getLong("cart_price")));
        }
        return new Cart(cartId, customerId, items);
    }

    @Override
    public void save(Cart cart) throws SQLException {
        Jdbc.update(connection, "DELETE FROM cart_item WHERE cart_id = ?", cart.getId());
        for (CartItem i : cart.getItems())
            Jdbc.update(connection, "INSERT INTO cart_item (cart_id, product_id, quantity, cart_price) VALUES (?, ?, ?, ?)",
                    cart.getId(), i.getProduct().getId(), i.getQuantity(), i.getCartPrice());
        Jdbc.update(connection, "UPDATE cart SET updated_at = ? WHERE cart_id = ?", Jdbc.ts(LocalDateTime.now()), cart.getId());
    }

    @Override
    public void clear(Cart cart) throws SQLException {
        Jdbc.update(connection, "DELETE FROM cart_item WHERE cart_id = ?", cart.getId());
        Jdbc.update(connection, "UPDATE cart SET updated_at = ? WHERE cart_id = ?", Jdbc.ts(LocalDateTime.now()), cart.getId());
    }
}
