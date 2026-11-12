package vn.ptit.ecom.model.product;

import java.util.ArrayList;
import java.util.List;
import vn.ptit.ecom.model.RuleViolation;

/**
 * Identity and the attributes every product has. A product of a kind with its own attributes is an instance of a
 * subclass (BookDetail, LaptopDetail, PhoneDetail, ApparelDetail), stored as a product row plus a row of its detail table.
 */
public class Product {
    public enum Status { ACTIVE, HIDDEN }

    /** One label and value of the product page (UC05). */
    public record Spec(String label, String value) { }

    private final int id;
    private final String sku;
    private final String name;
    private final String brand;
    private final long price;
    private int stockQuantity;
    private final String description;
    private final String imageFile;
    private final Status status;
    private final Category category;

    public Product(int id, String sku, String name, String brand, long price, int stockQuantity, String description,
                   String imageFile, Status status, Category category) {
        this.id = id;
        this.sku = sku;
        this.name = name;
        this.brand = brand;
        this.price = price;
        this.stockQuantity = stockQuantity;
        this.description = description;
        this.imageFile = imageFile;
        this.status = status;
        this.category = category;
    }

    /** A subclass object for the same product row: the common attributes are copied from the row. */
    protected Product(Product row) {
        this(row.id, row.sku, row.name, row.brand, row.price, row.stockQuantity, row.description, row.imageFile,
                row.status, row.category);
    }

    /** BR01 and stock: can this quantity be bought now? */
    public boolean isAvailable(int quantity) {
        return status == Status.ACTIVE && quantity <= stockQuantity;
    }

    /** UC15, BR12. */
    public void updateStock(int quantity) {
        if (quantity < 0) throw new RuleViolation("BR12", "Stock quantity cannot be negative.");
        this.stockQuantity = quantity;
    }

    /** The kind of the subclass; a product without kind-specific attributes has none. */
    public DetailKind kind() { return null; }

    /** Kind-specific attributes in display order (UC05); every subclass overrides it. */
    public List<Spec> specs() { return List.of(); }

    public int getId() { return id; }
    public String getSku() { return sku; }
    public String getName() { return name; }
    public String getBrand() { return brand; }
    public long getPrice() { return price; }
    public int getStockQuantity() { return stockQuantity; }
    public String getDescription() { return description; }
    public String getImageFile() { return imageFile; }
    public Status getStatus() { return status; }
    public Category getCategory() { return category; }

    static Spec spec(String label, String value) { return value == null ? null : new Spec(label, value); }

    static List<Spec> list(Spec... specs) {
        List<Spec> out = new ArrayList<>();
        for (Spec s : specs) if (s != null) out.add(s);
        return out;
    }
}
