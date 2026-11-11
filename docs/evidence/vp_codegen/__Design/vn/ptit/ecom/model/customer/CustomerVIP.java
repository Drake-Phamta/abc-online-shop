package __Design.vn.ptit.ecom.model.customer;

public class CustomerVIP extends Customer {
	private int vipLevel;
	private BigDecimal discountRate;
	private int rewardPoints;

	public BigDecimal discountRate() {
		throw new UnsupportedOperationException();
	}

	public String kindLabel() {
		throw new UnsupportedOperationException();
	}
}