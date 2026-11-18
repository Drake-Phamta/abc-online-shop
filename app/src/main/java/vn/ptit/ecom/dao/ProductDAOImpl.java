package vn.ptit.ecom.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import vn.ptit.ecom.model.product.ApparelDetail;
import vn.ptit.ecom.model.product.BookDetail;
import vn.ptit.ecom.model.product.Category;
import vn.ptit.ecom.model.product.DetailKind;
import vn.ptit.ecom.model.product.LaptopDetail;
import vn.ptit.ecom.model.product.PhoneDetail;
import vn.ptit.ecom.model.product.Product;

class ProductDAOImpl implements ProductDAO {

    @FunctionalInterface
    private interface DetailMapper {
        Product map(Product row, ResultSet rs) throws SQLException;
    }

    /** One mapper per subclass (table per subclass): the category's detail kind picks the table and the subclass. */
    private static final Map<DetailKind, DetailMapper> DETAILS = new EnumMap<>(DetailKind.class);

    static {
        DETAILS.put(DetailKind.BOOK, (row, rs) -> new BookDetail(row, rs.getString("Author"), rs.getString("Publisher"),
                Jdbc.intOrNull(rs, "Pages"), rs.getString("Language")));
        DETAILS.put(DetailKind.LAPTOP, (row, rs) -> new LaptopDetail(row, rs.getString("Cpu"), rs.getInt("RamGb"),
                rs.getInt("StorageGb"), rs.getDouble("ScreenInch"), rs.getInt("WarrantyMonths")));
        DETAILS.put(DetailKind.PHONE, (row, rs) -> new PhoneDetail(row, rs.getString("Os"), rs.getInt("StorageGb"),
                Jdbc.intOrNull(rs, "CameraMp"), rs.getDouble("ScreenInch"), Jdbc.intOrNull(rs, "BatteryMah"),
                rs.getInt("WarrantyMonths")));
        DETAILS.put(DetailKind.APPAREL, (row, rs) -> new ApparelDetail(row, rs.getString("SizeLabel"),
                rs.getString("Color"), rs.getString("Material")));
    }

    private static final String SELECT = "SELECT p.*, c.ParentId, c.Name AS category_name, c.Slug, c.DetailKind "
            + "FROM Product p JOIN Category c ON c.CategoryId = p.CategoryId ";

    private final Connection connection;

    ProductDAOImpl(Connection connection) {
        this.connection = connection;
    }

    @Override
    public List<Category> categories() throws SQLException {
        List<Category> out = new ArrayList<>();
        try (PreparedStatement ps = connection.prepareStatement("SELECT * FROM Category ORDER BY CategoryId");
             ResultSet rs = ps.executeQuery()) {
            while (rs.next())
                out.add(new Category(rs.getInt("CategoryId"), Jdbc.intOrNull(rs, "ParentId"), rs.getString("Name"),
                        rs.getString("Slug"), kind(rs.getString("DetailKind"))));
        }
        return out;
    }

    @Override
    public List<Product> search(String keyword, String categorySlug, Sort sort) throws SQLException {
        StringBuilder sql = new StringBuilder(SELECT).append("WHERE p.Status = 'ACTIVE' ");
        List<Object> args = new ArrayList<>();
        if (categorySlug != null && !categorySlug.isBlank()) {
            sql.append("AND (c.Slug = ? OR c.ParentId = (SELECT CategoryId FROM Category WHERE Slug = ?)) ");
            args.add(categorySlug);
            args.add(categorySlug);
        }
        String like = null;
        if (keyword != null && !keyword.isBlank()) {
            like = "%" + keyword.trim().toLowerCase() + "%";
            sql.append("AND (lower(p.Name) LIKE ? OR lower(coalesce(p.Brand, '')) LIKE ? OR lower(c.Name) LIKE ?) ");
            args.add(like);
            args.add(like);
            args.add(like);
        }
        switch (sort == null ? Sort.RELEVANCE : sort) {
            case PRICE_ASC -> sql.append("ORDER BY p.Price ASC");
            case PRICE_DESC -> sql.append("ORDER BY p.Price DESC");
            case NEWEST -> sql.append("ORDER BY p.CreatedAt DESC, p.ProductId DESC");
            default -> {
                if (like != null) {
                    sql.append("ORDER BY CASE WHEN lower(p.Name) LIKE ? THEN 0 ELSE 1 END, p.Name");
                    args.add(like);
                } else {
                    sql.append("ORDER BY c.CategoryId, p.ProductId");
                }
            }
        }
        List<Product> rows = new ArrayList<>();
        try (PreparedStatement ps = Jdbc.prepare(connection, sql.toString(), args.toArray()); ResultSet rs = ps.executeQuery()) {
            while (rs.next()) rows.add(map(rs));
        }
        List<Product> out = new ArrayList<>();
        for (Product p : rows) out.add(asSubclass(p));
        return out;
    }

