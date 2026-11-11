package vn.ptit.ecom.controller;

import jakarta.servlet.http.HttpSession;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import vn.ptit.ecom.model.customer.Role;
import vn.ptit.ecom.service.ShippingService;

/** UC14 shipping steps with the data exchanged with the Shipping Provider (UC16): ship and deliver. */
@RestController
public class ShippingController {
    record ShipRequest(String carrier, String trackingNumber) { }

    private final ShippingService shipping;

    public ShippingController(ShippingService shipping) {
        this.shipping = shipping;
    }

    @PostMapping("/api/staff/orders/{id}/ship")
    public Views.OrderView ship(@PathVariable int id, @RequestBody ShipRequest req, HttpSession session) {
        CurrentUser u = CurrentUser.require(session, Role.SALES);
        return OrderController.view(shipping.ship(id, trim(req.carrier()), trim(req.trackingNumber()), u.name()), u);
    }

    @PostMapping("/api/staff/orders/{id}/deliver")
    public Views.OrderView deliver(@PathVariable int id, HttpSession session) {
        CurrentUser u = CurrentUser.require(session, Role.SALES);
        return OrderController.view(shipping.deliver(id, u.name()), u);
    }

    private static String trim(String s) {
        return s == null ? null : s.trim();
    }
}
