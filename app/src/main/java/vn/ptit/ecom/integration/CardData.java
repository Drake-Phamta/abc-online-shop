package vn.ptit.ecom.integration;

import java.time.YearMonth;

/** Card data typed by the customer; checked before the provider is called (UC08 A2). Never stored. */
public record CardData(String holder, String number, String expiry, String cvv) {

    public CardData {
        holder = holder == null ? "" : holder.trim();
        number = number == null ? "" : number.replaceAll("[\\s-]", "");
        expiry = expiry == null ? "" : expiry.trim();
        cvv = cvv == null ? "" : cvv.trim();
        if (holder.length() < 2) throw new IllegalArgumentException("Enter the name printed on the card.");
        if (!number.matches("\\d{16}") || !luhn(number)) throw new IllegalArgumentException("The card number is not valid.");
        if (!expiry.matches("(0[1-9]|1[0-2])/\\d{2}")) throw new IllegalArgumentException("Expiry must look like MM/YY.");
        YearMonth exp = YearMonth.of(2000 + Integer.parseInt(expiry.substring(3)), Integer.parseInt(expiry.substring(0, 2)));
        if (exp.isBefore(YearMonth.now())) throw new IllegalArgumentException("The card has expired.");
        if (!cvv.matches("\\d{3}")) throw new IllegalArgumentException("CVV must be 3 digits.");
    }

    public String last4() { return number.substring(12); }

    private static boolean luhn(String digits) {
        int sum = 0;
        for (int i = 0; i < digits.length(); i++) {
            int d = digits.charAt(digits.length() - 1 - i) - '0';
            if (i % 2 == 1) { d *= 2; if (d > 9) d -= 9; }
            sum += d;
        }
        return sum % 10 == 0;
    }
}
