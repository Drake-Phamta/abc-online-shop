package __Design.vn.ptit.ecom.model.order;

import java.util.Vector;
import __Design.vn.ptit.ecom.model.order.Payment;

public class Order {
	private Integer id;
	private int customerId;
	private int addressId;
	private LocalDateTime orderDate;
	private OrderStatus status;
	private PaymentMethod paymentMethod;
	private long subtotal;
	private long discount;
	private long shippingFee;
	private long totalAmount;
	public Vector<OrderItem> items = new Vector<OrderItem>();
	public Vector<OrderEvent> events = new Vector<OrderEvent>();
	public Vector<Payment> payments = new Vector<Payment>();
	public Shipping shipping;

	public static Order place(Customer customer, Cart cart, Address address, PaymentMethod method, LocalDateTime now) {
		throw new UnsupportedOperationException();
	}

	public void changeStatus(OrderStatus to, Actor actor, String actorName, LocalDateTime now, String note) {
		throw new UnsupportedOperationException();
	}

	public void recordCardPayment(PayCredit payment, LocalDateTime now) {
		throw new UnsupportedOperationException();
	}

	public void cancel(Actor actor, String actorName, LocalDateTime now) {
		throw new UnsupportedOperationException();
	}

	public Shipping ship(String carrier, String trackingNumber, String actorName, LocalDateTime now) {
		throw new UnsupportedOperationException();
	}

	public void deliver(String actorName, LocalDateTime now) {
		throw new UnsupportedOperationException();
	}

	public String code() {
		throw new UnsupportedOperationException();
	}
}