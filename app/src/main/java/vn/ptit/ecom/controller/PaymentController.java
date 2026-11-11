package vn.ptit.ecom.controller;

import jakarta.servlet.http.HttpSession;
import java.util.Map;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import vn.ptit.ecom.integration.CardData;
import vn.ptit.ecom.model.customer.Role;
import vn.ptit.ecom.service.PaymentService;

/** UC08 Make Payment. The card data is checked here (format, Luhn, expiry: UC08 A2); the payment itself is PaymentService's. */
@RestController
public class PaymentController {
    record CardPayment(String cardHolder, String cardNumber, String expiry, String cvv) { }

    private final PaymentService payments;

    public PaymentController(PaymentService payments) {
        this.payments = payments;
    }

    @PostMapping("/api/orders/{id}/payments")
    public Map<String, Object> pay(@PathVariable int id, @RequestBody CardPayment req, HttpSession session) {
        CurrentUser u = CurrentUser.require(session, Role.CUSTOMER);
        CardData card = new CardData(req.cardHolder(), req.cardNumber(), req.expiry(), req.cvv());
        PaymentService.PaymentResult r = payments.pay(id, u.id(), card);
        return Map.of("approved", r.approved(), "status", r.order().getStatus(),
                "message", r.approved() ? "Payment approved." : r.reason() + ". Your order is kept; try another card.");
    }
}
