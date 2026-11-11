package __Design.vn.ptit.ecom.controller;

import __Design.vn.ptit.ecom.model.customer.Role;
import Role...;

public class CurrentUser {
	private Role role;
	private int id;
	private String name;

	public static CurrentUser require(HttpSession session, Object roles) {
		throw new UnsupportedOperationException();
	}
}