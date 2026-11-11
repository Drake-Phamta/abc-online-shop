package vn.ptit.ecom.controller;

import jakarta.servlet.http.HttpSession;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import vn.ptit.ecom.model.customer.Role;
import vn.ptit.ecom.service.CartService;

/** UC06 Manage Shopping Cart. The customer id always comes from the session, never from the request (BR08). */
@RestController
@RequestMapping("/api/cart")
public class CartController {
    record AddItem(Integer productId, Integer quantity) { }

    record ChangeQuantity(Integer quantity) { }

    private final CartService carts;

    public CartController(CartService carts) {
        this.carts = carts;
    }

    @GetMapping
    public Views.CartView viewCart(HttpSession session) {
        CurrentUser u = CurrentUser.require(session, Role.CUSTOMER);
        return Views.CartView.of(carts.cart(u.id()));
    }

    @PostMapping("/items")
    public Views.CartView addItem(@RequestBody AddItem req, HttpSession session) {
        CurrentUser u = CurrentUser.require(session, Role.CUSTOMER);
        if (req.productId() == null || req.quantity() == null) throw new IllegalArgumentException("Choose a product and a quantity.");
        return Views.CartView.of(carts.addItem(u.id(), req.productId(), req.quantity()));
    }

    @PutMapping("/items/{productId}")
    public Views.CartView changeQuantity(@PathVariable int productId, @RequestBody ChangeQuantity req, HttpSession session) {
        CurrentUser u = CurrentUser.require(session, Role.CUSTOMER);
        if (req.quantity() == null) throw new IllegalArgumentException("Enter a quantity.");
        return Views.CartView.of(carts.changeQuantity(u.id(), productId, req.quantity()));
    }

    @DeleteMapping("/items/{productId}")
    public Views.CartView removeItem(@PathVariable int productId, HttpSession session) {
        CurrentUser u = CurrentUser.require(session, Role.CUSTOMER);
        return Views.CartView.of(carts.removeItem(u.id(), productId));
    }
}
