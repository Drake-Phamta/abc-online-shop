package vn.ptit.ecom.model;

import java.util.List;

/** A business rule of docs/SPEC.md (BR01 to BR13) refused an operation. */
public class RuleViolation extends RuntimeException {
    private final String rule;
    private final List<?> details;

    public RuleViolation(String rule, String message) {
        this(rule, message, List.of());
    }

    public RuleViolation(String rule, String message, List<?> details) {
        super(message);
        this.rule = rule;
        this.details = details;
    }

    public String getRule() { return rule; }
    public List<?> getDetails() { return details; }
}
