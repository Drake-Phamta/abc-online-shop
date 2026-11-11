package vn.ptit.ecom.model.order;

import java.time.LocalDateTime;

/** The one shipment of an order (BR10). id is null until stored. */
public class Shipping {
    public enum Status { IN_TRANSIT, DELIVERED }

    private Integer id;
    private final int addressId;
    private final String carrier;
    private final String trackingNumber;
    private final long shippingFee;
    private Status status;
    private final LocalDateTime shippedDate;
    private LocalDateTime deliveredDate;

    public Shipping(Integer id, int addressId, String carrier, String trackingNumber, long shippingFee, Status status,
                    LocalDateTime shippedDate, LocalDateTime deliveredDate) {
        this.id = id;
        this.addressId = addressId;
        this.carrier = carrier;
        this.trackingNumber = trackingNumber;
        this.shippingFee = shippingFee;
        this.status = status;
        this.shippedDate = shippedDate;
        this.deliveredDate = deliveredDate;
    }

    void markDelivered(LocalDateTime when) {
        status = Status.DELIVERED;
        deliveredDate = when;
    }

    public void assignId(int id) { this.id = id; }
    public Integer getId() { return id; }
    public int getAddressId() { return addressId; }
    public String getCarrier() { return carrier; }
    public String getTrackingNumber() { return trackingNumber; }
    public long getShippingFee() { return shippingFee; }
    public Status getStatus() { return status; }
    public LocalDateTime getShippedDate() { return shippedDate; }
    public LocalDateTime getDeliveredDate() { return deliveredDate; }
}
