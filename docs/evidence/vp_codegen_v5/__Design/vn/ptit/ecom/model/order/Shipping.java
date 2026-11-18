package __Design.vn.ptit.ecom.model.order;

public class Shipping {
	private Integer _id;
	private int _addressId;
	private String _carrier;
	private String _trackingNumber;
	private long _shippingFee;
	private Status _status;
	private LocalDateTime _shippedDate;
	private LocalDateTime _deliveredDate;
}