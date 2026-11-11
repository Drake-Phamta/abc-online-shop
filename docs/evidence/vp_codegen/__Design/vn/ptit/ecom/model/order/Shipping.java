package __Design.vn.ptit.ecom.model.order;

public class Shipping {
	private Integer id;
	private int addressId;
	private String carrier;
	private String trackingNumber;
	private long shippingFee;
	private Status status;
	private LocalDateTime shippedDate;
	private LocalDateTime deliveredDate;
}