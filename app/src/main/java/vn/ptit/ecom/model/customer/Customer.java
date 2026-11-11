package vn.ptit.ecom.model.customer;

import java.math.BigDecimal;

public class Customer {
    private final int id;
    private final FullName fullName;
    private final String email;
    private final String phone;

    public Customer(int id, FullName fullName, String email, String phone) {
        this.id = id;
        this.fullName = fullName;
        this.email = email;
        this.phone = phone;
    }

    /** Share of the subtotal given as discount (BR04); ordinary customers get none. */
    public BigDecimal discountRate() { return BigDecimal.ZERO; }

    /** Short label of the customer kind shown in the UI. */
    public String kindLabel() { return "Customer"; }

    public int getId() { return id; }
    public FullName getFullName() { return fullName; }
    public String getEmail() { return email; }
    public String getPhone() { return phone; }
}
