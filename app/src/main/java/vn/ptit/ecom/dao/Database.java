package vn.ptit.ecom.dao;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;
import org.sqlite.SQLiteConfig;

/**
 * Opens the SQLite database and runs one unit of work in one transaction. Checkout touches carts, products,
 * orders and payments; running them on one connection makes it all-or-nothing (NFR07, NFR10).
 */
public class Database {

    /** All DAOs of one unit of work, sharing its connection. */
    public record Daos(ProductDAO products, CustomerDAO customers, StaffDAO staff, CartDAO carts, OrderDAO orders,
                       PaymentDAO payments, ShippingDAO shipping) { }

    @FunctionalInterface
    public interface Work<T> {
        T run(Daos daos) throws SQLException;
    }

    private final Path file;

    public Database(Path file) {
        this.file = file;
    }

    public <T> T inTransaction(Work<T> work) {
        try (Connection c = open()) {
            c.setAutoCommit(false);
            try {
                T result = work.run(new Daos(new ProductDAOImpl(c), new CustomerDAOImpl(c), new StaffDAOImpl(c),
                        new CartDAOImpl(c), new OrderDAOImpl(c), new PaymentDAOImpl(c), new ShippingDAOImpl(c)));
                c.commit();
                return result;
            } catch (RuntimeException | SQLException e) {
                c.rollback();
                throw e;
            }
        } catch (SQLException e) {
            throw new DataAccessError(e);
        }
    }

    /** Creates the database from the DDL generated from the physical model (db/schema.sql) and the seed data. */
    public void create(boolean replaceExisting) {
        try {
            if (Files.exists(file) && !replaceExisting) return;
            if (file.getParent() != null) Files.createDirectories(file.getParent());
            Files.deleteIfExists(file);
            try (Connection c = open(); Statement s = c.createStatement()) {
                for (String script : new String[]{"/db/schema.sql", "/db/seed.sql"})
                    for (String sql : statements(resource(script))) s.execute(sql);
            }
        } catch (IOException | SQLException e) {
            throw new DataAccessError(e);
        }
    }

    private Connection open() throws SQLException {
        SQLiteConfig config = new SQLiteConfig();
        config.enforceForeignKeys(true);
        config.setBusyTimeout(5000);
        config.setTransactionMode(SQLiteConfig.TransactionMode.IMMEDIATE);
        return config.createConnection("jdbc:sqlite:" + file.toAbsolutePath());
    }

    private static String resource(String name) throws IOException {
        try (InputStream in = Database.class.getResourceAsStream(name)) {
            if (in == null) throw new IOException("missing resource " + name);
            return new String(in.readAllBytes(), StandardCharsets.UTF_8);
        }
    }

    /** Splits a script on semicolons that end a line; comment lines are dropped. */
    static String[] statements(String script) {
        StringBuilder clean = new StringBuilder();
        for (String line : script.split("\\R")) if (!line.trim().startsWith("--")) clean.append(line).append('\n');
        return java.util.Arrays.stream(clean.toString().split(";\\s*\\n")).map(String::trim).filter(s -> !s.isEmpty())
                .toArray(String[]::new);
    }

    public Path getFile() { return file; }
}
