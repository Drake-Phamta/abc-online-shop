package vn.ptit.ecom.ai;

import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * FR-S5: the photo side of the AI search. Every product image is described by three feature vectors: the colours
 * of the object (the background is found from the border of the picture and left out), the directions of its edges
 * in four regions, and its silhouette on a 6 x 6 grid. A photo is compared with every product by the cosine of
 * each vector; the weighted sum is the similarity.
 */
public class ImageIndex {
    static final int SIZE = 96;
    static final double W_COLOUR = 0.55, W_EDGES = 0.25, W_SHAPE = 0.20;
    /** Below this similarity the picture is not shown (failure analysis: unrelated photo). */
    static final double MIN_SCORE = 0.6;

    record Features(double[] colour, double[] edges, double[] shape) { }

    private final Map<Integer, Features> features;

    private ImageIndex(Map<Integer, Features> features) {
        this.features = features;
    }

    /** @param images product id -> its catalogue image */
    public static ImageIndex build(Map<Integer, BufferedImage> images) {
        Map<Integer, Features> f = new LinkedHashMap<>();
        images.forEach((id, img) -> f.put(id, features(img)));
        return new ImageIndex(f);
    }

    public int size() {
        return features.size();
    }

    /** Up to k products whose image looks most like the photo, best first. */
    public List<Hit> rank(BufferedImage photo, int k) {
        Features q = features(photo);
        List<Hit> hits = new ArrayList<>();
        features.forEach((id, f) -> {
            double colour = dot(q.colour(), f.colour()), edges = dot(q.edges(), f.edges()), shape = dot(q.shape(), f.shape());
            double score = W_COLOUR * colour + W_EDGES * edges + W_SHAPE * shape;
            if (score < MIN_SCORE) return;
            hits.add(new Hit(id, Math.round(score * 1000) / 1000.0, List.of(
                    "colours alike " + Math.round(colour * 100) + " %",
                    "outline alike " + Math.round((W_EDGES * edges + W_SHAPE * shape) / (W_EDGES + W_SHAPE) * 100) + " %")));
        });
        hits.sort(Comparator.comparingDouble(Hit::score).reversed().thenComparingInt(Hit::productId));
        return hits.size() > k ? new ArrayList<>(hits.subList(0, k)) : hits;
    }

    static Features features(BufferedImage source) {
        BufferedImage img = new BufferedImage(SIZE, SIZE, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = img.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_INTERPOLATION, RenderingHints.VALUE_INTERPOLATION_BILINEAR);
        g.drawImage(source, 0, 0, SIZE, SIZE, null);
        g.dispose();
        int[] rgb = img.getRGB(0, 0, SIZE, SIZE, null, 0, SIZE);
        boolean[] object = objectMask(rgb);
        return new Features(colours(rgb, object), edges(rgb, object), silhouette(object));
    }

    /** Background = pixels close to the mean colour of a 3-pixel border; if that leaves almost nothing, all pixels. */
    static boolean[] objectMask(int[] rgb) {
        long r = 0, gr = 0, b = 0;
        int count = 0;
        for (int y = 0; y < SIZE; y++)
            for (int x = 0; x < SIZE; x++)
                if (x < 3 || y < 3 || x >= SIZE - 3 || y >= SIZE - 3) {
                    int p = rgb[y * SIZE + x];
                    r += (p >> 16) & 255; gr += (p >> 8) & 255; b += p & 255;
                    count++;
                }
        double br = (double) r / count, bg = (double) gr / count, bb = (double) b / count;
        boolean[] mask = new boolean[rgb.length];
        int on = 0;
        for (int i = 0; i < rgb.length; i++) {
            int p = rgb[i];
            double d = Math.sqrt(sq(((p >> 16) & 255) - br) + sq(((p >> 8) & 255) - bg) + sq((p & 255) - bb));
            mask[i] = d > 40;
            if (mask[i]) on++;
        }
        if (on < rgb.length / 20) java.util.Arrays.fill(mask, true);
        return mask;
    }

    /** 18 hue bins weighted by saturation, plus black, grey and white; square root of the shares (Hellinger). */
    static double[] colours(int[] rgb, boolean[] object) {
        double[] h = new double[21];
        float[] hsb = new float[3];
        for (int i = 0; i < rgb.length; i++) {
            if (!object[i]) continue;
            int p = rgb[i];
            java.awt.Color.RGBtoHSB((p >> 16) & 255, (p >> 8) & 255, p & 255, hsb);
            if (hsb[1] < 0.18 || hsb[2] < 0.18) h[18 + (hsb[2] < 0.3 ? 0 : hsb[2] < 0.75 ? 1 : 2)] += 1;
            else h[Math.min(17, (int) (hsb[0] * 18))] += 0.5 + hsb[1] / 2;
        }
        double sum = 0;
        for (double v : h) sum += v;
        for (int i = 0; i < h.length; i++) h[i] = sum == 0 ? 0 : Math.sqrt(h[i] / sum);
        return unit(h);
    }

    /** Sobel edge directions (8 bins over 180 degrees) in each quarter of the picture, weighted by edge strength. */
    static double[] edges(int[] rgb, boolean[] object) {
        double[] gray = new double[rgb.length];
        for (int i = 0; i < rgb.length; i++) {
            int p = rgb[i];
            gray[i] = 0.299 * ((p >> 16) & 255) + 0.587 * ((p >> 8) & 255) + 0.114 * (p & 255);
        }
        double[] h = new double[32];
        for (int y = 1; y < SIZE - 1; y++)
            for (int x = 1; x < SIZE - 1; x++) {
                double gx = gray[(y - 1) * SIZE + x + 1] + 2 * gray[y * SIZE + x + 1] + gray[(y + 1) * SIZE + x + 1]
                        - gray[(y - 1) * SIZE + x - 1] - 2 * gray[y * SIZE + x - 1] - gray[(y + 1) * SIZE + x - 1];
                double gy = gray[(y + 1) * SIZE + x - 1] + 2 * gray[(y + 1) * SIZE + x] + gray[(y + 1) * SIZE + x + 1]
                        - gray[(y - 1) * SIZE + x - 1] - 2 * gray[(y - 1) * SIZE + x] - gray[(y - 1) * SIZE + x + 1];
                double m = Math.hypot(gx, gy);
                if (m < 40) continue;
                double angle = Math.atan2(gy, gx);
                if (angle < 0) angle += Math.PI;
                int bin = Math.min(7, (int) (angle / Math.PI * 8));
                int cell = (y < SIZE / 2 ? 0 : 2) + (x < SIZE / 2 ? 0 : 1);
                h[cell * 8 + bin] += m;
            }
        return unit(h);
    }

    /** Share of object pixels in each cell of a 6 x 6 grid. */
    static double[] silhouette(boolean[] object) {
        double[] h = new double[36];
        int cell = SIZE / 6;
        for (int i = 0; i < object.length; i++)
            if (object[i]) h[(i / SIZE / cell) * 6 + (i % SIZE) / cell] += 1;
        return unit(h);
    }

    private static double[] unit(double[] v) {
        double norm = 0;
        for (double x : v) norm += x * x;
        norm = Math.sqrt(norm);
        if (norm > 0) for (int i = 0; i < v.length; i++) v[i] /= norm;
        return v;
    }

    private static double dot(double[] a, double[] b) {
        double s = 0;
        for (int i = 0; i < a.length; i++) s += a[i] * b[i];
        return s;
    }

    private static double sq(double x) {
        return x * x;
    }
}
