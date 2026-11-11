package vn.ptit.ecom.model.customer;

public record Address(int id, int customerId, String recipientName, String phone, String houseNumber, String street,
                      String district, String city, boolean isDefault) {

    public String oneLine() {
        String head = houseNumber == null || houseNumber.isBlank() ? street : houseNumber + " " + street;
        return head + ", " + district + ", " + city;
    }
}
