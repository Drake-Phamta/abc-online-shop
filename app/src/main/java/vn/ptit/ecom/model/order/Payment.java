package vn.ptit.ecom.model.order;

import java.time.LocalDateTime;

/** A payment of an order; always cash or card. id is null until stored. */
public abstract class Payment {
    public enum Status { APPROVED, DECLINED, REFUNDED, COMPLETED }

    private Integer id;
    private final long amount;
    private Status status;
    private final LocalDateTime paymentDate;

    protected Payment(Integer id, long amount, Status status, LocalDateTime paymentDate) {
        this.id = id;
        this.amount = amount;
        this.status = status;
        this.paymentDate = paymentDate;
    }

    /** "CARD" or "CASH", the payment.method column. */
    public abstract String method();

    /** Money that was taken is returned when a paid order is cancelled. */
    void refund() {
        if (status == Status.APPROVED) status = Status.REFUNDED;
    }

    public boolean isSuccessful() { return status == Status.APPROVED || status == Status.COMPLETED; }

    public void assignId(int id) { this.id = id; }
    public Integer getId() { return id; }
    public long getAmount() { return amount; }
    public Status getStatus() { return status; }
    public LocalDateTime getPaymentDate() { return paymentDate; }
}
