package vn.ptit.ecom.model.product;

import java.util.List;

/** An apparel item (clothes, shoes): a product with the attributes of the apparel_detail table. */
public class ApparelDetail extends Product {
    private final String sizeLabel;
    private final String color;
    private final String material;

    public ApparelDetail(Product row, String sizeLabel, String color, String material) {
        super(row);
        this.sizeLabel = sizeLabel;
        this.color = color;
        this.material = material;
    }

    @Override
    public DetailKind kind() { return DetailKind.APPAREL; }

    @Override
    public List<Spec> specs() {
        return list(spec("Size", sizeLabel), spec("Colour", color), spec("Material", material));
    }

    public String getSizeLabel() { return sizeLabel; }
    public String getColor() { return color; }
    public String getMaterial() { return material; }
}
