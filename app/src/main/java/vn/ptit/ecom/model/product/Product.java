package vn.ptit.ecom.model.product;

import vn.ptit.ecom.model.RuleViolation;

/** Identity and the attributes every product has; kind-specific attributes are in the detail. */
public class Product {
    public enum Status { ACTIVE, HIDDEN }

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
    private final ProductDetail detail;

    public Product(int id, String sku, String name, String brand, long price, int stockQuantity, String description,
                   String imageFile, Status status, Category category, ProductDetail detail) {
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
        this.detail = detail;
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
    public ProductDetail getDetail() { return detail; }
}
