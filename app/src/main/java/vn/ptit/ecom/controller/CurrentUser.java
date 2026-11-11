package vn.ptit.ecom.controller;

import jakarta.servlet.http.HttpSession;
import java.util.Arrays;
import vn.ptit.ecom.model.customer.Role;

/** The logged-in user kept in the HTTP session (UC02); controllers read ids from here, never from the request (BR08). */
record CurrentUser(Role role, int id, String name) {
    static final String KEY = "currentUser";

    static CurrentUser of(HttpSession session) {
        return session == null ? null : (CurrentUser) session.getAttribute(KEY);
    }

    /** BR13: the caller must be logged in with one of the roles. */
    static CurrentUser require(HttpSession session, Role... roles) {
        CurrentUser user = of(session);
        if (user == null) throw new ApiErrors.Unauthorized();
        if (!Arrays.asList(roles).contains(user.role())) throw new ApiErrors.Forbidden();
        return user;
    }
}
