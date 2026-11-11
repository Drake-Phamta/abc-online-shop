package vn.ptit.ecom.model.cart;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import vn.ptit.ecom.model.RuleViolation;
import vn.ptit.ecom.model.product.Product;

/** A customer's cart; its products are the current product rows, its prices the ones shown when added. */
public class Cart {
    private final int id;
    private final int customerId;
    private final List<CartItem> items;

    public Cart(int id, int customerId, List<CartItem> items) {
        this.id = id;
        this.customerId = customerId;
        this.items = new ArrayList<>(items);
    }

    /** UC06: BR01 active product, BR02 one line per product and quantity within stock. */
    public CartItem addItem(Product product, int quantity) {
        if (quantity < 1) throw new RuleViolation("BR02", "Quantity must be at least 1.");
        if (product.getStatus() != Product.Status.ACTIVE)
            throw new RuleViolation("BR01", product.getName() + " is not for sale.");
        Optional<CartItem> line = find(product.getId());
        int wanted = quantity + line.map(CartItem::getQuantity).orElse(0);
        if (wanted > product.getStockQuantity())
            throw new RuleViolation("BR02", "Only " + product.getStockQuantity() + " of " + product.getName() + " in stock.");
        if (line.isPresent()) {
            line.get().setQuantity(wanted);
            return line.get();
        }
        CartItem item = new CartItem(product, quantity, product.getPrice());
        items.add(item);
        return item;
    }

    /** UC06 step 3. */
    public void setQuantity(int productId, int quantity) {
        CartItem line = find(productId).orElseThrow(() -> new RuleViolation("BR02", "This product is not in the cart."));
        if (quantity < 1) throw new RuleViolation("BR02", "Quantity must be at least 1; remove the line instead.");
        if (quantity > line.getProduct().getStockQuantity())
            throw new RuleViolation("BR02", "Only " + line.getProduct().getStockQuantity() + " in stock.");
        line.setQuantity(quantity);
    }

    public void removeItem(int productId) {
        items.removeIf(i -> i.getProduct().getId() == productId);
    }

    /**
     * UC21 Validate Cart (BR03): compares every line with the current product. Changed prices are taken over and
     * reported; unavailable products and missing stock are reported as blocking.
     */
    public List<CartIssue> validate() {
        List<CartIssue> issues = new ArrayList<>();
        for (CartItem i : items) {
            Product p = i.getProduct();
            if (!p.isAvailable(i.getQuantity())) {   // the product answers; the cart only names the reason for the customer
                if (p.getStatus() != Product.Status.ACTIVE)
                    issues.add(new CartIssue(p.getId(), p.getName(), CartIssue.Kind.UNAVAILABLE, i.getCartPrice(), p.getPrice(), 0));
                else
                    issues.add(new CartIssue(p.getId(), p.getName(), CartIssue.Kind.NOT_ENOUGH_STOCK, i.getCartPrice(),
                            p.getPrice(), p.getStockQuantity()));
            }
            if (i.getCartPrice() != p.getPrice()) {
                issues.add(new CartIssue(p.getId(), p.getName(), CartIssue.Kind.PRICE_CHANGED, i.getCartPrice(), p.getPrice(),
                        p.getStockQuantity()));
                i.setCartPrice(p.getPrice());
            }
        }
        return issues;
    }

    public long calcTotal() {
        return items.stream().mapToLong(CartItem::subTotal).sum();
    }

    public boolean isEmpty() { return items.isEmpty(); }

    private Optional<CartItem> find(int productId) {
        return items.stream().filter(i -> i.getProduct().getId() == productId).findFirst();
    }

    public int getId() { return id; }
    public int getCustomerId() { return customerId; }
    public List<CartItem> getItems() { return Collections.unmodifiableList(items); }
}
