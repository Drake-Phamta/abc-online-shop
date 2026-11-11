package __Design.vn.ptit.ecom.model.order;

public class OrderEvent {
	private Integer id;
	private OrderStatus status;
	private LocalDateTime occurredAt;
	private String actor;
	private String note;
}