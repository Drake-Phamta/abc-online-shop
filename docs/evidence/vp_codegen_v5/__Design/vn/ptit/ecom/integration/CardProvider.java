package __Design.vn.ptit.ecom.integration;

public interface CardProvider {

	public Result charge(String aOrderCode, long aAmount, CardData aCard);
}