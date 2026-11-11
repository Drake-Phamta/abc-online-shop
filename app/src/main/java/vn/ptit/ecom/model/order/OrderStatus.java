package vn.ptit.ecom.model.order;

import java.util.EnumMap;
import java.util.EnumSet;
import java.util.Map;
import java.util.Set;

/** Order lifecycle of docs/SPEC.md section 3 (BR09): one transition table instead of scattered checks. */
public enum OrderStatus {
    PENDING_PAYMENT, PLACED, PAID, PROCESSING, SHIPPED, DELIVERED, CANCELLED;

    /** Who causes a transition. PROVIDER is the payment provider's approval (UC08). */
    public enum Actor { CUSTOMER, SALES, PROVIDER }

    private static final Map<OrderStatus, Map<OrderStatus, Set<Actor>>> TRANSITIONS = new EnumMap<>(OrderStatus.class);

    static {
        allow(PENDING_PAYMENT, PAID, Actor.PROVIDER);
        allow(PENDING_PAYMENT, CANCELLED, Actor.CUSTOMER);
        allow(PLACED, PROCESSING, Actor.SALES);
        allow(PLACED, CANCELLED, Actor.CUSTOMER, Actor.SALES);
        allow(PAID, PROCESSING, Actor.SALES);
        allow(PAID, CANCELLED, Actor.SALES);
        allow(PROCESSING, SHIPPED, Actor.SALES);
        allow(PROCESSING, CANCELLED, Actor.SALES);
        allow(SHIPPED, DELIVERED, Actor.SALES);
    }

    private static void allow(OrderStatus from, OrderStatus to, Actor... actors) {
        TRANSITIONS.computeIfAbsent(from, k -> new EnumMap<>(OrderStatus.class)).put(to, Set.of(actors));
    }

    public boolean canMoveTo(OrderStatus to, Actor actor) {
        return TRANSITIONS.getOrDefault(this, Map.of()).getOrDefault(to, Set.of()).contains(actor);
    }

    /** The statuses this actor may move the order to next (drives the buttons in the UI). */
    public Set<OrderStatus> next(Actor actor) {
        Set<OrderStatus> out = EnumSet.noneOf(OrderStatus.class);
        TRANSITIONS.getOrDefault(this, Map.of()).forEach((to, actors) -> { if (actors.contains(actor)) out.add(to); });
        return out;
    }
}
