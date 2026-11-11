package __Design.vn.ptit.ecom.model.order;

public class Totals {
	private long subtotal;
	private long discount;
	private long shippingFee;
	private long total;

	public static Totals of(long subtotal, BigDecimal rate) {
		throw new UnsupportedOperationException();
	}
}