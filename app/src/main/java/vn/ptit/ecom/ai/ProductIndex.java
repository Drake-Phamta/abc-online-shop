package vn.ptit.ecom.ai;

import java.text.NumberFormat;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * FR-S2, FR-S3: the text side of the AI search. Every ACTIVE product is a vector of its words; a word weighs more in
 * the name than in the description, and less when many products use it (TF-IDF, weights learned from the catalogue).
 * A query is a vector of its terms plus, at half weight, their related words; the score is the cosine of the two.
 */
public class ProductIndex {
    static final double W_NAME = 3.0, W_BRAND = 2.5, W_CATEGORY = 2.0, W_DETAIL = 1.5, W_DESCRIPTION = 1.0;
    static final double RELATED_WEIGHT = 0.5;
    /** Below this score a product shares only a stray word with the query and is not shown. */
    static final double MIN_SCORE = 0.05;

    private record Doc(int productId, long price, Map<String, Double> vector, Map<String, String> fieldOf) { }

    private final List<Doc> docs;
    private final Map<String, Integer> df;
    private final int n;

    private ProductIndex(List<Doc> docs, Map<String, Integer> df) {
        this.docs = docs;
        this.df = df;
        this.n = docs.size();
    }

    /** @param documents the ACTIVE products (AI01) as documents; the category text includes the parent category */
    public static ProductIndex build(List<Document> documents) {
        List<Map<String, Double>> tfs = new ArrayList<>();
        List<Map<String, String>> fields = new ArrayList<>();
        Map<String, Integer> df = new HashMap<>();
        for (Document p : documents) {
            Map<String, Double> tf = new HashMap<>();
            Map<String, String> fieldOf = new HashMap<>();
            Map<String, Double> best = new HashMap<>();
            add(tf, fieldOf, best, p.name(), W_NAME, "name");
            add(tf, fieldOf, best, p.brand(), W_BRAND, "brand");
            add(tf, fieldOf, best, p.category(), W_CATEGORY, "category");
            p.details().forEach((label, value) -> add(tf, fieldOf, best, value, W_DETAIL, label.toLowerCase(Locale.ROOT)));
            add(tf, fieldOf, best, p.description(), W_DESCRIPTION, "description");
            for (String t : tf.keySet()) df.merge(t, 1, Integer::sum);
            tfs.add(tf);
            fields.add(fieldOf);
        }
        int n = documents.size();
        List<Doc> docs = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            Map<String, Double> v = new HashMap<>();
            for (Map.Entry<String, Double> e : tfs.get(i).entrySet())
                v.put(e.getKey(), (1 + Math.log(e.getValue())) * idf(n, df.get(e.getKey())));
            normalize(v);
            docs.add(new Doc(documents.get(i).id(), documents.get(i).price(), v, fields.get(i)));
        }
        return new ProductIndex(docs, df);
    }

    private static void add(Map<String, Double> tf, Map<String, String> fieldOf, Map<String, Double> best,
                            String text, double weight, String field) {
        for (String t : QueryInterpreter.tokens(text)) {
            tf.merge(t, weight, Double::sum);
            if (weight > best.getOrDefault(t, 0.0)) {
                best.put(t, weight);
                fieldOf.put(t, field);
            }
        }
    }

    private static double idf(int n, int df) {
        return Math.log(1.0 + (double) n / df);
    }

    private static void normalize(Map<String, Double> v) {
        double norm = Math.sqrt(v.values().stream().mapToDouble(x -> x * x).sum());
        if (norm > 0) v.replaceAll((k, x) -> x / norm);
    }

    /** Catalogue word -> number of products that use it (for the spelling correction of the QueryInterpreter). */
    public Map<String, Integer> vocabulary() {
        return Map.copyOf(df);
    }

    /** Up to k products, best first; ties keep the product id order, so the same query always ranks the same. */
    public List<Hit> rank(SearchQuery q, int k) {
        Map<String, Double> qv = new LinkedHashMap<>();
        Map<String, String> via = new HashMap<>();
        for (String t : q.terms()) if (df.containsKey(t)) qv.put(t, idf(n, df.get(t)));
        q.related().forEach((t, rels) -> {
            // weighted by the customer's word, not by the related word: a rare related word ("burgundy") must not
            // outweigh the word the customer typed ("red")
            double weight = RELATED_WEIGHT * idf(n, df.getOrDefault(t, 1));
            for (String r : rels)
                if (df.containsKey(r) && !qv.containsKey(r)) {
                    qv.put(r, weight);
                    via.put(r, t);
                }
        });
        normalize(qv);
        String priceReason = priceReason(q);
        List<Doc> candidates = docs.stream()
                .filter(d -> (q.minPrice() == null || d.price() >= q.minPrice()) && (q.maxPrice() == null || d.price() <= q.maxPrice()))
                .toList();
        List<Hit> hits = new ArrayList<>();
        if (qv.isEmpty()) {
            // only a price limit ("under 2 million"): every product in the range, cheapest first
            if (priceReason == null || !q.terms().isEmpty()) return hits;
            candidates.stream().sorted(Comparator.comparingLong(Doc::price).thenComparingInt(Doc::productId)).limit(k)
                    .forEach(d -> hits.add(new Hit(d.productId(), 1.0, List.of(priceReason))));
            return hits;
        }
        long maxPrice = candidates.stream().mapToLong(Doc::price).max().orElse(1);
        for (Doc d : candidates) {
            // a related word stands in for its query term, it does not add to it: per query term the best of the
            // term and its related words counts ("red sneakers": red canvas shoes beat burgundy boots)
            Map<String, Double> best = new HashMap<>();
            Map<String, String> bestWord = new HashMap<>();
            for (Map.Entry<String, Double> e : qv.entrySet()) {
                Double w = d.vector().get(e.getKey());
                if (w == null) continue;
                String origin = via.getOrDefault(e.getKey(), e.getKey());
                double part = e.getValue() * w;
                if (part > best.getOrDefault(origin, 0.0)) {
                    best.put(origin, part);
                    bestWord.put(origin, e.getKey());
                }
            }
            double score = best.values().stream().mapToDouble(Double::doubleValue).sum();
            if (score < MIN_SCORE) continue;
            if (q.cheap()) score *= 1 + 0.25 * (1 - (double) d.price() / maxPrice);
            List<String> reasons = new ArrayList<>();
            best.entrySet().stream().sorted(Map.Entry.<String, Double>comparingByValue().reversed()).limit(3).forEach(e -> {
                String word = bestWord.get(e.getKey());
                String field = d.fieldOf().get(word);
                reasons.add(field + ": “" + word + "”" + (word.equals(e.getKey()) ? "" : " (related to “" + e.getKey() + "”)"));
            });
            if (priceReason != null) reasons.add(priceReason);
            if (q.cheap()) reasons.add("cheaper products ranked higher");
            hits.add(new Hit(d.productId(), Math.round(score * 1000) / 1000.0, reasons));
        }
        hits.sort(Comparator.comparingDouble(Hit::score).reversed().thenComparingInt(Hit::productId));
        return hits.size() > k ? new ArrayList<>(hits.subList(0, k)) : hits;
    }

    private static String priceReason(SearchQuery q) {
        NumberFormat f = NumberFormat.getIntegerInstance(Locale.forLanguageTag("vi-VN"));
        if (q.minPrice() != null && q.maxPrice() != null) return "price between " + f.format(q.minPrice()) + " and " + f.format(q.maxPrice()) + " ₫";
        if (q.maxPrice() != null) return "price at most " + f.format(q.maxPrice()) + " ₫";
        if (q.minPrice() != null) return "price at least " + f.format(q.minPrice()) + " ₫";
        return null;
    }
}
