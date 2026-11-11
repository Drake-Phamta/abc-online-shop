package vn.ptit.ecom.model.order;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import vn.ptit.ecom.model.RuleViolation;
import vn.ptit.ecom.model.cart.Cart;
import vn.ptit.ecom.model.cart.CartIssue;
import vn.ptit.ecom.model.cart.CartItem;
import vn.ptit.ecom.model.customer.Address;
import vn.ptit.ecom.model.customer.Customer;
import vn.ptit.ecom.model.order.OrderStatus.Actor;

public class Order {
    public static final long SHIPPING_FEE = 30_000;
    public static final long FREE_SHIPPING_FROM = 500_000;

    private Integer id;
    private final int customerId;
    private final int addressId;
    private final LocalDateTime orderDate;
    private OrderStatus status;
    private final PaymentMethod paymentMethod;
    private final long subtotal;
    private final long discount;
    private final long shippingFee;
    private final long totalAmount;
    private final List<OrderItem> items;
    private final List<OrderEvent> events;
    private final List<Payment> payments;
    private Shipping shipping;

    public Order(Integer id, int customerId, int addressId, LocalDateTime orderDate, OrderStatus status,
                 PaymentMethod paymentMethod, long subtotal, long discount, long shippingFee, long totalAmount,
                 List<OrderItem> items, List<OrderEvent> events, List<Payment> payments, Shipping shipping) {
        this.id = id;
        this.customerId = customerId;
        this.addressId = addressId;
        this.orderDate = orderDate;
        this.status = status;
        this.paymentMethod = paymentMethod;
        this.subtotal = subtotal;
        this.discount = discount;
        this.shippingFee = shippingFee;
        this.totalAmount = totalAmount;
        this.items = new ArrayList<>(items);
        this.events = new ArrayList<>(events);
        this.payments = new ArrayList<>(payments);
        this.shipping = shipping;
    }

    /** The amounts of BR04 for a subtotal and a discount rate. */
    public record Totals(long subtotal, long discount, long shippingFee, long total) {
        public static Totals of(long subtotal, BigDecimal discountRate) {
            long discount = BigDecimal.valueOf(subtotal).multiply(discountRate).setScale(0, RoundingMode.HALF_UP).longValue();
            long afterDiscount = subtotal - discount;
            long fee = afterDiscount >= FREE_SHIPPING_FROM ? 0 : SHIPPING_FEE;
            return new Totals(subtotal, discount, fee, afterDiscount + fee);
        }
    }

    /**
     * UC07 step 6: builds the order from a validated cart. Blocking cart issues (UC07 A1) and a foreign address
     * (BR06) are refused. The caller reserves the stock (BR05) and stores the order in the same transaction.
     */
    public static Order place(Customer customer, Cart cart, Address address, PaymentMethod method, LocalDateTime now) {
        if (address.customerId() != customer.getId())
            throw new RuleViolation("BR06", "The delivery address does not belong to this customer.");
        if (cart.isEmpty()) throw new RuleViolation("BR02", "The cart is empty.");
        List<CartIssue> blocking = cart.validate().stream().filter(i -> i.kind().isBlocking()).toList();
        if (!blocking.isEmpty())
            throw new RuleViolation("BR05", "Some products cannot be ordered in this quantity.", blocking);
        List<OrderItem> lines = new ArrayList<>();
        for (CartItem i : cart.getItems())
            lines.add(new OrderItem(null, i.getProduct().getId(), i.getProduct().getName(), i.getQuantity(), i.getCartPrice()));
        Totals t = Totals.of(cart.calcTotal(), customer.discountRate());
        OrderStatus first = method == PaymentMethod.CARD ? OrderStatus.PENDING_PAYMENT : OrderStatus.PLACED;
        String note = method == PaymentMethod.CARD ? "Order placed, waiting for card payment" : "Order placed, cash on delivery";
        OrderEvent placed = new OrderEvent(null, first, now, customer.getFullName().display(), note);
        return new Order(null, customer.getId(), address.id(), now, first, method, t.subtotal(), t.discount(),
                t.shippingFee(), t.total(), lines, List.of(placed), List.of(), null);
    }

