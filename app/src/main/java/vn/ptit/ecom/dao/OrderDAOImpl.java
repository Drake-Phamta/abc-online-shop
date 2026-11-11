package vn.ptit.ecom.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import vn.ptit.ecom.model.order.Order;
import vn.ptit.ecom.model.order.OrderEvent;
import vn.ptit.ecom.model.order.OrderItem;
import vn.ptit.ecom.model.order.OrderStatus;
import vn.ptit.ecom.model.order.PayCash;
import vn.ptit.ecom.model.order.PayCredit;
import vn.ptit.ecom.model.order.Payment;
import vn.ptit.ecom.model.order.PaymentMethod;
import vn.ptit.ecom.model.order.Shipping;

class OrderDAOImpl implements OrderDAO {
    private final Connection connection;

    OrderDAOImpl(Connection connection) {
        this.connection = connection;
    }

    @Override
    public void insert(Order o) throws SQLException {
        int id = Jdbc.insert(connection, "INSERT INTO customer_order (customer_id, address_id, order_date, status, payment_method, "
                        + "subtotal, discount, shipping_fee, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                o.getCustomerId(), o.getAddressId(), Jdbc.ts(o.getOrderDate()), o.getStatus().name(),
                o.getPaymentMethod().name(), o.getSubtotal(), o.getDiscount(), o.getShippingFee(), o.getTotalAmount());
        o.assignId(id);
        for (OrderItem i : o.getItems())
            Jdbc.update(connection, "INSERT INTO order_item (order_id, product_id, product_name, quantity, unit_price) "
                    + "VALUES (?, ?, ?, ?, ?)", id, i.productId(), i.productName(), i.quantity(), i.unitPrice());
        insertNewEvents(o);
    }

    @Override
    public Optional<Order> findById(int orderId) throws SQLException {
        try (PreparedStatement ps = Jdbc.prepare(connection, "SELECT * FROM customer_order WHERE order_id = ?", orderId);
             ResultSet rs = ps.executeQuery()) {
            if (!rs.next()) return Optional.empty();
            return Optional.of(new Order(rs.getInt("order_id"), rs.getInt("customer_id"), rs.getInt("address_id"),
                    Jdbc.ts(rs.getString("order_date")), OrderStatus.valueOf(rs.getString("status")),
                    PaymentMethod.valueOf(rs.getString("payment_method")), rs.getLong("subtotal"), rs.getLong("discount"),
                    rs.getLong("shipping_fee"), rs.getLong("total_amount"), items(orderId), events(orderId),
                    payments(orderId), shipping(orderId)));
        }
    }

    @Override
    public List<OrderSummary> findByCustomer(int customerId) throws SQLException {
        return summaries("WHERE o.customer_id = ?", customerId);
    }

    @Override
    public List<OrderSummary> findAll() throws SQLException {
        return summaries("");
    }

    @Override
    public void saveProgress(Order o) throws SQLException {
        Jdbc.update(connection, "UPDATE customer_order SET status = ? WHERE order_id = ?", o.getStatus().name(), o.getId());
        insertNewEvents(o);
    }

    private void insertNewEvents(Order o) throws SQLException {
        for (OrderEvent e : o.getEvents())
            if (e.id() == null)
                Jdbc.update(connection, "INSERT INTO order_event (order_id, status, occurred_at, actor, note) VALUES (?, ?, ?, ?, ?)",
                        o.getId(), e.status().name(), Jdbc.ts(e.occurredAt()), e.actor(), e.note());
    }

