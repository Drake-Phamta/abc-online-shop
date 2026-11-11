package vn.ptit.ecom.ai;

import java.util.Map;

/**
 * A product as the AI search sees it: words and a price, no domain behaviour. The AI component depends on nothing
 * else in the application; the SearchService turns the catalogue into documents.
 *
 * @param details label -> value of the detail attributes ("colour" -> "Red", "author" -> "George Orwell")
 */
public record Document(int id, long price, String name, String brand, String category, Map<String, String> details,
                       String description) { }
