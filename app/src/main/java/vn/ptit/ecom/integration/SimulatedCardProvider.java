package vn.ptit.ecom.integration;

import java.security.SecureRandom;
import java.util.HexFormat;

/** Stand-in for the real provider (docs/SPEC.md section 1): cards ending in 0002 are declined. */
public class SimulatedCardProvider implements CardProvider {
    private final SecureRandom random = new SecureRandom();

    @Override
    public Result charge(String orderReference, long amountVnd, CardData card) {
        if (card.number().endsWith("0002")) return new Result(false, null, "Declined by the issuing bank");
        byte[] bytes = new byte[12];
        random.nextBytes(bytes);
        return new Result(true, "tok_" + HexFormat.of().formatHex(bytes), null);
    }
}
