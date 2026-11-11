package vn.ptit.ecom.ai;

import java.util.List;

/** One ranked product of the AI search: its relevance score and why it matched (AI02). */
public record Hit(int productId, double score, List<String> reasons) { }