    /** BR09: the only way the status changes. */
    public void changeStatus(OrderStatus to, Actor actor, String actorName, LocalDateTime now, String note) {
        if (!status.canMoveTo(to, actor))
            throw new RuleViolation("BR09", "Order " + code() + " cannot go from " + status + " to " + to + ".");
        status = to;
        events.add(new OrderEvent(null, to, now, actorName, note));
    }

    /** UC08: records a provider result; only an approved card payment makes the order PAID (BR07). */
    public void recordCardPayment(PayCredit payment, LocalDateTime now) {
        if (paymentMethod != PaymentMethod.CARD || status != OrderStatus.PENDING_PAYMENT)
            throw new RuleViolation("BR07", "Order " + code() + " is not waiting for a card payment.");
        if (payment.getAmount() != totalAmount)
            throw new RuleViolation("BR07", "The payment amount does not match the order total.");
        payments.add(payment);
        String card = "card ending " + payment.getCardLast4();
        if (payment.getStatus() == Payment.Status.APPROVED)
            changeStatus(OrderStatus.PAID, Actor.PROVIDER, "Payment provider", now, "Paid by " + card);
        else
            events.add(new OrderEvent(null, status, now, "Payment provider", "Payment declined, " + card));
    }

    /** Cancels the order; the caller releases the reserved stock of the lines (BR05). */
    public void cancel(Actor actor, String actorName, LocalDateTime now) {
        changeStatus(OrderStatus.CANCELLED, actor, actorName, now, "Order cancelled");
        payments.forEach(Payment::refund);
    }

    /** UC14 with the shipping data of UC16 (BR10). */
    public Shipping ship(String carrier, String trackingNumber, String staffName, LocalDateTime now) {
        if (carrier == null || carrier.isBlank() || trackingNumber == null || trackingNumber.isBlank())
            throw new RuleViolation("BR10", "Carrier and tracking number are required to ship an order.");
        changeStatus(OrderStatus.SHIPPED, Actor.SALES, staffName, now, "Handed to " + carrier + ", tracking " + trackingNumber);
        shipping = new Shipping(null, addressId, carrier, trackingNumber, shippingFee, Shipping.Status.IN_TRANSIT, now, null);
        return shipping;
    }

    /** Delivery confirmed; cash on delivery is collected now (BR11). */
    public void deliver(String staffName, LocalDateTime now) {
        changeStatus(OrderStatus.DELIVERED, Actor.SALES, staffName, now, "Delivered to the customer");
        shipping.markDelivered(now);
        if (paymentMethod == PaymentMethod.COD)
            payments.add(new PayCash(null, totalAmount, Payment.Status.COMPLETED, now, totalAmount, 0));
    }

    public String code() { return id == null ? "(new)" : String.format("ORD-%06d", id); }

    public void assignId(int id) { this.id = id; }
    public Integer getId() { return id; }
    public int getCustomerId() { return customerId; }
    public int getAddressId() { return addressId; }
    public LocalDateTime getOrderDate() { return orderDate; }
    public OrderStatus getStatus() { return status; }
    public PaymentMethod getPaymentMethod() { return paymentMethod; }
    public long getSubtotal() { return subtotal; }
    public long getDiscount() { return discount; }
    public long getShippingFee() { return shippingFee; }
    public long getTotalAmount() { return totalAmount; }
    public List<OrderItem> getItems() { return Collections.unmodifiableList(items); }
    public List<OrderEvent> getEvents() { return Collections.unmodifiableList(events); }
    public List<Payment> getPayments() { return Collections.unmodifiableList(payments); }
    public Shipping getShipping() { return shipping; }
}
