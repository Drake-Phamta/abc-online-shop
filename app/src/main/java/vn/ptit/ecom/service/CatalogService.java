package vn.ptit.ecom.service;

import java.util.List;
import org.springframework.stereotype.Service;
import vn.ptit.ecom.dao.Database;
import vn.ptit.ecom.dao.ProductDAO;
import vn.ptit.ecom.model.product.Category;
import vn.ptit.ecom.model.product.Product;

/** UC04 Browse / Search Products, UC05 View Product, UC15 Manage Inventory. */
@Service
public class CatalogService {
    /** A product page: the product with its detail, and the parent of its category for the breadcrumb. */
    public record ProductDetails(Product product, Category parentCategory) { }

    private final Database db;

    public CatalogService(Database db) {
        this.db = db;
    }

    public List<Category> categories() {
        return db.inTransaction(d -> d.products().categories());
    }

    /** UC04: ACTIVE products only; a parent category includes its sub-categories. */
    public List<Product> search(String keyword, String categorySlug, ProductDAO.Sort sort) {
        return db.inTransaction(d -> d.products().search(keyword, categorySlug, sort));
    }

    /** UC05: a hidden product is reported as missing (BR01). */
    public ProductDetails product(int id) {
        return db.inTransaction(d -> {
            Product p = d.products().findById(id).filter(x -> x.getStatus() == Product.Status.ACTIVE)
                    .orElseThrow(() -> new NotFound("This product does not exist."));
            Integer parentId = p.getCategory().parentId();
            Category parent = parentId == null ? null
                    : d.products().categories().stream().filter(c -> c.id() == parentId).findFirst().orElse(null);
            return new ProductDetails(p, parent);
        });
    }

    /** UC15 step 1: every product, lowest stock first. */
    public List<Product> stockList() {
        return db.inTransaction(d -> d.products().listForStock());
    }

    /** UC15 steps 2 and 3: the new quantity is checked by the model (BR12) before it is stored. */
    public Product updateStock(int productId, int quantity) {
        return db.inTransaction(d -> {
            Product p = d.products().findById(productId).orElseThrow(() -> new NotFound("This product does not exist."));
            p.updateStock(quantity);
            d.products().updateStock(productId, p.getStockQuantity());
            return p;
        });
    }
}
