package vn.ptit.ecom.controller;

import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import vn.ptit.ecom.dao.DataAccessError;
import vn.ptit.ecom.model.RuleViolation;
import vn.ptit.ecom.service.NotFound;

/** Maps failures to HTTP answers the views understand: {status, rule?, message, details?}. */
@RestControllerAdvice
class ApiErrors {
    private static final Logger log = LoggerFactory.getLogger(ApiErrors.class);

    static class Unauthorized extends RuntimeException {
        Unauthorized() { this("Please log in first."); }
        Unauthorized(String message) { super(message); }
    }

    static class Forbidden extends RuntimeException {
        Forbidden() { super("Your account cannot use this function."); }
    }

    @ExceptionHandler(RuleViolation.class)
    ResponseEntity<Map<String, Object>> rule(RuleViolation e) {
        return body(HttpStatus.CONFLICT, Map.of("rule", e.getRule(), "message", e.getMessage(), "details", e.getDetails()));
    }

    @ExceptionHandler(IllegalArgumentException.class)
    ResponseEntity<Map<String, Object>> badInput(IllegalArgumentException e) {
        return body(HttpStatus.BAD_REQUEST, Map.of("message", e.getMessage()));
    }

    @ExceptionHandler(org.springframework.web.multipart.MaxUploadSizeExceededException.class)   // AI06
    ResponseEntity<Map<String, Object>> tooLarge(Exception e) {
        return body(HttpStatus.BAD_REQUEST, Map.of("message", "The photo is larger than 5 MB."));
    }

    @ExceptionHandler(NotFound.class)   // vn.ptit.ecom.service.NotFound: decided by the services (missing record, BR08)
    ResponseEntity<Map<String, Object>> notFound(NotFound e) {
        return body(HttpStatus.NOT_FOUND, Map.of("message", e.getMessage()));
    }

    @ExceptionHandler(Unauthorized.class)
    ResponseEntity<Map<String, Object>> unauthorized(Unauthorized e) {
        return body(HttpStatus.UNAUTHORIZED, Map.of("message", e.getMessage()));
    }

    @ExceptionHandler(Forbidden.class)
    ResponseEntity<Map<String, Object>> forbidden(Forbidden e) {
        return body(HttpStatus.FORBIDDEN, Map.of("message", e.getMessage()));
    }

    @ExceptionHandler(DataAccessError.class)
    ResponseEntity<Map<String, Object>> database(DataAccessError e) {
        log.error("database error", e);
        return body(HttpStatus.INTERNAL_SERVER_ERROR, Map.of("message", "The shop could not save your request. Please try again."));
    }

    private static ResponseEntity<Map<String, Object>> body(HttpStatus status, Map<String, Object> fields) {
        Map<String, Object> out = new java.util.LinkedHashMap<>(fields);
        out.put("status", status.value());
        if (out.get("details") instanceof List<?> l && l.isEmpty()) out.remove("details");
        return ResponseEntity.status(status).body(out);
    }
}