    private List<OrderSummary> summaries(String where, Object... args) throws SQLException {
        String sql = "SELECT o.*, c.first_name, c.middle_name, c.last_name, "
                + "(SELECT sum(quantity) FROM order_item i WHERE i.order_id = o.order_id) AS item_count, "
                + "(SELECT product_name FROM order_item i WHERE i.order_id = o.order_id ORDER BY order_item_id LIMIT 1) AS first_item "
                + "FROM customer_order o JOIN customer c ON c.customer_id = o.customer_id " + where
                + " ORDER BY o.order_date DESC, o.order_id DESC";
        List<OrderSummary> out = new ArrayList<>();
        try (PreparedStatement ps = Jdbc.prepare(connection, sql, args); ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                String middle = rs.getString("middle_name");
                String name = rs.getString("last_name") + (middle == null ? "" : " " + middle) + " " + rs.getString("first_name");
                int id = rs.getInt("order_id");
                out.add(new OrderSummary(id, String.format("ORD-%06d", id), Jdbc.ts(rs.getString("order_date")),
                        OrderStatus.valueOf(rs.getString("status")), rs.getString("payment_method"),
                        rs.getLong("total_amount"), rs.getInt("item_count"), rs.getString("first_item"),
                        rs.getInt("customer_id"), name));
            }
        }
        return out;
    }

    private List<OrderItem> items(int orderId) throws SQLException {
        List<OrderItem> out = new ArrayList<>();
        try (PreparedStatement ps = Jdbc.prepare(connection, "SELECT * FROM order_item WHERE order_id = ? ORDER BY order_item_id", orderId);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next())
                out.add(new OrderItem(rs.getInt("order_item_id"), rs.getInt("product_id"), rs.getString("product_name"),
                        rs.getInt("quantity"), rs.getLong("unit_price")));
        }
        return out;
    }

    private List<OrderEvent> events(int orderId) throws SQLException {
        List<OrderEvent> out = new ArrayList<>();
        try (PreparedStatement ps = Jdbc.prepare(connection, "SELECT * FROM order_event WHERE order_id = ? ORDER BY occurred_at, event_id", orderId);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next())
                out.add(new OrderEvent(rs.getInt("event_id"), OrderStatus.valueOf(rs.getString("status")),
                        Jdbc.ts(rs.getString("occurred_at")), rs.getString("actor"), rs.getString("note")));
        }
        return out;
    }

    private List<Payment> payments(int orderId) throws SQLException {
        String sql = "SELECT p.*, cr.card_holder, cr.card_last4, cr.expiry, cr.provider_token, ca.cash_received, ca.change_amount "
                + "FROM payment p LEFT JOIN pay_credit cr ON cr.payment_id = p.payment_id "
                + "LEFT JOIN pay_cash ca ON ca.payment_id = p.payment_id WHERE p.order_id = ? ORDER BY p.payment_id";
        List<Payment> out = new ArrayList<>();
        try (PreparedStatement ps = Jdbc.prepare(connection, sql, orderId); ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                Payment.Status status = Payment.Status.valueOf(rs.getString("status"));
                if ("CARD".equals(rs.getString("method")))
                    out.add(new PayCredit(rs.getInt("payment_id"), rs.getLong("amount"), status, Jdbc.ts(rs.getString("payment_date")),
                            rs.getString("card_holder"), rs.getString("card_last4"), rs.getString("expiry"),
                            rs.getString("provider_token")));
                else
                    out.add(new PayCash(rs.getInt("payment_id"), rs.getLong("amount"), status, Jdbc.ts(rs.getString("payment_date")),
                            rs.getLong("cash_received"), rs.getLong("change_amount")));
            }
        }
        return out;
    }

    private Shipping shipping(int orderId) throws SQLException {
        try (PreparedStatement ps = Jdbc.prepare(connection, "SELECT * FROM shipping WHERE order_id = ?", orderId);
             ResultSet rs = ps.executeQuery()) {
            if (!rs.next()) return null;
            return new Shipping(rs.getInt("shipping_id"), rs.getInt("address_id"), rs.getString("carrier"),
                    rs.getString("tracking_number"), rs.getLong("shipping_fee"), Shipping.Status.valueOf(rs.getString("status")),
                    Jdbc.ts(rs.getString("shipped_date")), Jdbc.ts(rs.getString("delivered_date")));
        }
    }
}
