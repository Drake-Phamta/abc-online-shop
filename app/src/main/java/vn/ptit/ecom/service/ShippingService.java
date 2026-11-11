package vn.ptit.ecom.service;

import java.time.LocalDateTime;
import org.springframework.stereotype.Service;
import vn.ptit.ecom.dao.Database;
import vn.ptit.ecom.model.order.Order;

/** UC14 shipping steps with the data exchanged with the Shipping Provider (UC16): ship and deliver. */
@Service
public class ShippingService {
    private final Database db;

    public ShippingService(Database db) {
        this.db = db;
    }

    /** BR10: one shipment per order, created when a PROCESSING order is handed to the carrier. */
    public OrderService.OrderDetails ship(int orderId, String carrier, String trackingNumber, String staffName) {
        return db.inTransaction(d -> {
            Order o = OrderService.load(d, orderId, null);
            o.ship(carrier, trackingNumber, staffName, LocalDateTime.now());
            d.shipping().save(o.getId(), o.getShipping());
            d.orders().saveProgress(o);
            return OrderService.details(d, o);
        });
    }

    /** BR11: delivering a cash-on-delivery order records its cash payment. */
    public OrderService.OrderDetails deliver(int orderId, String staffName) {
        return db.inTransaction(d -> {
            Order o = OrderService.load(d, orderId, null);
            o.deliver(staffName, LocalDateTime.now());
            d.shipping().save(o.getId(), o.getShipping());
            d.payments().saveAll(o.getId(), o.getPayments());
            d.orders().saveProgress(o);
            return OrderService.details(d, o);
        });
    }
}
