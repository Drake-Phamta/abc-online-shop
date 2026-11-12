package vn.ptit.ecom.controller;

import jakarta.servlet.http.HttpSession;
import java.util.ArrayList;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import vn.ptit.ecom.dao.ProductDAO;
import vn.ptit.ecom.model.customer.Role;
import vn.ptit.ecom.model.product.Category;
import vn.ptit.ecom.model.product.Product;
import vn.ptit.ecom.service.CatalogService;

/** UC04 Browse / Search Products, UC05 View Product, UC15 Manage Inventory. */
@RestController
public class ProductController {
    record CategoryNode(int id, String name, String slug, List<CategoryNode> children) { }

    record StockRow(int id, String sku, String name, String category, int stock, String stockState, String status, String image) {
        static StockRow of(Product p) {
            return new StockRow(p.getId(), p.getSku(), p.getName(), p.getCategory().name(), p.getStockQuantity(),
                    Views.stockState(p), p.getStatus().name(), Views.image(p));
        }
    }

    record StockChange(Integer quantity) { }

    private final CatalogService catalog;

    public ProductController(CatalogService catalog) {
        this.catalog = catalog;
    }

    /** The category tree for the navigation (roots with their sub-categories). */
    @GetMapping("/api/categories")
    public List<CategoryNode> categories() {
        List<Category> all = catalog.categories();
        List<CategoryNode> roots = new ArrayList<>();
        for (Category c : all)
            if (c.parentId() == null) {
                List<CategoryNode> children = all.stream().filter(k -> k.parentId() != null && k.parentId() == c.id())
                        .map(k -> new CategoryNode(k.id(), k.name(), k.slug(), List.of())).toList();
                roots.add(new CategoryNode(c.id(), c.name(), c.slug(), children));
            }
        return roots;
    }

    @GetMapping("/api/products")
    public List<Views.ProductCard> search(@RequestParam(required = false) String q,
                                          @RequestParam(required = false) String category,
                                          @RequestParam(required = false, defaultValue = "RELEVANCE") ProductDAO.Sort sort) {
        return catalog.search(q, category, sort).stream().map(Views.ProductCard::of).toList();
    }

    @GetMapping("/api/products/{id}")
    public Views.ProductPage product(@PathVariable int id) {
        CatalogService.ProductDetails pd = catalog.product(id);
        Product p = pd.product();
        Category parent = pd.parentCategory();
        return new Views.ProductPage(Views.ProductCard.of(p), p.getDescription(), p.getStatus().name(),
                p.specs(),
                parent == null ? null : parent.name(), parent == null ? null : parent.slug());
    }

    @GetMapping("/api/staff/stock")
    public List<StockRow> stock(HttpSession session) {
        CurrentUser.require(session, Role.WAREHOUSE);
        return catalog.stockList().stream().map(StockRow::of).toList();
    }

    @PutMapping("/api/staff/stock/{id}")
    public StockRow updateStock(@PathVariable int id, @RequestBody StockChange change, HttpSession session) {
        CurrentUser.require(session, Role.WAREHOUSE);
        if (change.quantity() == null) throw new IllegalArgumentException("Enter a quantity.");
        return StockRow.of(catalog.updateStock(id, change.quantity()));
    }
}
