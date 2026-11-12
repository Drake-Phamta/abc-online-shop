package vn.ptit.ecom.model;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import org.junit.jupiter.api.Test;
import vn.ptit.ecom.model.cart.Cart;
import vn.ptit.ecom.model.cart.CartIssue;
import vn.ptit.ecom.model.cart.CartItem;
import vn.ptit.ecom.model.customer.Address;
import vn.ptit.ecom.model.customer.Customer;
import vn.ptit.ecom.model.customer.CustomerVIP;
import vn.ptit.ecom.model.customer.FullName;
import vn.ptit.ecom.model.order.Order;
import vn.ptit.ecom.model.order.OrderStatus;
import vn.ptit.ecom.model.order.OrderStatus.Actor;
import vn.ptit.ecom.model.order.PayCredit;
import vn.ptit.ecom.model.order.Payment;
import vn.ptit.ecom.model.order.PaymentMethod;
import vn.ptit.ecom.model.product.Category;
import vn.ptit.ecom.model.product.DetailKind;
import vn.ptit.ecom.model.product.Product;

/** Behaviour of the business rules of docs/SPEC.md on the model classes (no database). */
class OrderRulesTest {
    private static final LocalDateTime NOW = LocalDateTime.of(2026, 11, 11, 10, 0);
    private static final Category LAPTOPS = new Category(6, 5, "Laptops", "laptops", DetailKind.LAPTOP);
    private final Customer an = new CustomerVIP(1, new FullName("An", "Văn", "Nguyễn"), "an@example.com", null, 2,
            new BigDecimal("0.05"), 0);
    private final Customer lan = new Customer(2, new FullName("Lan", "Thị", "Trần"), "lan@example.com", null);
    private final Address anHome = new Address(1, 1, "Nguyễn Văn An", "0912", "12", "Trần Phú", "Hà Đông", "Hà Nội", true);

    private static Product product(long price, int stock) {
        return new Product(10, "EL-LAP-001", "ThinkPad", "Lenovo", price, stock, null, null, Product.Status.ACTIVE, LAPTOPS);
    }

    @Test
    void addingTheSameProductMergesLinesAndRespectsStock() {             // BR02, AT01
        Cart cart = new Cart(1, 1, List.of());
        cart.addItem(product(1_000_000, 2), 1);
        cart.addItem(product(1_000_000, 2), 1);
        assertEquals(1, cart.getItems().size());
        assertEquals(2, cart.getItems().get(0).getQuantity());
        RuleViolation v = assertThrows(RuleViolation.class, () -> cart.addItem(product(1_000_000, 2), 1));
        assertEquals("BR02", v.getRule());
    }

    @Test
    void hiddenProductsCannotBeAdded() {                                  // BR01
        Product hidden = new Product(11, "X", "Old", null, 100, 5, null, null, Product.Status.HIDDEN, LAPTOPS);
        assertEquals("BR01", assertThrows(RuleViolation.class, () -> new Cart(1, 1, List.of()).addItem(hidden, 1)).getRule());
    }

    @Test
    void validationTakesOverChangedPrices() {                             // BR03, AT02
        Cart cart = new Cart(1, 1, List.of(new CartItem(product(900_000, 5), 1, 1_000_000)));
        List<CartIssue> issues = cart.validate();
        assertEquals(1, issues.size());
        assertEquals(CartIssue.Kind.PRICE_CHANGED, issues.get(0).kind());
        assertFalse(issues.get(0).kind().isBlocking());
        assertEquals(900_000, cart.getItems().get(0).getCartPrice());
    }

    @Test
    void totalsApplyVipDiscountAndFreeDelivery() {                       // BR04, AT03
        Order.Totals t = Order.Totals.of(1_000_000, new BigDecimal("0.05"));
        assertEquals(50_000, t.discount());
        assertEquals(0, t.shippingFee());
        assertEquals(950_000, t.total());
        Order.Totals small = Order.Totals.of(200_000, BigDecimal.ZERO);
        assertEquals(30_000, small.shippingFee());
        assertEquals(230_000, small.total());
    }

