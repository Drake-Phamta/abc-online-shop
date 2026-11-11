package vn.ptit.ecom.service;

/** A requested record does not exist, or the caller may not see it (BR08 reports a foreign order the same way). */
public class NotFound extends RuntimeException {
    public NotFound(String message) {
        super(message);
    }
}
