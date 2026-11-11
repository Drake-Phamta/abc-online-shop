package vn.ptit.ecom.dao;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.List;
import vn.ptit.ecom.model.order.PayCash;
import vn.ptit.ecom.model.order.PayCredit;
import vn.ptit.ecom.model.order.Payment;

class PaymentDAOImpl implements PaymentDAO {
    private final Connection connection;

    PaymentDAOImpl(Connection connection) {
        this.connection = connection;
    }

    @Override
    public void saveAll(int orderId, List<Payment> payments) throws SQLException {
        for (Payment p : payments) {
            if (p.getId() != null) {
                Jdbc.update(connection, "UPDATE payment SET status = ? WHERE payment_id = ?", p.getStatus().name(), p.getId());
                continue;
            }
            int id = Jdbc.insert(connection, "INSERT INTO payment (order_id, method, amount, status, payment_date) VALUES (?, ?, ?, ?, ?)",
                    orderId, p.method(), p.getAmount(), p.getStatus().name(), Jdbc.ts(p.getPaymentDate()));
            p.assignId(id);
            if (p instanceof PayCredit c)
                Jdbc.update(connection, "INSERT INTO pay_credit (payment_id, card_holder, card_last4, expiry, provider_token) "
                        + "VALUES (?, ?, ?, ?, ?)", id, c.getCardHolder(), c.getCardLast4(), c.getExpiry(), c.getProviderToken());
            else if (p instanceof PayCash c)
                Jdbc.update(connection, "INSERT INTO pay_cash (payment_id, cash_received, change_amount) VALUES (?, ?, ?)",
                        id, c.getCashReceived(), c.getChangeAmount());
        }
    }
}
