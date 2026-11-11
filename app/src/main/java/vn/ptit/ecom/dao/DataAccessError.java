package vn.ptit.ecom.dao;

/** An unexpected database failure (not a business rule); reported as a server error. */
public class DataAccessError extends RuntimeException {
    public DataAccessError(Throwable cause) {
        super(cause.getMessage(), cause);
    }
}
