package __Design.vn.ptit.ecom.dao;

import __Design.vn.ptit.ecom.model.cart.Cart;

public interface CartDAO {

	public Cart findOrCreate(int aCustomerId);

	public void save(Cart aCart);

	public void clear(Cart aCart);
}