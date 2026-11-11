package vn.ptit.ecom.service;

import org.springframework.stereotype.Service;
import vn.ptit.ecom.dao.Database;
import vn.ptit.ecom.model.cart.Cart;
import vn.ptit.ecom.model.product.Product;

/** UC06 Manage Shopping Cart. Each operation loads the customer's cart, changes it through the model and saves it. */
@Service
public class CartService {
    private final Database db;

    public CartService(Database db) {
        this.db = db;
    }

    public Cart cart(int customerId) {
        return db.inTransaction(d -> d.carts().findOrCreate(customerId));
    }

    /** UC06 steps 1 and 2: BR01 and BR02 are checked by Cart.addItem. */
    public Cart addItem(int customerId, int productId, int quantity) {
        return db.inTransaction(d -> {
            Product p = d.products().findById(productId).orElseThrow(() -> new NotFound("This product does not exist."));
            Cart cart = d.carts().findOrCreate(customerId);
            cart.addItem(p, quantity);
            d.carts().save(cart);
            return cart;
        });
    }

    /** UC06 step 3. */
    public Cart changeQuantity(int customerId, int productId, int quantity) {
        return db.inTransaction(d -> {
            Cart cart = d.carts().findOrCreate(customerId);
            cart.setQuantity(productId, quantity);
            d.carts().save(cart);
            return cart;
        });
    }

    public Cart removeItem(int customerId, int productId) {
        return db.inTransaction(d -> {
            Cart cart = d.carts().findOrCreate(customerId);
            cart.removeItem(productId);
            d.carts().save(cart);
            return cart;
        });
    }
}
