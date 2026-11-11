package vn.ptit.ecom.controller;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import vn.ptit.ecom.model.customer.Account;
import vn.ptit.ecom.model.customer.Role;
import vn.ptit.ecom.service.AuthService;

/** UC02 Login for customers and staff. The session holds who is logged in; the account check is AuthService's. */
@RestController
@RequestMapping("/api/auth")
public class AuthController {
    record LoginRequest(String email, String password) { }

    private final AuthService auth;

    public AuthController(AuthService auth) {
        this.auth = auth;
    }

    @PostMapping("/login")
    public Map<String, Object> login(@RequestBody LoginRequest req, HttpServletRequest http) {
        Account a = auth.login(req.email(), req.password())
                .orElseThrow(() -> new ApiErrors.Unauthorized("Email or password is incorrect."));
        HttpSession old = http.getSession(false);
        if (old != null) old.invalidate();   // a new session id after login (no session fixation)
        http.getSession(true).setAttribute(CurrentUser.KEY, new CurrentUser(a.role(), a.id(), a.displayName()));
        return me(http.getSession(false));
    }

    @PostMapping("/logout")
    public Map<String, Object> logout(HttpServletRequest http) {
        HttpSession s = http.getSession(false);
        if (s != null) s.invalidate();
        return Map.of("loggedIn", false);
    }

    @GetMapping("/me")
    public Map<String, Object> me(HttpSession session) {
        CurrentUser u = CurrentUser.of(session);
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("loggedIn", u != null);
        if (u == null) return out;
        out.put("role", u.role());
        out.put("name", u.name());
        if (u.role() == Role.CUSTOMER) {
            AuthService.CustomerProfile p = auth.profile(u.id());
            out.put("kind", p.customer().kindLabel());
            out.put("discountRate", p.customer().discountRate());
            out.put("cartCount", p.cartItems());
        }
        return out;
    }
}
