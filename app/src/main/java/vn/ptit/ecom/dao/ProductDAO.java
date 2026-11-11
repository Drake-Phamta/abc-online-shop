package vn.ptit.ecom.dao;

import java.sql.SQLException;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import vn.ptit.ecom.model.product.Category;
import vn.ptit.ecom.model.product.Product;

public interface ProductDAO {

    enum Sort { RELEVANCE, PRICE_ASC, PRICE_DESC, NEWEST }

    List<Category> categories() throws SQLException;

    /** UC04: active products of a category and its sub-categories whose name, brand or category matches. */
    List<Product> search(String keyword, String categorySlug, Sort sort) throws SQLException;

    /** UC05: one product with its category and its detail. */
    Optional<Product> findById(int productId) throws SQLException;

    /** Current rows (without detail) of the given products. */
    Map<Integer, Product> findByIds(Collection<Integer> productIds) throws SQLException;

    /** BR05: takes the quantity only if enough stock is left; false means nothing was changed. */
    boolean reserveStock(int productId, int quantity) throws SQLException;

    void releaseStock(int productId, int quantity) throws SQLException;

    /** UC15. */
    void updateStock(int productId, int quantity) throws SQLException;

    /** UC15: every product, lowest stock first. */
    List<Product> listForStock() throws SQLException;
}
