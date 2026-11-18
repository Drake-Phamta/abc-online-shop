package __Design.vn.ptit.ecom.controller;

import __Design.vn.ptit.ecom.model.customer.Role;
import Role...;

public class CurrentUser {
	private Role _role;
	private int _id;
	private String _name;

	public static CurrentUser require(HttpSession aSession, Object aRoles) {
		throw new UnsupportedOperationException();
	}
}