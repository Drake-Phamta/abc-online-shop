package __Design.vn.ptit.ecom.model.customer;

public class CustomerVIP extends Customer {
	private int _vipLevel;
	private BigDecimal _discountRate;
	private int _rewardPoints;

	public BigDecimal discountRate() {
		throw new UnsupportedOperationException();
	}

	public String kindLabel() {
		throw new UnsupportedOperationException();
	}
}