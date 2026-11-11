package vn.ptit.ecom.model.customer;

import java.math.BigDecimal;

public class CustomerVIP extends Customer {
    private final int vipLevel;
    private final BigDecimal discountRate;
    private final int rewardPoints;

    public CustomerVIP(int id, FullName fullName, String email, String phone, int vipLevel, BigDecimal discountRate,
                       int rewardPoints) {
        super(id, fullName, email, phone);
        this.vipLevel = vipLevel;
        this.discountRate = discountRate;
        this.rewardPoints = rewardPoints;
    }

    @Override
    public BigDecimal discountRate() { return discountRate; }

    @Override
    public String kindLabel() { return "VIP level " + vipLevel; }

    public int getVipLevel() { return vipLevel; }
    public int getRewardPoints() { return rewardPoints; }
}
