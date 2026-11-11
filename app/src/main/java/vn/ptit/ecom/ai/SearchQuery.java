package vn.ptit.ecom.ai;

import java.util.List;
import java.util.Map;

/**
 * What the AI search understood from the customer's words (FR-S1, shown to the customer by AI02).
 *
 * @param text        the query as typed or spoken
 * @param terms       normalized search terms after spelling correction
 * @param related     for a term, the related words of the shop's lexicon that the catalogue uses
 * @param corrections misspelled word to the catalogue word it was corrected to
 * @param minPrice    lower price limit in VND, or null
 * @param maxPrice    upper price limit in VND, or null (AI03: a hard filter)
 * @param cheap       the customer asked for something cheap: lower prices rank higher
 */
public record SearchQuery(String text, List<String> terms, Map<String, List<String>> related,
                          Map<String, String> corrections, Long minPrice, Long maxPrice, boolean cheap) {

    public boolean isEmpty() {
        return terms.isEmpty() && minPrice == null && maxPrice == null;
    }
}
