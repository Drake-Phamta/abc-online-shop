package vn.ptit.ecom.dao;

import java.sql.SQLException;
import vn.ptit.ecom.model.order.Shipping;

public interface ShippingDAO {

    /** Inserts the shipment when the order is shipped, or stores its delivery. */
    void save(int orderId, Shipping shipping) throws SQLException;
}
