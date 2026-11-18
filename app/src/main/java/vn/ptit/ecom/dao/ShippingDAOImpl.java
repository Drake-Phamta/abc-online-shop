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
            s.assignId(Jdbc.insert(connection, "INSERT INTO Shipping (OrderId, AddressId, Carrier, TrackingNumber, ShippingFee, "
                            + "Status, ShippedDate, DeliveredDate) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    orderId, s.getAddressId(), s.getCarrier(), s.getTrackingNumber(), s.getShippingFee(), s.getStatus().name(),
                    Jdbc.ts(s.getShippedDate()), Jdbc.ts(s.getDeliveredDate())));
        } else {
            Jdbc.update(connection, "UPDATE Shipping SET Status = ?, DeliveredDate = ? WHERE ShippingId = ?",
                    s.getStatus().name(), Jdbc.ts(s.getDeliveredDate()), s.getId());
        }
    }
}
