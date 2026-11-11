package vn.ptit.ecom.service;

import java.util.Optional;
import org.springframework.stereotype.Service;
import vn.ptit.ecom.dao.Database;
import vn.ptit.ecom.model.customer.Account;
import vn.ptit.ecom.model.customer.Customer;

/** UC02 Login: finds the account (customer first, then staff) and checks the password hash. */
@Service
public class AuthService {
    /** What the header shows for a logged-in customer. */
    public record CustomerProfile(Customer customer, int cartItems) { }

    private final Database db;

    public AuthService(Database db) {
        this.db = db;
    }

    /** UC02 step 2. Empty for an unknown email and for a wrong password alike (UC02 A1 gives no hint which one). */
    public Optional<Account> login(String email, String password) {
        String key = email == null ? "" : email.trim();
        Optional<Account> account = db.inTransaction(d -> {
            Optional<Account> a = d.customers().findAccount(key);
            return a.isPresent() ? a : d.staff().findAccount(key);
        });
        return account.filter(a -> password != null && PasswordHasher.matches(password, a.passwordHash()));
    }

    public CustomerProfile profile(int customerId) {
        return db.inTransaction(d -> {
            Customer c = d.customers().findById(customerId).orElseThrow(() -> new NotFound("Customer not found."));
            int items = d.carts().findOrCreate(customerId).getItems().stream().mapToInt(i -> i.getQuantity()).sum();
            return new CustomerProfile(c, items);
        });
    }
}
