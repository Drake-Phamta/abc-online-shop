package vn.ptit.ecom.model.product;

/** A node of the category tree; only leaf categories have a detail kind and hold products. */
public record Category(int id, Integer parentId, String name, String slug, DetailKind detailKind) {

    public boolean isLeaf() { return detailKind != null; }
}
