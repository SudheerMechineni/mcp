package com.demo.mcp.payments.model;

public class PaymentStatusResponse {
    private String transactionId;
    private String status;
    private String settlementDate;
    private double amount;
    private String currency;

    public PaymentStatusResponse(String transactionId, String status, String settlementDate, double amount, String currency) {
        this.transactionId = transactionId;
        this.status = status;
        this.settlementDate = settlementDate;
        this.amount = amount;
        this.currency = currency;
    }

    public String getTransactionId() {
        return transactionId;
    }

    public void setTransactionId(String transactionId) {
        this.transactionId = transactionId;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getSettlementDate() {
        return settlementDate;
    }

    public void setSettlementDate(String settlementDate) {
        this.settlementDate = settlementDate;
    }

    public double getAmount() {
        return amount;
    }

    public void setAmount(double amount) {
        this.amount = amount;
    }

    public String getCurrency() {
        return currency;
    }

    public void setCurrency(String currency) {
        this.currency = currency;
    }
}
