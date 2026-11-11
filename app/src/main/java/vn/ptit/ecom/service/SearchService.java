package vn.ptit.ecom.service;

import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;
import javax.imageio.ImageIO;
import org.springframework.stereotype.Service;
import vn.ptit.ecom.ai.Document;
import vn.ptit.ecom.ai.Hit;
import vn.ptit.ecom.ai.ImageIndex;
import vn.ptit.ecom.ai.ProductIndex;
import vn.ptit.ecom.ai.QueryInterpreter;
import vn.ptit.ecom.ai.SearchQuery;
import vn.ptit.ecom.dao.Database;
import vn.ptit.ecom.dao.ProductDAO;
import vn.ptit.ecom.model.product.Category;
import vn.ptit.ecom.model.product.Product;
import vn.ptit.ecom.model.product.ProductDetail;

/**
 * UC04 with the AI search of docs/SPEC.md section 6: text (typed or spoken) and photo queries. The indexes are built
 * from the catalogue when the first search runs and again whenever the catalogue changed (FR-S7); the products of a
 * result are always read fresh, so prices and stock are current.
 */
@Service
public class SearchService {
    public static final int TOP_K = 12;
    /** A photo shows one product: six look-alikes are enough, more would be noise. */
    public static final int TOP_K_PHOTO = 6;
    /** AI06. */
    public static final int MAX_PHOTO_BYTES = 5 * 1024 * 1024;

    public enum Mode { TEXT, PHOTO, KEYWORD }

    public record Item(Product product, double score, List<String> reasons) { }

    /** fallback = the AI search found nothing and the keyword search produced the items (AI04). */
    public record SearchResult(Mode mode, SearchQuery understood, List<Item> items, boolean fallback, long tookMs) { }

    private record Indexes(String catalogue, ProductIndex text, ImageIndex images, QueryInterpreter interpreter) { }

    private final Database db;
    private volatile Indexes indexes;

    public SearchService(Database db) {
        this.db = db;
    }

    /** Builds the indexes once the application is up, so the first customer does not wait for it. */
    @org.springframework.context.event.EventListener(org.springframework.boot.context.event.ApplicationReadyEvent.class)
    public void warmUp() {
        indexes(activeProducts());
    }

    /** FR-S1, FR-S2, FR-S3, FR-S6. */
    public SearchResult search(String text) {
        long t0 = System.nanoTime();
        if (text == null || text.isBlank()) throw new IllegalArgumentException("Type what you are looking for.");
        List<Product> active = activeProducts();
        Indexes ix = indexes(active);
        SearchQuery q = ix.interpreter().interpret(text);
        List<Hit> hits = ix.text().rank(q, TOP_K);
        if (!hits.isEmpty()) return new SearchResult(Mode.TEXT, q, items(hits, active, true), false, ms(t0));
        // AI04: nothing understood or nothing close enough, the keyword search of UC04 has the last word
        List<Item> keyword = db.inTransaction(d -> d.products().search(text.trim(), null, ProductDAO.Sort.RELEVANCE)).stream()
                .limit(TOP_K).map(p -> new Item(p, 0, List.of("keyword match in name, brand or category"))).toList();
        return new SearchResult(Mode.KEYWORD, q, keyword, true, ms(t0));
    }

    /** FR-S5; AI05: the photo is decoded in memory and dropped after the search. */
    public SearchResult searchByPhoto(byte[] photo) {
        long t0 = System.nanoTime();
        if (photo == null || photo.length == 0) throw new IllegalArgumentException("Choose a photo first.");
        if (photo.length > MAX_PHOTO_BYTES) throw new IllegalArgumentException("The photo is larger than 5 MB.");
        if (!isJpeg(photo) && !isPng(photo)) throw new IllegalArgumentException("The file is not a JPEG or PNG image.");
        BufferedImage img;
        try {
            img = ImageIO.read(new ByteArrayInputStream(photo));
        } catch (IOException e) {
            img = null;
        }
        if (img == null) throw new IllegalArgumentException("The file is not a JPEG or PNG image.");
        List<Product> active = activeProducts();
        Indexes ix = indexes(active);
        List<Hit> hits = ix.images().rank(img, TOP_K_PHOTO);
        SearchQuery none = new SearchQuery("", List.of(), Map.of(), Map.of(), null, null, false);
        return new SearchResult(Mode.PHOTO, none, items(hits, active, false), false, ms(t0));
    }

