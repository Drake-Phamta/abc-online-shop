package __Design.vn.ptit.ecom.model.order;

public enum OrderStatus {
	PENDING_PAYMENT, 
	PLACED, 
	PAID, 
	PROCESSING, 
	SHIPPED, 
	DELIVERED, 
	CANCELLED;

	public boolean canMoveTo(OrderStatus to, Actor actor) {
		throw new UnsupportedOperationException();
	}

	public Set<OrderStatus> next(Actor actor) {
		throw new UnsupportedOperationException();
	}
}