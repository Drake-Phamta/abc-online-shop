package vn.ptit.ecom.model.order;

import java.time.LocalDateTime;

/** Cash collected on delivery (BR11). */
public class PayCash extends Payment {
    private final long cashReceived;
    private final long changeAmount;

    public PayCash(Integer id, long amount, Status status, LocalDateTime paymentDate, long cashReceived, long changeAmount) {
        super(id, amount, status, paymentDate);
        this.cashReceived = cashReceived;
        this.changeAmount = changeAmount;
    }

    @Override
    public String method() { return "CASH"; }

    public long getCashReceived() { return cashReceived; }
    public long getChangeAmount() { return changeAmount; }
}
