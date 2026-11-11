package vn.ptit.ecom.controller;

import jakarta.servlet.http.HttpSession;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import vn.ptit.ecom.dao.OrderDAO;
import vn.ptit.ecom.model.customer.Role;
import vn.ptit.ecom.model.order.Order;
import vn.ptit.ecom.model.order.OrderStatus.Actor;
import vn.ptit.ecom.model.order.PaymentMethod;
import vn.ptit.ecom.service.OrderService;

/** UC07 Place Order (with UC21 Validate Cart), UC09 Track Order, UC14 Process Orders (status part). */
@RestController
public class OrderController {
    record PlaceOrder(Integer addressId, String paymentMethod, Long expectedTotal) { }

    private final OrderService orders;

    public OrderController(OrderService orders) {
        this.orders = orders;
    }

    /** UC07 steps 1 to 4: the validated cart (UC21), the customer's addresses and the totals of BR04. */
    @GetMapping("/api/checkout")
    public Map<String, Object> checkout(HttpSession session) {
        CurrentUser u = CurrentUser.require(session, Role.CUSTOMER);
        OrderService.Checkout c = orders.checkout(u.id());
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("cart", Views.CartView.of(c.cart()));
        out.put("issues", c.issues().stream().map(Views.Issue::of).toList());
        out.put("addresses", c.addresses().stream().map(Views.AddressView::of).toList());
        out.put("customerKind", c.customer().kindLabel());
        out.put("discountRate", c.customer().discountRate());
        out.put("totals", c.totals());
        return out;
    }

    /** UC07 steps 5 to 7. The request is checked here; the rules and the transaction are OrderService's. */
    @PostMapping("/api/orders")
    public Map<String, Object> placeOrder(@RequestBody PlaceOrder req, HttpSession session) {
        CurrentUser u = CurrentUser.require(session, Role.CUSTOMER);
        if (req.addressId() == null) throw new IllegalArgumentException("Choose a delivery address.");
        Order order = orders.placeOrder(u.id(), req.addressId(), parseMethod(req.paymentMethod()), req.expectedTotal());
        return Map.of("orderId", order.getId(), "code", order.code(), "status", order.getStatus(), "total", order.getTotalAmount());
    }

    /** UC09 step 2. */
    @GetMapping("/api/orders")
    public List<OrderDAO.OrderSummary> myOrders(HttpSession session) {
        CurrentUser u = CurrentUser.require(session, Role.CUSTOMER);
        return orders.ordersOf(u.id());
    }

    /** UC09 step 4 for the customer (own orders only, BR08) and UC14 for sales staff. */
    @GetMapping("/api/orders/{id}")
    public Views.OrderView order(@PathVariable int id, HttpSession session) {
        CurrentUser u = CurrentUser.require(session, Role.CUSTOMER, Role.SALES);
        return view(orders.details(id, ownerFilter(u)), u);
    }

    /** Customer cancels an order that is not yet being processed (BR09). */
    @PostMapping("/api/orders/{id}/cancel")
    public Views.OrderView cancelByCustomer(@PathVariable int id, HttpSession session) {
        CurrentUser u = CurrentUser.require(session, Role.CUSTOMER);
        return view(orders.cancel(id, u.id(), Actor.CUSTOMER, u.name()), u);
    }

    /** UC14 step 1: the board of all orders. */
    @GetMapping("/api/staff/orders")
    public List<Views.BoardCard> board(HttpSession session) {
        CurrentUser.require(session, Role.SALES);
        return orders.allOrders().stream().map(Views.BoardCard::of).toList();
    }

    @PostMapping("/api/staff/orders/{id}/process")
    public Views.OrderView process(@PathVariable int id, HttpSession session) {
        CurrentUser u = CurrentUser.require(session, Role.SALES);
        return view(orders.process(id, u.name()), u);
    }

    @PostMapping("/api/staff/orders/{id}/cancel")
    public Views.OrderView cancelByStaff(@PathVariable int id, HttpSession session) {
        CurrentUser u = CurrentUser.require(session, Role.SALES);
        return view(orders.cancel(id, null, Actor.SALES, u.name()), u);
    }

    /** Customers see only their own orders (BR08); staff see all. */
    static Integer ownerFilter(CurrentUser u) {
        return u.role() == Role.CUSTOMER ? u.id() : null;
    }

    /** The order page, with the actions the caller may take next (BR09). */
    static Views.OrderView view(OrderService.OrderDetails d, CurrentUser u) {
        return Views.OrderView.of(d.order(), d.address(), d.customerName(),
                d.order().getStatus().next(u.role() == Role.SALES ? Actor.SALES : Actor.CUSTOMER));
    }

    private static PaymentMethod parseMethod(String s) {
        try {
            return PaymentMethod.valueOf(s == null ? "" : s.trim().toUpperCase());
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("Choose card or cash on delivery.");
        }
    }
}
