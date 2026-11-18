package __Design.vn.ptit.ecom.integration;

public class SimulatedCardProvider implements CardProvider {

	public Result charge(String aOrderCode, long aAmount, CardData aCard) {
		throw new UnsupportedOperationException();
	}
}