    private List<Product> activeProducts() {
        return db.inTransaction(d -> d.products().search(null, null, ProductDAO.Sort.RELEVANCE));
    }

    /** AI07: in a text search an out-of-stock product counts 20 % less, so it stays in front only when clearly more relevant. */
    static final double OUT_OF_STOCK_FACTOR = 0.8;

    private static List<Item> items(List<Hit> hits, List<Product> active, boolean stockMatters) {
        Map<Integer, Product> byId = active.stream().collect(Collectors.toMap(Product::getId, Function.identity()));
        List<Item> out = new ArrayList<>();
        for (Hit h : hits) {
            Product p = byId.get(h.productId());
            if (p == null) continue;   // AI01: hidden since the index was built
            if (!stockMatters || p.getStockQuantity() > 0) {
                out.add(new Item(p, h.score(), h.reasons()));
            } else {
                List<String> reasons = new ArrayList<>(h.reasons());
                reasons.add("out of stock: ranked lower");
                out.add(new Item(p, Math.round(h.score() * OUT_OF_STOCK_FACTOR * 1000) / 1000.0, reasons));
            }
        }
        out.sort(java.util.Comparator.comparingDouble(Item::score).reversed().thenComparingInt(i -> i.product().getId()));
        return out;
    }

    /** The catalogue text in one string; when it differs from the indexed one, the indexes are rebuilt (FR-S7). */
    private Indexes indexes(List<Product> active) {
        String catalogue = active.stream().map(p -> p.getId() + "|" + p.getName() + "|" + p.getImageFile() + "|" + p.getPrice())
                .collect(Collectors.joining("\n"));
        Indexes ix = indexes;
        if (ix != null && ix.catalogue().equals(catalogue)) return ix;
        synchronized (this) {
            if (indexes != null && indexes.catalogue().equals(catalogue)) return indexes;
            Map<Integer, String> names = db.inTransaction(d -> d.products().categories()).stream()
                    .collect(Collectors.toMap(Category::id, Category::name));
            ProductIndex text = ProductIndex.build(active.stream().map(p -> document(p, names)).toList());
            Map<Integer, BufferedImage> pictures = new LinkedHashMap<>();
            for (Product p : active) {
                BufferedImage img = catalogueImage(p.getImageFile());
                if (img != null) pictures.put(p.getId(), img);
            }
            indexes = new Indexes(catalogue, text, ImageIndex.build(pictures), new QueryInterpreter(text.vocabulary()));
            return indexes;
        }
    }

    /** The product as the AI component sees it; the category text carries the parent ("Shoes Fashion"). */
    static Document document(Product p, Map<Integer, String> categoryNames) {
        Integer parent = p.getCategory().parentId();
        String category = p.getCategory().name() + (parent == null ? "" : " " + categoryNames.getOrDefault(parent, ""));
        Map<String, String> details = new LinkedHashMap<>();
        if (p.getDetail() != null) for (ProductDetail.Spec s : p.getDetail().specs()) details.put(s.label(), s.value());
        return new Document(p.getId(), p.getPrice(), p.getName(), p.getBrand(), category, details, p.getDescription());
    }

    private BufferedImage catalogueImage(String file) {
        if (file == null) return null;
        try (InputStream in = SearchService.class.getResourceAsStream("/static/img/products/" + file)) {
            return in == null ? null : ImageIO.read(in);
        } catch (IOException e) {
            return null;
        }
    }

    private static boolean isJpeg(byte[] b) {
        return b.length > 3 && (b[0] & 0xFF) == 0xFF && (b[1] & 0xFF) == 0xD8 && (b[2] & 0xFF) == 0xFF;
    }

    private static boolean isPng(byte[] b) {
        return b.length > 8 && (b[0] & 0xFF) == 0x89 && b[1] == 'P' && b[2] == 'N' && b[3] == 'G';
    }

    private static long ms(long t0) {
        return (System.nanoTime() - t0) / 1_000_000;
    }
}
