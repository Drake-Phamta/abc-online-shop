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
        DETAILS.put(DetailKind.BOOK, (row, rs) -> new BookDetail(row, rs.getString("author"), rs.getString("publisher"),
                Jdbc.intOrNull(rs, "pages"), rs.getString("language")));
        DETAILS.put(DetailKind.LAPTOP, (row, rs) -> new LaptopDetail(row, rs.getString("cpu"), rs.getInt("ram_gb"),
                rs.getInt("storage_gb"), rs.getDouble("screen_inch"), rs.getInt("warranty_months")));
        DETAILS.put(DetailKind.PHONE, (row, rs) -> new PhoneDetail(row, rs.getString("os"), rs.getInt("storage_gb"),
                Jdbc.intOrNull(rs, "camera_mp"), rs.getDouble("screen_inch"), Jdbc.intOrNull(rs, "battery_mah"),
                rs.getInt("warranty_months")));
        DETAILS.put(DetailKind.APPAREL, (row, rs) -> new ApparelDetail(row, rs.getString("size_label"),
                rs.getString("color"), rs.getString("material")));
    }

    private static final String SELECT = "SELECT p.*, c.parent_id, c.name AS category_name, c.slug, c.detail_kind "
            + "FROM product p JOIN category c ON c.category_id = p.category_id ";

    private final Connection connection;

    ProductDAOImpl(Connection connection) {
        this.connection = connection;
    }

    @Override
    public List<Category> categories() throws SQLException {
        List<Category> out = new ArrayList<>();
        try (PreparedStatement ps = connection.prepareStatement("SELECT * FROM category ORDER BY category_id");
             ResultSet rs = ps.executeQuery()) {
            while (rs.next())
                out.add(new Category(rs.getInt("category_id"), Jdbc.intOrNull(rs, "parent_id"), rs.getString("name"),
                        rs.getString("slug"), kind(rs.getString("detail_kind"))));
        }
        return out;
    }

    @Override
    public List<Product> search(String keyword, String categorySlug, Sort sort) throws SQLException {
        StringBuilder sql = new StringBuilder(SELECT).append("WHERE p.status = 'ACTIVE' ");
        List<Object> args = new ArrayList<>();
        if (categorySlug != null && !categorySlug.isBlank()) {
            sql.append("AND (c.slug = ? OR c.parent_id = (SELECT category_id FROM category WHERE slug = ?)) ");
            args.add(categorySlug);
            args.add(categorySlug);
        }
        String like = null;
        if (keyword != null && !keyword.isBlank()) {
            like = "%" + keyword.trim().toLowerCase() + "%";
            sql.append("AND (lower(p.name) LIKE ? OR lower(coalesce(p.brand, '')) LIKE ? OR lower(c.name) LIKE ?) ");
            args.add(like);
            args.add(like);
            args.add(like);
        }
        switch (sort == null ? Sort.RELEVANCE : sort) {
            case PRICE_ASC -> sql.append("ORDER BY p.price ASC");
            case PRICE_DESC -> sql.append("ORDER BY p.price DESC");
            case NEWEST -> sql.append("ORDER BY p.created_at DESC, p.product_id DESC");
            default -> {
                if (like != null) {
                    sql.append("ORDER BY CASE WHEN lower(p.name) LIKE ? THEN 0 ELSE 1 END, p.name");
                    args.add(like);
                } else {
                    sql.append("ORDER BY c.category_id, p.product_id");
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
        try (PreparedStatement ps = Jdbc.prepare(connection, SELECT + "WHERE p.product_id = ?", productId);
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
        try (PreparedStatement ps = Jdbc.prepare(connection, SELECT + "WHERE p.product_id IN (" + marks + ")", productIds.toArray());
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
        return Jdbc.update(connection, "UPDATE product SET stock_quantity = stock_quantity - ? "
                + "WHERE product_id = ? AND status = 'ACTIVE' AND stock_quantity >= ?", quantity, productId, quantity) == 1;
    }

    @Override
    public void releaseStock(int productId, int quantity) throws SQLException {
        Jdbc.update(connection, "UPDATE product SET stock_quantity = stock_quantity + ? WHERE product_id = ?", quantity, productId);
    }

    @Override
    public void updateStock(int productId, int quantity) throws SQLException {
        Jdbc.update(connection, "UPDATE product SET stock_quantity = ? WHERE product_id = ?", quantity, productId);
    }

    @Override
    public List<Product> listForStock() throws SQLException {
        List<Product> out = new ArrayList<>();
        try (PreparedStatement ps = connection.prepareStatement(SELECT + "ORDER BY p.stock_quantity, p.name");
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
        try (PreparedStatement ps = Jdbc.prepare(connection, "SELECT * FROM " + kind.table() + " WHERE product_id = ?", row.getId());
             ResultSet rs = ps.executeQuery()) {
            return rs.next() ? DETAILS.get(kind).map(row, rs) : row;
        }
    }

    static Product map(ResultSet rs) throws SQLException {
        Category category = new Category(rs.getInt("category_id"), Jdbc.intOrNull(rs, "parent_id"),
                rs.getString("category_name"), rs.getString("slug"), kind(rs.getString("detail_kind")));
        return new Product(rs.getInt("product_id"), rs.getString("sku"), rs.getString("name"), rs.getString("brand"),
                rs.getLong("price"), rs.getInt("stock_quantity"), rs.getString("description"), rs.getString("image_file"),
                Product.Status.valueOf(rs.getString("status")), category);
    }

    private static DetailKind kind(String s) {
        return s == null ? null : DetailKind.valueOf(s);
    }
}
