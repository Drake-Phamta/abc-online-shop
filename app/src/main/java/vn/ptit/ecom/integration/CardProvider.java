package vn.ptit.ecom.integration;

/** The external Payment Provider of UC08; only the boundary is modelled, the card network is not. */
public interface CardProvider {

    record Result(boolean approved, String token, String reason) { }

    Result charge(String orderReference, long amountVnd, CardData card);
}
