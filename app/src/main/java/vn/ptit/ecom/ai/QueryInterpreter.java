package vn.ptit.ecom.ai;

import java.text.Normalizer;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * FR-S1: turns the customer's words into a {@link SearchQuery}. Price limits become filters (AI03), words of the
 * shop's lexicon bring their related words, and a word the catalogue does not know is corrected to the closest
 * catalogue word. The same text and vocabulary always give the same query.
 */
public class QueryInterpreter {
    /** AI06. */
    public static final int MAX_LENGTH = 200;

    /**
     * The shop's lexicon, kept by the sales staff (SPEC section 6). SYNONYMS are words for the same thing; BROADER
     * links a kind to its general word (a sneaker is a shoe, a boot is a shoe, but a boot is not a sneaker).
     */
    static final String[][] SYNONYMS = {
            {"laptop", "notebook", "ultrabook"},
            {"smartphone", "phone", "mobile", "cellphone"},
            {"sneaker", "trainer"},
            {"shoe", "footwear"},
            {"sweater", "jumper", "pullover", "knitwear"},
            {"jacket", "coat"},
            {"jean", "denim"},
            {"trouser", "pant"},
            {"shirt", "tee"},
            {"book", "paperback", "hardcover"},
            {"fiction", "novel", "story", "literature"},
            {"programming", "programmer", "coding", "code", "software", "developer", "computing", "algorithm"},
            {"business", "startup", "entrepreneur", "management", "company"},
            {"camera", "photo", "photography"},
    };
    static final String[][] BROADER = {
            {"sneaker", "shoe"}, {"trainer", "shoe"}, {"boot", "shoe"}, {"polo", "shirt"}, {"jean", "trouser"},
            {"burgundy", "red"}, {"crimson", "red"}, {"maroon", "red"}, {"indigo", "blue"}, {"navy", "blue"},
    };

    /** Vietnamese words (accents removed) for the same products; longest phrase first. Part of the lexicon. */
    static final String[][] VIETNAMESE = {
            {"may tinh xach tay", "laptop"}, {"dien thoai", "smartphone"}, {"may tinh", "laptop"}, {"ao khoac", "jacket"},
            {"ao len", "sweater"}, {"quan jean", "jean"}, {"quan bo", "jean"}, {"tieu thuyet", "novel"},
            {"chien tranh", "war"}, {"lap trinh", "programming"}, {"kinh doanh", "business"}, {"gia re", "cheap"},
            {"mau do", "red"}, {"mau xanh", "blue"}, {"mau den", "black"}, {"mau trang", "white"},
            {"giay", "shoe"}, {"sach", "book"}, {"ao", "shirt"},
    };

    static final Set<String> STOP = Set.of("a", "an", "the", "for", "of", "to", "with", "and", "or", "in", "on", "by",
            "my", "me", "i", "want", "need", "looking", "look", "show", "find", "search", "some", "any", "about", "please",
            "that", "this", "is", "are", "be", "it", "something", "buy", "good", "nice", "like", "who", "which", "what");

    static final Set<String> CHEAP = Set.of("cheap", "cheapest", "budget", "affordable", "inexpensive");

    private static final String AMOUNT = "(\\d+(?:[.,]\\d+)*)\\s*(k|nghin|ngan|thousand|tr|trieu|m|mil|million|millions|vnd|dong|d)?\\b";
    private static final Pattern BETWEEN = Pattern.compile("\\bbetween\\s+" + AMOUNT + "\\s+(?:and|to)\\s+" + AMOUNT);
    private static final Pattern MAX = Pattern.compile("(?:\\b(?:under|below|less than|cheaper than|up to|at most|max|maximum|within|duoi)|<=?)\\s*" + AMOUNT);
    private static final Pattern MIN = Pattern.compile("(?:\\b(?:over|above|more than|at least|from|min|minimum|tren)|>=?)\\s*" + AMOUNT);

    private static final Map<String, Set<String>> RELATED = new HashMap<>();
    static {
        for (String[] group : SYNONYMS)
            for (String w : group)
                for (String r : group)
                    if (!w.equals(r)) RELATED.computeIfAbsent(stem(w), k -> new TreeSet<>()).add(stem(r));
        for (String[] pair : BROADER) {   // both ways: "shoes" also finds boots, "boots" also finds other shoes
            RELATED.computeIfAbsent(stem(pair[0]), k -> new TreeSet<>()).add(stem(pair[1]));
            RELATED.computeIfAbsent(stem(pair[1]), k -> new TreeSet<>()).add(stem(pair[0]));
        }
    }

    /** Catalogue word -> number of products that use it (from the index). */
    private final Map<String, Integer> vocabulary;

    public QueryInterpreter(Map<String, Integer> vocabulary) {
        this.vocabulary = vocabulary;
    }

