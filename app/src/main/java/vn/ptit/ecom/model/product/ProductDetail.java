package vn.ptit.ecom.model.product;

import java.util.ArrayList;
import java.util.List;

/** Attributes that only one kind of product has; stored in the detail table of its kind. */
public sealed interface ProductDetail
        permits ProductDetail.BookDetail, ProductDetail.LaptopDetail, ProductDetail.PhoneDetail, ProductDetail.ApparelDetail {

    record Spec(String label, String value) { }

    DetailKind kind();

    /** Label and value pairs in display order (UC05). */
    List<Spec> specs();

    record BookDetail(String author, String publisher, Integer pages, String language) implements ProductDetail {
        public DetailKind kind() { return DetailKind.BOOK; }
        public List<Spec> specs() {
            return list(spec("Author", author), spec("Publisher", publisher),
                    spec("Pages", pages == null ? null : pages.toString()), spec("Language", language));
        }
    }

    record LaptopDetail(String cpu, int ramGb, int storageGb, double screenInch, int warrantyMonths) implements ProductDetail {
        public DetailKind kind() { return DetailKind.LAPTOP; }
        public List<Spec> specs() {
            return list(spec("Processor", cpu), spec("Memory", ramGb + " GB"), spec("Storage", storageGb + " GB"),
                    spec("Screen", screenInch + " inch"), spec("Warranty", warrantyMonths + " months"));
        }
    }

    record PhoneDetail(String os, int storageGb, Integer cameraMp, double screenInch, Integer batteryMah,
                       int warrantyMonths) implements ProductDetail {
        public DetailKind kind() { return DetailKind.PHONE; }
        public List<Spec> specs() {
            return list(spec("Operating system", os), spec("Storage", storageGb + " GB"),
                    spec("Main camera", cameraMp == null ? null : cameraMp + " MP"), spec("Screen", screenInch + " inch"),
                    spec("Battery", batteryMah == null ? null : batteryMah + " mAh"), spec("Warranty", warrantyMonths + " months"));
        }
    }

    record ApparelDetail(String sizeLabel, String color, String material) implements ProductDetail {
        public DetailKind kind() { return DetailKind.APPAREL; }
        public List<Spec> specs() {
            return list(spec("Size", sizeLabel), spec("Colour", color), spec("Material", material));
        }
    }

    private static Spec spec(String label, String value) { return value == null ? null : new Spec(label, value); }

    private static List<Spec> list(Spec... specs) {
        List<Spec> out = new ArrayList<>();
        for (Spec s : specs) if (s != null) out.add(s);
        return out;
    }
}
