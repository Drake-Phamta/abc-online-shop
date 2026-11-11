package __Design.vn.ptit.ecom.controller;

import __Design.vn.ptit.ecom.service.AuthService;

public class AuthController {
	private AuthService auth;

	public Map login(LoginRequest req, HttpServletRequest http) {
		throw new UnsupportedOperationException();
	}

	public Map logout(HttpServletRequest http) {
		throw new UnsupportedOperationException();
	}

	public Map me(HttpSession session) {
		throw new UnsupportedOperationException();
	}
}