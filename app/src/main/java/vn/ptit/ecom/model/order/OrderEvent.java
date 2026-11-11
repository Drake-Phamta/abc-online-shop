package vn.ptit.ecom.model.order;

import java.time.LocalDateTime;

/** One entry of the order history shown in UC09; id is null until stored. */
public record OrderEvent(Integer id, OrderStatus status, LocalDateTime occurredAt, String actor, String note) { }
