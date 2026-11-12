package vn.ptit.ecom.model.product;

import java.util.List;

/** A laptop: a product with the attributes of the laptop_detail table. */
public class LaptopDetail extends Product {
    private final String cpu;
    private final int ramGb;
    private final int storageGb;
    private final double screenInch;
    private final int warrantyMonths;

    public LaptopDetail(Product row, String cpu, int ramGb, int storageGb, double screenInch, int warrantyMonths) {
        super(row);
        this.cpu = cpu;
        this.ramGb = ramGb;
        this.storageGb = storageGb;
        this.screenInch = screenInch;
        this.warrantyMonths = warrantyMonths;
    }

    @Override
    public DetailKind kind() { return DetailKind.LAPTOP; }

    @Override
    public List<Spec> specs() {
        return list(spec("Processor", cpu), spec("Memory", ramGb + " GB"), spec("Storage", storageGb + " GB"),
                spec("Screen", screenInch + " inch"), spec("Warranty", warrantyMonths + " months"));
    }

    public String getCpu() { return cpu; }
    public int getRamGb() { return ramGb; }
    public int getStorageGb() { return storageGb; }
    public double getScreenInch() { return screenInch; }
    public int getWarrantyMonths() { return warrantyMonths; }
}
