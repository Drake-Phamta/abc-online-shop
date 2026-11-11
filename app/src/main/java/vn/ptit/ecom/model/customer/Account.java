package vn.ptit.ecom.model.customer;

/** Login data of a customer or a staff member; the hash never leaves the server. */
public record Account(Role role, int id, String displayName, String passwordHash) { }
