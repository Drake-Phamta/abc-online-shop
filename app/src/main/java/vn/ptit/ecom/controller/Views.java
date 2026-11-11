package vn.ptit.ecom.controller;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Set;
import vn.ptit.ecom.dao.OrderDAO;
import vn.ptit.ecom.model.cart.Cart;
import vn.ptit.ecom.model.cart.CartIssue;
import vn.ptit.ecom.model.customer.Address;
import vn.ptit.ecom.model.order.Order;
import vn.ptit.ecom.model.order.OrderStatus;
import vn.ptit.ecom.model.order.PayCash;
import vn.ptit.ecom.model.order.PayCredit;
import vn.ptit.ecom.model.order.Payment;
import vn.ptit.ecom.model.order.Shipping;
import vn.ptit.ecom.model.product.Product;
import vn.ptit.ecom.model.product.ProductDetail;

/** JSON shapes sent to the view classes; the model classes stay free of presentation concerns. */
final class Views {
    static final int LOW_STOCK = 3;

    private Views() { }

    /** chips: the first values of the product's detail, e.g. "16 GB" and "512 GB" for a laptop. */
    record ProductCard(int id, String sku, String name, String brand, long price, int stock, String stockState,
                       String image, String category, String categorySlug, String detailKind, List<String> chips,
                       String byline) {
        static ProductCard of(Product p) {
            List<String> chips = p.getDetail() == null ? List.of()
                    : p.getDetail().specs().stream()
                    .filter(s -> !s.label().equals("Warranty") && !s.label().equals("Author") && !s.label().equals("Publisher"))
                    .limit(3).map(ProductDetail.Spec::value).toList();
            return new ProductCard(p.getId(), p.getSku(), p.getName(), p.getBrand(), p.getPrice(), p.getStockQuantity(),
                    Views.stockState(p), Views.image(p), p.getCategory().name(), p.getCategory().slug(),
                    p.getCategory().detailKind() == null ? null : p.getCategory().detailKind().name(), chips,
                    p.getBrand() != null ? p.getBrand()
                            : p.getDetail() instanceof ProductDetail.BookDetail b ? b.author() : null);
        }
    }

    record ProductPage(ProductCard product, String description, String status, List<ProductDetail.Spec> specs,
                       String parentCategory, String parentSlug) { }

    record CartLine(int productId, String name, String brand, String image, long cartPrice, long currentPrice,
                    int quantity, int stock, long subTotal) { }

    record CartView(int cartId, List<CartLine> lines, int count, long subtotal) {
        static CartView of(Cart cart) {
            List<CartLine> lines = cart.getItems().stream().map(i -> new CartLine(i.getProduct().getId(), i.getProduct().getName(),
                    i.getProduct().getBrand(), image(i.getProduct()), i.getCartPrice(), i.getProduct().getPrice(),
                    i.getQuantity(), i.getProduct().getStockQuantity(), i.subTotal())).toList();
            return new CartView(cart.getId(), lines, lines.stream().mapToInt(CartLine::quantity).sum(), cart.calcTotal());
        }
    }

    record Issue(int productId, String kind, boolean blocking, String message, long oldPrice, long newPrice, int available) {
        static Issue of(CartIssue i) {
            return new Issue(i.productId(), i.kind().name(), i.kind().isBlocking(), i.message(), i.oldPrice(), i.newPrice(),
                    i.available());
        }
    }

    record AddressView(int id, String recipient, String phone, String line, boolean isDefault) {
        static AddressView of(Address a) {
            return new AddressView(a.id(), a.recipientName(), a.phone(), a.oneLine(), a.isDefault());
        }
    }

    record LineView(int productId, String name, int quantity, long unitPrice, long subTotal) { }

    record EventView(String status, LocalDateTime at, String actor, String note) { }

    record PaymentView(String method, String status, long amount, LocalDateTime at, String detail) {
        static PaymentView of(Payment p) {
            String detail = p instanceof PayCredit c ? c.getCardHolder() + ", card ending " + c.getCardLast4()
                    : p instanceof PayCash c ? "cash received " + c.getCashReceived() : "";
            return new PaymentView(p.method(), p.getStatus().name(), p.getAmount(), p.getPaymentDate(), detail);
        }
    }

    record ShippingView(String carrier, String trackingNumber, String status, LocalDateTime shipped, LocalDateTime delivered) {
        static ShippingView of(Shipping s) {
            return s == null ? null : new ShippingView(s.getCarrier(), s.getTrackingNumber(), s.getStatus().name(),
                    s.getShippedDate(), s.getDeliveredDate());
        }
    }

    /** One order on the board with the transitions sales staff may make from its status (BR09); the view only draws them. */
    record BoardCard(int id, String code, LocalDateTime orderDate, OrderStatus status, String paymentMethod, long totalAmount,
                     int itemCount, String firstItem, String customerName, Set<OrderStatus> next) {
        static BoardCard of(OrderDAO.OrderSummary s) {
            return new BoardCard(s.id(), s.code(), s.orderDate(), s.status(), s.paymentMethod(), s.totalAmount(), s.itemCount(),
                    s.firstItem(), s.customerName(), s.status().next(OrderStatus.Actor.SALES));
        }
    }

    record OrderView(int id, String code, LocalDateTime orderDate, String status, String paymentMethod, long subtotal,
                     long discount, long shippingFee, long total, List<LineView> lines, List<EventView> events,
                     List<PaymentView> payments, ShippingView shipping, AddressView address, String customerName,
                     Set<OrderStatus> next) {
        static OrderView of(Order o, Address address, String customerName, Set<OrderStatus> next) {
            return new OrderView(o.getId(), o.code(), o.getOrderDate(), o.getStatus().name(), o.getPaymentMethod().name(),
                    o.getSubtotal(), o.getDiscount(), o.getShippingFee(), o.getTotalAmount(),
                    o.getItems().stream().map(i -> new LineView(i.productId(), i.productName(), i.quantity(), i.unitPrice(),
                            i.subTotal())).toList(),
                    o.getEvents().stream().map(e -> new EventView(e.status().name(), e.occurredAt(), e.actor(), e.note())).toList(),
                    o.getPayments().stream().map(PaymentView::of).toList(), ShippingView.of(o.getShipping()),
                    address == null ? null : AddressView.of(address), customerName, next);
        }
    }

    static String stockState(Product p) {
        if (p.getStockQuantity() == 0) return "OUT";
        return p.getStockQuantity() <= LOW_STOCK ? "LOW" : "IN";
    }

    static String image(Product p) {
        return p.getImageFile() == null ? null : "/img/products/" + p.getImageFile();
    }
}
