package __Design.vn.ptit.ecom.dao;

public class Database {
	private Path file;

	public T inTransaction(Work<T> work) {
		throw new UnsupportedOperationException();
	}

	public void create(boolean replaceExisting) {
		throw new UnsupportedOperationException();
	}

	public Path getFile() {
		return this.file;
	}
}