    public SearchQuery interpret(String text) {
        String original = text == null ? "" : text.trim();
        if (original.length() > MAX_LENGTH) throw new IllegalArgumentException("A search can have at most " + MAX_LENGTH + " characters.");
        String s = " " + normalize(original) + " ";
        for (String[] vi : VIETNAMESE) s = s.replace(" " + vi[0] + " ", " " + vi[1] + " ");
        Long min = null, max = null;
        Matcher m = BETWEEN.matcher(s);
        if (m.find()) {
            min = amount(m.group(1), m.group(2));
            max = amount(m.group(3), m.group(4) != null ? m.group(4) : m.group(2));
            s = s.substring(0, m.start()) + " " + s.substring(m.end());
        }
        m = MAX.matcher(s);
        if (m.find()) {
            max = amount(m.group(1), m.group(2));
            s = s.substring(0, m.start()) + " " + s.substring(m.end());
        }
        m = MIN.matcher(s);
        if (m.find()) {
            min = amount(m.group(1), m.group(2));
            s = s.substring(0, m.start()) + " " + s.substring(m.end());
        }
        boolean cheap = false;
        List<String> terms = new ArrayList<>();
        Map<String, String> corrections = new LinkedHashMap<>();
        for (String raw : s.split("[^a-z0-9]+")) {
            if (raw.isEmpty() || STOP.contains(raw)) continue;
            if (CHEAP.contains(raw)) { cheap = true; continue; }
            String t = stem(raw);
            if (!known(t) && !t.chars().allMatch(Character::isDigit)) {
                String c = correct(t);
                if (c != null) {
                    corrections.put(raw, c);
                    t = c;
                }
            }
            if (!terms.contains(t)) terms.add(t);
        }
        Map<String, List<String>> related = new LinkedHashMap<>();
        for (String t : terms) {
            List<String> rel = RELATED.getOrDefault(t, Set.of()).stream()
                    .filter(r -> vocabulary.containsKey(r) && !terms.contains(r)).toList();
            if (!rel.isEmpty()) related.put(t, rel);
        }
        return new SearchQuery(original, List.copyOf(terms), related, corrections, min, max, cheap);
    }

    /**
     * Lower case, no accents (Vietnamese queries work with or without diacritics), no apostrophes ("Levi's" = "levis"),
     * letters and digits apart ("16gb" = "16 gb", as the catalogue writes "16 GB").
     */
    static String normalize(String text) {
        String s = Normalizer.normalize(text.toLowerCase().replace('đ', 'd'), Normalizer.Form.NFD).replaceAll("\\p{M}+", "");
        s = s.replace("'", "").replace("’", "");
        return s.replaceAll("(?<=[a-z])(?=\\d)|(?<=\\d)(?=[a-z])", " ");
    }

    /** The words of a text as the index stores them; the index and the query use the same function. */
    public static List<String> tokens(String text) {
        List<String> out = new ArrayList<>();
        if (text == null) return out;
        for (String raw : normalize(text).split("[^a-z0-9]+"))
            if (!raw.isEmpty() && !STOP.contains(raw)) out.add(stem(raw));
        return out;
    }

    /** Plural to singular, enough for product words: sneakers, laptops, stories. Numbers stay as they are. */
    static String stem(String w) {
        if (w.length() > 4 && w.endsWith("ies")) return w.substring(0, w.length() - 3) + "y";
        if (w.length() > 3 && w.endsWith("s") && !w.endsWith("ss") && !w.endsWith("us") && !w.endsWith("is")
                && !Character.isDigit(w.charAt(0))) return w.substring(0, w.length() - 1);
        return w;
    }

    private boolean known(String t) {
        return vocabulary.containsKey(t) || RELATED.containsKey(t);
    }

    /**
     * The catalogue or lexicon word closest to a word nobody uses: one edit for words of 5 to 7 letters, two from 8.
     * Shorter words are left alone: "dien" is one edit away from too many words to guess.
     */
    private String correct(String t) {
        if (t.length() < 5) return null;
        int limit = t.length() <= 7 ? 1 : 2;
        Comparator<String> better = Comparator.<String>comparingInt(c -> distance(t, c))
                .thenComparing(c -> -vocabulary.getOrDefault(c, 0)).thenComparing(c -> c);
        String best = null;
        for (String c : candidates()) {
            if (Math.abs(c.length() - t.length()) > limit || c.chars().allMatch(Character::isDigit)) continue;
            if (distance(t, c) <= limit && (best == null || better.compare(c, best) < 0)) best = c;
        }
        return best;
    }

    private Set<String> candidates() {
        Set<String> all = new TreeSet<>(vocabulary.keySet());
        all.addAll(RELATED.keySet());
        return all;
    }

    /** Damerau-Levenshtein distance (a swap of two neighbouring letters counts as one edit). */
    static int distance(String a, String b) {
        int[][] d = new int[a.length() + 1][b.length() + 1];
        for (int i = 0; i <= a.length(); i++) d[i][0] = i;
        for (int j = 0; j <= b.length(); j++) d[0][j] = j;
        for (int i = 1; i <= a.length(); i++)
            for (int j = 1; j <= b.length(); j++) {
                int cost = a.charAt(i - 1) == b.charAt(j - 1) ? 0 : 1;
                d[i][j] = Math.min(Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1), d[i - 1][j - 1] + cost);
                if (i > 1 && j > 1 && a.charAt(i - 1) == b.charAt(j - 2) && a.charAt(i - 2) == b.charAt(j - 1))
                    d[i][j] = Math.min(d[i][j], d[i - 2][j - 2] + 1);
            }
        return d[a.length()][b.length()];
    }

    /**
     * "10 million", "10tr", "500k", "1.5m", "2.000.000 vnd". A bare number after a price word is read as millions up to
     * 100 ("under 10") and as thousands above ("under 500"); a bare number elsewhere stays a search term ("501").
     */
    static long amount(String number, String unit) {
        double v = number.matches("\\d{1,3}([.,]\\d{3})+") ? Double.parseDouble(number.replaceAll("[.,]", ""))
                : Double.parseDouble(number.replace(',', '.'));
        String u = unit == null ? "" : unit;
        switch (u) {
            case "k", "nghin", "ngan", "thousand" -> v *= 1_000;
            case "tr", "trieu", "m", "mil", "million", "millions" -> v *= 1_000_000;
            case "" -> { if (v < 1000) v *= v <= 100 ? 1_000_000 : 1_000; }
            default -> { }
        }
        return Math.round(v);
    }
}
