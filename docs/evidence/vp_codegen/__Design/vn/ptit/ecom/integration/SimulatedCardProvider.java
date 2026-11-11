package __Design.vn.ptit.ecom.integration;

public class SimulatedCardProvider implements CardProvider {

	public Result charge(String orderCode, long amount, CardData card) {
		throw new UnsupportedOperationException();
	}
}