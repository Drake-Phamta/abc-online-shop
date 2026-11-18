package __Design.vn.ptit.ecom.model.order;

public class Totals {
	private long _subtotal;
	private long _discount;
	private long _shippingFee;
	private long _total;

	public static Totals of(long aSubtotal, BigDecimal aRate) {
		throw new UnsupportedOperationException();
	}
}