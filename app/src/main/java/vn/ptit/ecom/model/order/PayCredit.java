package vn.ptit.ecom.model.order;

import java.time.LocalDateTime;

/** Card payment; only the last four digits and the provider token are kept (BR07). */
public class PayCredit extends Payment {
    private final String cardHolder;
    private final String cardLast4;
    private final String expiry;
    private final String providerToken;

    public PayCredit(Integer id, long amount, Status status, LocalDateTime paymentDate, String cardHolder,
                     String cardLast4, String expiry, String providerToken) {
        super(id, amount, status, paymentDate);
        this.cardHolder = cardHolder;
        this.cardLast4 = cardLast4;
        this.expiry = expiry;
        this.providerToken = providerToken;
    }

    @Override
    public String method() { return "CARD"; }

    public String getCardHolder() { return cardHolder; }
    public String getCardLast4() { return cardLast4; }
    public String getExpiry() { return expiry; }
    public String getProviderToken() { return providerToken; }
}
