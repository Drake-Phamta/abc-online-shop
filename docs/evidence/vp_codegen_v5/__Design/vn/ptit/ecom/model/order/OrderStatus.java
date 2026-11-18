package __Design.vn.ptit.ecom.model.order;

public enum OrderStatus {

	public boolean canMoveTo(OrderStatus aTo, Actor aActor) {
		throw new UnsupportedOperationException();
	}

	public Set<OrderStatus> next(Actor aActor) {
		throw new UnsupportedOperationException();
	}
}