    @Override
    public Optional<Product> findById(int productId) throws SQLException {
        Product row;
        try (PreparedStatement ps = Jdbc.prepare(connection, SELECT + "WHERE p.ProductId = ?", productId);
             ResultSet rs = ps.executeQuery()) {
            if (!rs.next()) return Optional.empty();
            row = map(rs);
        }
        return Optional.of(asSubclass(row));
    }

    @Override
    public Map<Integer, Product> findByIds(Collection<Integer> productIds) throws SQLException {
        Map<Integer, Product> out = new LinkedHashMap<>();
        if (productIds.isEmpty()) return out;
        String marks = String.join(",", java.util.Collections.nCopies(productIds.size(), "?"));
        try (PreparedStatement ps = Jdbc.prepare(connection, SELECT + "WHERE p.ProductId IN (" + marks + ")", productIds.toArray());
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                Product p = map(rs);
                out.put(p.getId(), p);
            }
        }
        return out;
    }

    @Override
    public boolean reserveStock(int productId, int quantity) throws SQLException {
        return Jdbc.update(connection, "UPDATE Product SET StockQuantity = StockQuantity - ? "
                + "WHERE ProductId = ? AND Status = 'ACTIVE' AND StockQuantity >= ?", quantity, productId, quantity) == 1;
    }

    @Override
    public void releaseStock(int productId, int quantity) throws SQLException {
        Jdbc.update(connection, "UPDATE Product SET StockQuantity = StockQuantity + ? WHERE ProductId = ?", quantity, productId);
    }

    @Override
    public void updateStock(int productId, int quantity) throws SQLException {
        Jdbc.update(connection, "UPDATE Product SET StockQuantity = ? WHERE ProductId = ?", quantity, productId);
    }

    @Override
    public List<Product> listForStock() throws SQLException {
        List<Product> out = new ArrayList<>();
        try (PreparedStatement ps = connection.prepareStatement(SELECT + "ORDER BY p.StockQuantity, p.Name");
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) out.add(map(rs));
        }
        return out;
    }

    /** The product row joined with the row of its detail table, as an object of its subclass (catalogue sizes are
     * small, one query per product is fine). Without a detail kind or a detail row it stays a plain Product. */
    private Product asSubclass(Product row) throws SQLException {
        DetailKind kind = row.getCategory().detailKind();
        if (kind == null) return row;
        try (PreparedStatement ps = Jdbc.prepare(connection, "SELECT * FROM " + kind.table() + " WHERE ProductId = ?", row.getId());
             ResultSet rs = ps.executeQuery()) {
            return rs.next() ? DETAILS.get(kind).map(row, rs) : row;
        }
    }

    static Product map(ResultSet rs) throws SQLException {
        Category category = new Category(rs.getInt("CategoryId"), Jdbc.intOrNull(rs, "ParentId"),
                rs.getString("category_name"), rs.getString("Slug"), kind(rs.getString("DetailKind")));
        return new Product(rs.getInt("ProductId"), rs.getString("Sku"), rs.getString("Name"), rs.getString("Brand"),
                rs.getLong("Price"), rs.getInt("StockQuantity"), rs.getString("Description"), rs.getString("ImageFile"),
                Product.Status.valueOf(rs.getString("Status")), category);
    }

    private static DetailKind kind(String s) {
        return s == null ? null : DetailKind.valueOf(s);
    }
}
