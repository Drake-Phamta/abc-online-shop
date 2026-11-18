package __Design.vn.ptit.ecom.dao;

public class Database {
	private Path _file;

	public T inTransaction(Work<T> aWork) {
		throw new UnsupportedOperationException();
	}

	public void create(boolean aReplaceExisting) {
		throw new UnsupportedOperationException();
	}

	public Path getFile() {
		return this._file;
	}
}