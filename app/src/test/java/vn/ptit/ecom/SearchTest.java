package vn.ptit.ecom;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import java.awt.image.RescaleOp;
import java.io.ByteArrayOutputStream;
import java.util.ArrayList;
import java.util.List;
import javax.imageio.ImageIO;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.web.servlet.MockMvc;

/** The AI search through the controller on the demo catalogue (docs/SPEC.md AT11 to AT17). */
@SpringBootTest(properties = {"abc.db.file=target/test-db/abc_search_test.db", "abc.db.reset=true"})
@AutoConfigureMockMvc
@DirtiesContext
class SearchTest {
    @Autowired MockMvc mvc;
    private final ObjectMapper json = new ObjectMapper();

    private JsonNode search(String q) throws Exception {
        return json.readTree(mvc.perform(get("/api/search").param("q", q)).andExpect(status().isOk())
                .andReturn().getResponse().getContentAsString(java.nio.charset.StandardCharsets.UTF_8));   // JSON is UTF-8
    }

    private static List<String> skus(JsonNode r) {
        List<String> out = new ArrayList<>();
        for (JsonNode f : r.get("results")) out.add(f.get("product").get("sku").asText());
        return out;
    }

    @Test
    void synonymsAndColourFindTheRedSneakers() throws Exception {   // AT11, AI02
        JsonNode r = search("red sneakers");
        assertEquals("FA-SHO-003", skus(r).get(0));
        assertTrue(r.get("understood").get("related").toString().contains("shoe"));
        assertFalse(r.get("results").get(0).get("reasons").isEmpty());
    }

    @Test
    void misspelledWordIsCorrectedAndShown() throws Exception {   // AT12
        JsonNode r = search("macbok air");
        assertEquals("EL-LAP-001", skus(r).get(0));
        assertEquals("macbok → macbook", r.get("understood").get("corrections").get(0).asText());
    }

    @Test
    void priceLimitIsAHardFilter() throws Exception {   // AT13, AI03
        JsonNode r = search("laptop under 10 million");
        assertEquals(10_000_000L, r.get("understood").get("maxPrice").asLong());
        assertEquals(List.of("EL-LAP-002", "EL-LAP-003"), skus(r).stream().sorted().toList());
        for (JsonNode f : r.get("results")) assertTrue(f.get("product").get("price").asLong() <= 10_000_000L);
    }

    @Test
    void relatedWordsReachTheRightBooks() throws Exception {   // AT14
        List<String> top3 = skus(search("book for a programmer")).subList(0, 3);
        assertTrue(top3.contains("BK-COM-001") && top3.contains("BK-COM-004"), top3.toString());
    }

    @Test
    void outOfStockProductRanksLower() throws Exception {   // AI07: the Dell Latitude of the demo data has no stock
        JsonNode r = search("laptop");
        assertFalse(skus(r).get(0).equals("EL-LAP-003"));
        for (JsonNode f : r.get("results"))
            if (f.get("product").get("stock").asInt() == 0)
                assertTrue(f.get("reasons").toString().contains("out of stock"));
    }

    @Test
    void vietnameseWithoutAccentsWorks() throws Exception {   // FR-S1: "phone under 5 million"
        JsonNode r = search("dien thoai duoi 5 trieu");
        assertEquals(List.of("EL-PHN-004"), skus(r));
    }

    @Test
    void nothingFoundFallsBackToKeywordSearch() throws Exception {   // AT16, AI04
        JsonNode r = search("xyzzy");
        assertTrue(r.get("fallback").asBoolean());
        assertEquals("KEYWORD", r.get("mode").asText());
        assertEquals(0, r.get("results").size());
    }

    @Test
    void tooLongQueryIsRefused() throws Exception {   // AI06
        mvc.perform(get("/api/search").param("q", "x".repeat(201))).andExpect(status().isBadRequest());
    }

    @Test
    void photoOfAProductFindsIt() throws Exception {   // AT15, FR-S5
        BufferedImage shoe = ImageIO.read(getClass().getResourceAsStream("/static/img/products/fa-sho-002.jpg"));
        int w = shoe.getWidth(), h = shoe.getHeight();
        BufferedImage photo = new BufferedImage((int) (w * 0.8), (int) (h * 0.8), BufferedImage.TYPE_INT_RGB);
        Graphics2D g = photo.createGraphics();
        g.drawImage(shoe, -(int) (w * 0.1), -(int) (h * 0.1), null);   // the middle 80 %
        g.dispose();
        photo = new RescaleOp(0.75f, 0, null).filter(photo, null);     // a darker room
        ByteArrayOutputStream jpeg = new ByteArrayOutputStream();
        ImageIO.write(photo, "jpg", jpeg);
        String body = mvc.perform(multipart("/api/search/photo").file(new MockMultipartFile("photo", "shoe.jpg", "image/jpeg", jpeg.toByteArray())))
                .andExpect(status().isOk()).andExpect(jsonPath("$.mode").value("PHOTO")).andReturn().getResponse().getContentAsString();
        assertEquals("FA-SHO-002", skus(json.readTree(body)).get(0));
    }

    @Test
    void aTextFileIsNotAPhoto() throws Exception {   // AT17, AI05, AI06
        mvc.perform(multipart("/api/search/photo").file(new MockMultipartFile("photo", "notes.txt", "text/plain", "hello".getBytes())))
                .andExpect(status().isBadRequest()).andExpect(jsonPath("$.message").value("The file is not a JPEG or PNG image."));
    }
}
