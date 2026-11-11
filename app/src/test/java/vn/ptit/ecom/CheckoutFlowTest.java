package vn.ptit.ecom;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import vn.ptit.ecom.dao.Database;

/** The checkout path through controllers, DAOs and the real SQLite schema (docs/SPEC.md AT04, AT06, AT10). */
@SpringBootTest(properties = {"abc.db.file=target/test-db/abc_shop_test.db", "abc.db.reset=true"})
@AutoConfigureMockMvc
@DirtiesContext
class CheckoutFlowTest {
    @Autowired MockMvc mvc;
    @Autowired Database db;
    private final ObjectMapper json = new ObjectMapper();

    /** Login starts a fresh session (protection against session fixation), so the test keeps the new one. */
    private MockHttpSession login(String email) throws Exception {
        MvcResult r = mvc.perform(post("/api/auth/login").contentType(MediaType.APPLICATION_JSON)
                .content("{\"email\":\"" + email + "\",\"password\":\"demo1234\"}")).andExpect(status().isOk()).andReturn();
        return (MockHttpSession) r.getRequest().getSession(false);
    }

    private JsonNode read(MockHttpSession s, String url) throws Exception {
        return json.readTree(mvc.perform(get(url).session(s)).andReturn().getResponse().getContentAsString());
    }

    private int productWithStock(int min) throws Exception {
        for (JsonNode p : read(new MockHttpSession(), "/api/products"))
            if (p.get("stock").asInt() >= min) return p.get("id").asInt();
        throw new IllegalStateException("no product with stock " + min);
    }

    private void setStock(int productId, int quantity) throws SQLException {
        try (Connection c = DriverManager.getConnection("jdbc:sqlite:" + db.getFile().toAbsolutePath());
             Statement s = c.createStatement()) {
            s.executeUpdate("UPDATE product SET stock_quantity = " + quantity + " WHERE product_id = " + productId);
        }
    }

    private int placeCod(MockHttpSession s, int productId) throws Exception {
        mvc.perform(post("/api/cart/items").session(s).contentType(MediaType.APPLICATION_JSON)
                .content("{\"productId\":" + productId + ",\"quantity\":1}")).andExpect(status().isOk());
        JsonNode co = read(s, "/api/checkout");
        return mvc.perform(post("/api/orders").session(s).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"addressId\":" + co.get("addresses").get(0).get("id").asInt()
                                + ",\"paymentMethod\":\"COD\",\"expectedTotal\":" + co.get("totals").get("total").asLong() + "}"))
                .andReturn().getResponse().getStatus();
    }

    @Test
    void lastUnitCanBeSoldOnlyOnce() throws Exception {                 // AT04, BR05
        int pid = productWithStock(3);
        MockHttpSession an = login("an.nguyen@example.com"), lan = login("lan.tran@example.com");
        mvc.perform(post("/api/cart/items").session(an).contentType(MediaType.APPLICATION_JSON)
                .content("{\"productId\":" + pid + ",\"quantity\":1}")).andExpect(status().isOk());
        mvc.perform(post("/api/cart/items").session(lan).contentType(MediaType.APPLICATION_JSON)
                .content("{\"productId\":" + pid + ",\"quantity\":1}")).andExpect(status().isOk());
        setStock(pid, 1);
        JsonNode coAn = read(an, "/api/checkout"), coLan = read(lan, "/api/checkout");
        mvc.perform(post("/api/orders").session(an).contentType(MediaType.APPLICATION_JSON)
                .content("{\"addressId\":" + coAn.get("addresses").get(0).get("id").asInt() + ",\"paymentMethod\":\"COD\"}"))
                .andExpect(status().isOk());
        mvc.perform(post("/api/orders").session(lan).contentType(MediaType.APPLICATION_JSON)
                .content("{\"addressId\":" + coLan.get("addresses").get(0).get("id").asInt() + ",\"paymentMethod\":\"COD\"}"))
                .andExpect(status().isConflict()).andExpect(jsonPath("$.rule").value("BR05"));
        assertEquals(0, read(new MockHttpSession(), "/api/products/" + pid).get("product").get("stock").asInt());
    }

    @Test
    void ordersOfOtherCustomersAreNotFound() throws Exception {          // AT06, BR08
        MockHttpSession an = login("an.nguyen@example.com"), lan = login("lan.tran@example.com");
        assertEquals(200, placeCod(an, productWithStock(2)));
        int orderId = read(an, "/api/orders").get(0).get("id").asInt();
        mvc.perform(get("/api/orders/" + orderId).session(lan)).andExpect(status().isNotFound());
        mvc.perform(get("/api/orders/" + orderId).session(an)).andExpect(status().isOk());
    }

    @Test
    void staffFunctionsNeedTheStaffRole() throws Exception {              // AT10, BR13
        mvc.perform(get("/api/staff/orders")).andExpect(status().isUnauthorized());
        mvc.perform(get("/api/staff/orders").session(login("an.nguyen@example.com"))).andExpect(status().isForbidden());
        mvc.perform(get("/api/staff/stock").session(login("sales@example.com"))).andExpect(status().isForbidden());
        mvc.perform(get("/api/staff/stock").session(login("warehouse@example.com"))).andExpect(status().isOk());
    }

    @Test
    void theDatabaseItselfRefusesNegativeStock() {                        // BR05 in the schema, not only in code
        assertThrows(SQLException.class, () -> setStock(productWithStock(1), -1));
    }

    private void exec(String sql) throws SQLException {
        try (Connection c = DriverManager.getConnection("jdbc:sqlite:" + db.getFile().toAbsolutePath());
             Statement s = c.createStatement()) {
            s.executeUpdate(sql);
        }
    }

    private int stockOf(int productId) throws Exception {
        return read(new MockHttpSession(), "/api/products/" + productId).get("product").get("stock").asInt();
    }

    /**
     * UC07 is one transaction (OrderService.placeOrder): the stock is reserved before the order row is written. When
     * that write fails, the reservation must be rolled back too: same stock, same cart, no new order.
     */
    @Test
    void aFailedOrderWriteRollsBackTheStockReservation() throws Exception {   // BR05, commit / rollback
        MockHttpSession minh = login("minh.le@example.com");
        int pid = productWithStock(3);
        mvc.perform(post("/api/cart/items").session(minh).contentType(MediaType.APPLICATION_JSON)
                .content("{\"productId\":" + pid + ",\"quantity\":2}")).andExpect(status().isOk());
        int stockBefore = stockOf(pid), ordersBefore = read(minh, "/api/orders").size();
        JsonNode co = read(minh, "/api/checkout");
        exec("CREATE TRIGGER test_fail_order BEFORE INSERT ON customer_order BEGIN SELECT RAISE(ABORT, 'simulated failure'); END");
        try {
            mvc.perform(post("/api/orders").session(minh).contentType(MediaType.APPLICATION_JSON)
                    .content("{\"addressId\":" + co.get("addresses").get(0).get("id").asInt() + ",\"paymentMethod\":\"COD\"}"))
                    .andExpect(status().isInternalServerError());
        } finally {
            exec("DROP TRIGGER test_fail_order");
        }
        assertEquals(stockBefore, stockOf(pid));
        assertEquals(2, read(minh, "/api/cart").get("count").asInt());
        assertEquals(ordersBefore, read(minh, "/api/orders").size());
    }
}
