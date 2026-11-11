package vn.ptit.ecom.service;

import java.time.LocalDateTime;
import org.springframework.stereotype.Service;
import vn.ptit.ecom.dao.Database;
import vn.ptit.ecom.integration.CardData;
import vn.ptit.ecom.integration.CardProvider;
import vn.ptit.ecom.model.RuleViolation;
import vn.ptit.ecom.model.order.Order;
import vn.ptit.ecom.model.order.OrderStatus;
import vn.ptit.ecom.model.order.PayCredit;
import vn.ptit.ecom.model.order.Payment;

/**
 * UC08 Make Payment. Two short transactions with the provider call between them: no database lock is held while the
 * provider answers, and the result is recorded against the order only after it has come back (BR07).
 */
@Service
public class PaymentService {
    public record PaymentResult(boolean approved, Order order, String reason) { }

    private final Database db;
    private final CardProvider provider;

    public PaymentService(Database db, CardProvider provider) {
        this.db = db;
        this.provider = provider;
    }

    public PaymentResult pay(int orderId, int customerId, CardData card) {
        Order before = db.inTransaction(d -> OrderService.load(d, orderId, customerId));
        if (before.getStatus() != OrderStatus.PENDING_PAYMENT)
            throw new RuleViolation("BR07", "Order " + before.code() + " is not waiting for a card payment.");

        CardProvider.Result result = provider.charge(before.code(), before.getTotalAmount(), card);

        return db.inTransaction(d -> {
            Order o = OrderService.load(d, orderId, customerId);
            LocalDateTime now = LocalDateTime.now();
            PayCredit payment = new PayCredit(null, o.getTotalAmount(), result.approved() ? Payment.Status.APPROVED
                    : Payment.Status.DECLINED, now, card.holder(), card.last4(), card.expiry(), result.token());
            o.recordCardPayment(payment, now);
            d.payments().saveAll(o.getId(), o.getPayments());
            d.orders().saveProgress(o);
            return new PaymentResult(result.approved(), o, result.reason());
        });
    }
}
