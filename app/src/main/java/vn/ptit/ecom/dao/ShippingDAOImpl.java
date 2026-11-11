package vn.ptit.ecom.dao;

import java.sql.Connection;
import java.sql.SQLException;
import vn.ptit.ecom.model.order.Shipping;

class ShippingDAOImpl implements ShippingDAO {
    private final Connection connection;

    ShippingDAOImpl(Connection connection) {
        this.connection = connection;
    }

    @Override
    public void save(int orderId, Shipping s) throws SQLException {
        if (s.getId() == null) {
            s.assignId(Jdbc.insert(connection, "INSERT INTO shipping (order_id, address_id, carrier, tracking_number, shipping_fee, "
                            + "status, shipped_date, delivered_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    orderId, s.getAddressId(), s.getCarrier(), s.getTrackingNumber(), s.getShippingFee(), s.getStatus().name(),
                    Jdbc.ts(s.getShippedDate()), Jdbc.ts(s.getDeliveredDate())));
        } else {
            Jdbc.update(connection, "UPDATE shipping SET status = ?, delivered_date = ? WHERE shipping_id = ?",
                    s.getStatus().name(), Jdbc.ts(s.getDeliveredDate()), s.getId());
        }
    }
}
