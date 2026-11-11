package __Design.vn.ptit.ecom.dao;

import __Design.vn.ptit.ecom.model.cart.Cart;

public interface CartDAO {

	public Cart findOrCreate(int customerId);

	public void save(Cart cart);

	public void clear(Cart cart);
}