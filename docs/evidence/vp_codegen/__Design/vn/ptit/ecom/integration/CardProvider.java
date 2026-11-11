package __Design.vn.ptit.ecom.integration;

public interface CardProvider {

	public Result charge(String orderCode, long amount, CardData card);
}