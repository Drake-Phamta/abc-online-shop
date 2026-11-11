package vn.ptit.ecom.service;

import java.sql.SQLException;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;
import vn.ptit.ecom.dao.Database;
import vn.ptit.ecom.dao.OrderDAO;
import vn.ptit.ecom.model.RuleViolation;
import vn.ptit.ecom.model.cart.Cart;
import vn.ptit.ecom.model.cart.CartIssue;
import vn.ptit.ecom.model.customer.Address;
import vn.ptit.ecom.model.customer.Customer;
import vn.ptit.ecom.model.order.Order;
import vn.ptit.ecom.model.order.OrderItem;
import vn.ptit.ecom.model.order.OrderStatus;
import vn.ptit.ecom.model.order.OrderStatus.Actor;
import vn.ptit.ecom.model.order.PaymentMethod;

/**
 * UC07 Place Order with UC21 Validate Cart, UC09 Track Order, UC14 Process Orders (status changes).
 * Every public method is one database transaction: either all of its writes are committed or none (rollback).
 */
@Service
public class OrderService {
    /** UC07 steps 1 to 4: the validated cart, the delivery addresses and the totals of BR04. */
    public record Checkout(Customer customer, Cart cart, List<CartIssue> issues, List<Address> addresses, Order.Totals totals) { }

    /** An order with what its page shows next to it. */
    public record OrderDetails(Order order, Address address, String customerName) { }

    private final Database db;

    public OrderService(Database db) {
        this.db = db;
    }

    /** UC07 steps 1 to 4 and UC21: changed prices are taken over (BR03) and saved, blocking issues are reported. */
    public Checkout checkout(int customerId) {
        return db.inTransaction(d -> {
            Customer customer = d.customers().findById(customerId).orElseThrow(() -> new NotFound("Customer not found."));
            Cart cart = d.carts().findOrCreate(customerId);
            List<CartIssue> issues = cart.validate();
            d.carts().save(cart);
            return new Checkout(customer, cart, issues, d.customers().addresses(customerId),
                    Order.Totals.of(cart.calcTotal(), customer.discountRate()));
        });
    }

    /**
     * UC07 steps 5 to 7: create the order from the cart (BR06 address, BR05 blocking issues, BR04 totals), refuse it when
     * the total differs from the one the customer confirmed (BR03), reserve the stock of every line (BR05), store the
     * order and empty the cart. A failure at any step rolls back all of them.
     */
    public Order placeOrder(int customerId, int addressId, PaymentMethod method, Long expectedTotal) {
        return db.inTransaction(d -> {
            Customer customer = d.customers().findById(customerId).orElseThrow(() -> new NotFound("Customer not found."));
            Address address = d.customers().address(addressId)
                    .orElseThrow(() -> new RuleViolation("BR06", "Choose one of your delivery addresses."));
            Cart cart = d.carts().findOrCreate(customerId);
            Order order = Order.place(customer, cart, address, method, LocalDateTime.now());
            if (expectedTotal != null && expectedTotal != order.getTotalAmount())
                throw new RuleViolation("BR03", "Prices changed since you opened checkout. Please check the new total.",
                        List.of(Map.of("expectedTotal", expectedTotal, "newTotal", order.getTotalAmount())));
            for (OrderItem i : order.getItems())
                if (!d.products().reserveStock(i.productId(), i.quantity()))
                    throw new RuleViolation("BR05", i.productName() + " has just sold out in this quantity.");
            d.orders().insert(order);
            d.carts().clear(cart);
            return order;
        });
    }

    /** UC09 step 2. */
    public List<OrderDAO.OrderSummary> ordersOf(int customerId) {
        return db.inTransaction(d -> d.orders().findByCustomer(customerId));
    }

    /** UC14 step 1. */
    public List<OrderDAO.OrderSummary> allOrders() {
        return db.inTransaction(d -> d.orders().findAll());
    }

    /** UC09 step 4 (customerId = the caller) and UC14 (customerId = null for sales staff). */
    public OrderDetails details(int orderId, Integer customerId) {
        return db.inTransaction(d -> details(d, load(d, orderId, customerId)));
    }

    /** BR09: the customer may cancel before packing starts, sales staff until shipping; the stock is released (BR05). */
    public OrderDetails cancel(int orderId, Integer customerId, Actor actor, String actorName) {
        return db.inTransaction(d -> {
            Order o = load(d, orderId, customerId);
            o.cancel(actor, actorName, LocalDateTime.now());
            for (OrderItem i : o.getItems()) d.products().releaseStock(i.productId(), i.quantity());
            d.payments().saveAll(o.getId(), o.getPayments());
            d.orders().saveProgress(o);
            return details(d, o);
        });
    }

    /** UC14: sales staff start packing (BR09). */
    public OrderDetails process(int orderId, String staffName) {
        return db.inTransaction(d -> {
            Order o = load(d, orderId, null);
            o.changeStatus(OrderStatus.PROCESSING, Actor.SALES, staffName, LocalDateTime.now(), "Packing started");
            d.orders().saveProgress(o);
            return details(d, o);
        });
    }

    /** Loads an order the caller may see; another customer's order is reported as missing (BR08). */
    static Order load(Database.Daos d, int orderId, Integer customerId) throws SQLException {
        Order o = d.orders().findById(orderId).orElseThrow(() -> new NotFound("Order not found."));
        if (customerId != null && o.getCustomerId() != customerId) throw new NotFound("Order not found.");
        return o;
    }

    static OrderDetails details(Database.Daos d, Order o) throws SQLException {
        Address a = d.customers().address(o.getAddressId()).orElse(null);
        String customer = d.customers().findById(o.getCustomerId()).map(c -> c.getFullName().display()).orElse("");
        return new OrderDetails(o, a, customer);
    }
}
