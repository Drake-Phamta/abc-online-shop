package __Design.vn.ptit.ecom.model.order;

public class OrderEvent {
	private Integer _id;
	private OrderStatus _status;
	private LocalDateTime _occurredAt;
	private String _actor;
	private String _note;
}