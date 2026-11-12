package vn.ptit.ecom.model.product;

import java.util.List;

/** A phone: a product with the attributes of the phone_detail table. */
public class PhoneDetail extends Product {
    private final String os;
    private final int storageGb;
    private final Integer cameraMp;
    private final double screenInch;
    private final Integer batteryMah;
    private final int warrantyMonths;

    public PhoneDetail(Product row, String os, int storageGb, Integer cameraMp, double screenInch, Integer batteryMah,
                       int warrantyMonths) {
        super(row);
        this.os = os;
        this.storageGb = storageGb;
        this.cameraMp = cameraMp;
        this.screenInch = screenInch;
        this.batteryMah = batteryMah;
        this.warrantyMonths = warrantyMonths;
    }

    @Override
    public DetailKind kind() { return DetailKind.PHONE; }

    @Override
    public List<Spec> specs() {
        return list(spec("Operating system", os), spec("Storage", storageGb + " GB"),
                spec("Main camera", cameraMp == null ? null : cameraMp + " MP"), spec("Screen", screenInch + " inch"),
                spec("Battery", batteryMah == null ? null : batteryMah + " mAh"), spec("Warranty", warrantyMonths + " months"));
    }

    public String getOs() { return os; }
    public int getStorageGb() { return storageGb; }
    public Integer getCameraMp() { return cameraMp; }
    public double getScreenInch() { return screenInch; }
    public Integer getBatteryMah() { return batteryMah; }
    public int getWarrantyMonths() { return warrantyMonths; }
}
