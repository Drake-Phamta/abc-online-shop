package __Design.vn.ptit.ecom.ai;

public class SearchQuery {
	private String text;
	private List<String> terms;
	private Map<String__List<String>> related;
	private Map<String__String> corrections;
	private Long minPrice;
	private Long maxPrice;
	private boolean cheap;

	public boolean isEmpty() {
		throw new UnsupportedOperationException();
	}
}