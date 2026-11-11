package vn.ptit.ecom.model.cart;

import vn.ptit.ecom.model.product.Product;

/** One line of a cart; cartPrice is the price shown when the line was added (BR03). */
public class CartItem {
    private final Product product;
    private int quantity;
    private long cartPrice;

    public CartItem(Product product, int quantity, long cartPrice) {
        this.product = product;
        this.quantity = quantity;
        this.cartPrice = cartPrice;
    }

    public long subTotal() { return cartPrice * quantity; }

    void setQuantity(int quantity) { this.quantity = quantity; }
    void setCartPrice(long cartPrice) { this.cartPrice = cartPrice; }

    public Product getProduct() { return product; }
    public int getQuantity() { return quantity; }
    public long getCartPrice() { return cartPrice; }
}
