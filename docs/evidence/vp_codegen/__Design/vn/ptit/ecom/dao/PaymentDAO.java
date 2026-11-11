package __Design.vn.ptit.ecom.dao;

public interface PaymentDAO {

	public void saveAll(int orderId, List<Payment> payments);
}