    @Test
    void placingNeedsAnOwnAddressAndEnoughStock() {                       // BR06, BR05
        Cart cart = new Cart(1, 1, List.of(new CartItem(product(1_000_000, 1), 1, 1_000_000)));
        assertEquals("BR06", assertThrows(RuleViolation.class,
                () -> Order.place(lan, cart, anHome, PaymentMethod.COD, NOW)).getRule());
        Cart tooMany = new Cart(1, 1, List.of(new CartItem(product(1_000_000, 1), 3, 1_000_000)));
        assertEquals("BR05", assertThrows(RuleViolation.class,
                () -> Order.place(an, tooMany, anHome, PaymentMethod.COD, NOW)).getRule());
    }

    @Test
    void cardOrderBecomesPaidOnlyAfterApproval() {                         // BR07, AT05
        Cart cart = new Cart(1, 1, List.of(new CartItem(product(1_000_000, 5), 1, 1_000_000)));
        Order o = Order.place(an, cart, anHome, PaymentMethod.CARD, NOW);
        assertEquals(OrderStatus.PENDING_PAYMENT, o.getStatus());
        o.recordCardPayment(new PayCredit(null, o.getTotalAmount(), Payment.Status.DECLINED, NOW, "AN", "0002", "08/28", null), NOW);
        assertEquals(OrderStatus.PENDING_PAYMENT, o.getStatus());
        o.recordCardPayment(new PayCredit(null, o.getTotalAmount(), Payment.Status.APPROVED, NOW, "AN", "4242", "08/28", "tok"), NOW);
        assertEquals(OrderStatus.PAID, o.getStatus());
        assertEquals(2, o.getPayments().size());
    }

    @Test
    void lifecycleFollowsTheTransitionTable() {                            // BR09, BR10, BR11, AT07, AT08
        Cart cart = new Cart(1, 1, List.of(new CartItem(product(1_000_000, 5), 1, 1_000_000)));
        Order o = Order.place(an, cart, anHome, PaymentMethod.COD, NOW);
        assertEquals("BR09", assertThrows(RuleViolation.class, () -> o.ship("GHN", "T1", "staff", NOW)).getRule());
        o.changeStatus(OrderStatus.PROCESSING, Actor.SALES, "staff", NOW, null);
        o.ship("GHN", "T1", "staff", NOW);
        o.deliver("staff", NOW);
        assertEquals(OrderStatus.DELIVERED, o.getStatus());
        assertTrue(o.getPayments().get(0).isSuccessful());
        assertEquals("CASH", o.getPayments().get(0).method());
        assertEquals(4, o.getEvents().size());                            // placed, processing, shipped, delivered
    }

    @Test
    void customersCannotCancelOncePackingStarted() {                      // BR09
        assertTrue(OrderStatus.PLACED.canMoveTo(OrderStatus.CANCELLED, Actor.CUSTOMER));
        assertFalse(OrderStatus.PROCESSING.canMoveTo(OrderStatus.CANCELLED, Actor.CUSTOMER));
        assertTrue(OrderStatus.PROCESSING.canMoveTo(OrderStatus.CANCELLED, Actor.SALES));
        assertFalse(OrderStatus.PENDING_PAYMENT.canMoveTo(OrderStatus.PAID, Actor.CUSTOMER));
    }

    @Test
    void cancellingAPaidOrderRefundsTheCard() {                           // AT09
        Cart cart = new Cart(1, 1, List.of(new CartItem(product(1_000_000, 5), 1, 1_000_000)));
        Order o = Order.place(an, cart, anHome, PaymentMethod.CARD, NOW);
        o.recordCardPayment(new PayCredit(null, o.getTotalAmount(), Payment.Status.APPROVED, NOW, "AN", "4242", "08/28", "tok"), NOW);
        o.cancel(Actor.SALES, "staff", NOW);
        assertEquals(OrderStatus.CANCELLED, o.getStatus());
        assertEquals(Payment.Status.REFUNDED, o.getPayments().get(0).getStatus());
    }
}
