package vn.ptit.ecom.model.customer;

public record FullName(String firstName, String middleName, String lastName) {

    /** Vietnamese order: last name, middle name, first name ("Nguyễn Văn An"). */
    public String display() {
        return middleName == null || middleName.isBlank()
                ? lastName + " " + firstName
                : lastName + " " + middleName + " " + firstName;
    }
}
