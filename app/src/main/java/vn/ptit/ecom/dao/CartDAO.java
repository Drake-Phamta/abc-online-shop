package vn.ptit.ecom.dao;

import java.sql.SQLException;
import vn.ptit.ecom.model.cart.Cart;

public interface CartDAO {

    /** The customer's cart with its lines and their current products; created empty on first use. */
    Cart findOrCreate(int customerId) throws SQLException;

    /** Stores the lines of the cart as they are now (quantities and cart prices). */
    void save(Cart cart) throws SQLException;

    /** UC07 step 6: the cart is emptied when the order is created. */
    void clear(Cart cart) throws SQLException;
}
