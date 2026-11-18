package __Design.vn.ptit.ecom.model.order;

import java.util.Vector;
import __Design.vn.ptit.ecom.model.order.Payment;

public class Order {
	private Integer _id;
	private int _customerId;
	private int _addressId;
	private LocalDateTime _orderDate;
	private OrderStatus _status;
	private PaymentMethod _paymentMethod;
	private long _subtotal;
	private long _discount;
	private long _shippingFee;
	private long _totalAmount;
	public Vector<OrderItem> _items = new Vector<OrderItem>();
	public Vector<OrderEvent> _events = new Vector<OrderEvent>();
	public Vector<Payment> _payments = new Vector<Payment>();
	public Shipping _shipping;

	public static Order place(Customer aCustomer, Cart aCart, Address aAddress, PaymentMethod aMethod, LocalDateTime aNow) {
		throw new UnsupportedOperationException();
	}

	public void changeStatus(OrderStatus aTo, Actor aActor, String aActorName, LocalDateTime aNow, String aNote) {
		throw new UnsupportedOperationException();
	}

	public void recordCardPayment(PayCredit aPayment, LocalDateTime aNow) {
		throw new UnsupportedOperationException();
	}

	public void cancel(Actor aActor, String aActorName, LocalDateTime aNow) {
		throw new UnsupportedOperationException();
	}

	public Shipping ship(String aCarrier, String aTrackingNumber, String aActorName, LocalDateTime aNow) {
		throw new UnsupportedOperationException();
	}

	public void deliver(String aActorName, LocalDateTime aNow) {
		throw new UnsupportedOperationException();
	}

	public String code() {
		throw new UnsupportedOperationException();
	}
}