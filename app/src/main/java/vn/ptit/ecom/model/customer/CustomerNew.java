package vn.ptit.ecom.model.customer;

import java.time.LocalDate;

public class CustomerNew extends Customer {
    private final LocalDate registeredDate;
    private final String welcomeVoucher;

    public CustomerNew(int id, FullName fullName, String email, String phone, LocalDate registeredDate,
                       String welcomeVoucher) {
        super(id, fullName, email, phone);
        this.registeredDate = registeredDate;
        this.welcomeVoucher = welcomeVoucher;
    }

    @Override
    public String kindLabel() { return "New customer"; }

    public LocalDate getRegisteredDate() { return registeredDate; }
    public String getWelcomeVoucher() { return welcomeVoucher; }
}
