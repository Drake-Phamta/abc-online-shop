package vn.ptit.ecom.dao;

import java.sql.SQLException;
import java.util.List;
import vn.ptit.ecom.model.order.Payment;

public interface PaymentDAO {

    /** Inserts new payments (with their PayCash or PayCredit row) and stores status changes of existing ones. */
    void saveAll(int orderId, List<Payment> payments) throws SQLException;
}
