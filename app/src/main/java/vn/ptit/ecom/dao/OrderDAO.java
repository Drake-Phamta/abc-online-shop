package vn.ptit.ecom.dao;

import java.sql.SQLException;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import vn.ptit.ecom.model.order.Order;
import vn.ptit.ecom.model.order.OrderStatus;

public interface OrderDAO {

    /** One row of an order list (UC09 history, UC14 board). */
    record OrderSummary(int id, String code, LocalDateTime orderDate, OrderStatus status, String paymentMethod,
                        long totalAmount, int itemCount, String firstItem, int customerId, String customerName) { }

    /** Stores a new order with its lines and first event; assigns the id. */
    void insert(Order order) throws SQLException;

    /** The order with lines, history, payments and shipment. */
    Optional<Order> findById(int orderId) throws SQLException;

    List<OrderSummary> findByCustomer(int customerId) throws SQLException;

    List<OrderSummary> findAll() throws SQLException;

    /** Stores the status and the events added since loading (payments and shipping have their own DAOs). */
    void saveProgress(Order order) throws SQLException;
}
