package __Design.vn.ptit.ecom.ai;

public class SearchQuery {
	private String _text;
	private List<String> _terms;
	private Map<String__List<String>> _related;
	private Map<String__String> _corrections;
	private Long _minPrice;
	private Long _maxPrice;
	private boolean _cheap;

	public boolean isEmpty() {
		throw new UnsupportedOperationException();
	}
}