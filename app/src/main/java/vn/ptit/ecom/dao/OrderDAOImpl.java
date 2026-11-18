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
        int id = Jdbc.insert(connection, "INSERT INTO Orders (CustomerId, AddressId, OrderDate, Status, PaymentMethod, "
                        + "Subtotal, Discount, ShippingFee, TotalAmount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                o.getCustomerId(), o.getAddressId(), Jdbc.ts(o.getOrderDate()), o.getStatus().name(),
                o.getPaymentMethod().name(), o.getSubtotal(), o.getDiscount(), o.getShippingFee(), o.getTotalAmount());
        o.assignId(id);
        for (OrderItem i : o.getItems())
            Jdbc.update(connection, "INSERT INTO OrderItem (OrderId, ProductId, ProductName, Quantity, UnitPrice) "
                    + "VALUES (?, ?, ?, ?, ?)", id, i.productId(), i.productName(), i.quantity(), i.unitPrice());
        insertNewEvents(o);
    }

    @Override
    public Optional<Order> findById(int orderId) throws SQLException {
        try (PreparedStatement ps = Jdbc.prepare(connection, "SELECT * FROM Orders WHERE OrderId = ?", orderId);
             ResultSet rs = ps.executeQuery()) {
            if (!rs.next()) return Optional.empty();
            return Optional.of(new Order(rs.getInt("OrderId"), rs.getInt("CustomerId"), rs.getInt("AddressId"),
                    Jdbc.ts(rs.getString("OrderDate")), OrderStatus.valueOf(rs.getString("Status")),
                    PaymentMethod.valueOf(rs.getString("PaymentMethod")), rs.getLong("Subtotal"), rs.getLong("Discount"),
                    rs.getLong("ShippingFee"), rs.getLong("TotalAmount"), items(orderId), events(orderId),
                    payments(orderId), shipping(orderId)));
        }
    }

    @Override
    public List<OrderSummary> findByCustomer(int customerId) throws SQLException {
        return summaries("WHERE o.CustomerId = ?", customerId);
    }

    @Override
    public List<OrderSummary> findAll() throws SQLException {
        return summaries("");
    }

    @Override
    public void saveProgress(Order o) throws SQLException {
        Jdbc.update(connection, "UPDATE Orders SET Status = ? WHERE OrderId = ?", o.getStatus().name(), o.getId());
        insertNewEvents(o);
    }

    private void insertNewEvents(Order o) throws SQLException {
        for (OrderEvent e : o.getEvents())
            if (e.id() == null)
                Jdbc.update(connection, "INSERT INTO OrderEvent (OrderId, Status, OccurredAt, Actor, Note) VALUES (?, ?, ?, ?, ?)",
                        o.getId(), e.status().name(), Jdbc.ts(e.occurredAt()), e.actor(), e.note());
    }

    private List<OrderSummary> summaries(String where, Object... args) throws SQLException {
        String sql = "SELECT o.*, c.FirstName, c.MiddleName, c.LastName, "
                + "(SELECT sum(Quantity) FROM OrderItem i WHERE i.OrderId = o.OrderId) AS item_count, "
                + "(SELECT ProductName FROM OrderItem i WHERE i.OrderId = o.OrderId ORDER BY OrderItemId LIMIT 1) AS first_item "
                + "FROM Orders o JOIN Customer c ON c.CustomerId = o.CustomerId " + where
                + " ORDER BY o.OrderDate DESC, o.OrderId DESC";
        List<OrderSummary> out = new ArrayList<>();
        try (PreparedStatement ps = Jdbc.prepare(connection, sql, args); ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                String middle = rs.getString("MiddleName");
                String name = rs.getString("LastName") + (middle == null ? "" : " " + middle) + " " + rs.getString("FirstName");
                int id = rs.getInt("OrderId");
                out.add(new OrderSummary(id, String.format("ORD-%06d", id), Jdbc.ts(rs.getString("OrderDate")),
                        OrderStatus.valueOf(rs.getString("Status")), rs.getString("PaymentMethod"),
                        rs.getLong("TotalAmount"), rs.getInt("item_count"), rs.getString("first_item"),
                        rs.getInt("CustomerId"), name));
            }
        }
        return out;
    }

    private List<OrderItem> items(int orderId) throws SQLException {
        List<OrderItem> out = new ArrayList<>();
        try (PreparedStatement ps = Jdbc.prepare(connection, "SELECT * FROM OrderItem WHERE OrderId = ? ORDER BY OrderItemId", orderId);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next())
                out.add(new OrderItem(rs.getInt("OrderItemId"), rs.getInt("ProductId"), rs.getString("ProductName"),
                        rs.getInt("Quantity"), rs.getLong("UnitPrice")));
        }
        return out;
    }

    private List<OrderEvent> events(int orderId) throws SQLException {
        List<OrderEvent> out = new ArrayList<>();
        try (PreparedStatement ps = Jdbc.prepare(connection, "SELECT * FROM OrderEvent WHERE OrderId = ? ORDER BY OccurredAt, EventId", orderId);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next())
                out.add(new OrderEvent(rs.getInt("EventId"), OrderStatus.valueOf(rs.getString("Status")),
                        Jdbc.ts(rs.getString("OccurredAt")), rs.getString("Actor"), rs.getString("Note")));
        }
        return out;
    }

    private List<Payment> payments(int orderId) throws SQLException {
        String sql = "SELECT p.*, cr.CardHolder, cr.CardLast4, cr.Expiry, cr.ProviderToken, ca.CashReceived, ca.ChangeAmount "
                + "FROM Payment p LEFT JOIN PayCredit cr ON cr.PaymentId = p.PaymentId "
                + "LEFT JOIN PayCash ca ON ca.PaymentId = p.PaymentId WHERE p.OrderId = ? ORDER BY p.PaymentId";
        List<Payment> out = new ArrayList<>();
        try (PreparedStatement ps = Jdbc.prepare(connection, sql, orderId); ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                Payment.Status status = Payment.Status.valueOf(rs.getString("Status"));
                if ("CARD".equals(rs.getString("Method")))
                    out.add(new PayCredit(rs.getInt("PaymentId"), rs.getLong("Amount"), status, Jdbc.ts(rs.getString("PaymentDate")),
                            rs.getString("CardHolder"), rs.getString("CardLast4"), rs.getString("Expiry"),
                            rs.getString("ProviderToken")));
                else
                    out.add(new PayCash(rs.getInt("PaymentId"), rs.getLong("Amount"), status, Jdbc.ts(rs.getString("PaymentDate")),
                            rs.getLong("CashReceived"), rs.getLong("ChangeAmount")));
            }
        }
        return out;
    }

    private Shipping shipping(int orderId) throws SQLException {
        try (PreparedStatement ps = Jdbc.prepare(connection, "SELECT * FROM Shipping WHERE OrderId = ?", orderId);
             ResultSet rs = ps.executeQuery()) {
            if (!rs.next()) return null;
            return new Shipping(rs.getInt("ShippingId"), rs.getInt("AddressId"), rs.getString("Carrier"),
                    rs.getString("TrackingNumber"), rs.getLong("ShippingFee"), Shipping.Status.valueOf(rs.getString("Status")),
                    Jdbc.ts(rs.getString("ShippedDate")), Jdbc.ts(rs.getString("DeliveredDate")));
        }
    }
}
