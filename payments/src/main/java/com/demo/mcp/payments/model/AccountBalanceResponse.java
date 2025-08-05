package com.demo.mcp.payments.model;

public class AccountBalanceResponse {
    private String accountId;
    private String requestedCurrency;
    private double availableBalance;
    private String currency;
    private String timestamp;

    public AccountBalanceResponse(String accountId, String requestedCurrency, double availableBalance, String currency, String timestamp) {
        this.accountId = accountId;
        this.requestedCurrency = requestedCurrency;
        this.availableBalance = availableBalance;
        this.currency = currency;
        this.timestamp = timestamp;
    }

    public String getAccountId() {
        return accountId;
    }

    public void setAccountId(String accountId) {
        this.accountId = accountId;
    }

    public String getRequestedCurrency() {
        return requestedCurrency;
    }

    public void setRequestedCurrency(String requestedCurrency) {
        this.requestedCurrency = requestedCurrency;
    }

    public double getAvailableBalance() {
        return availableBalance;
    }

    public void setAvailableBalance(double availableBalance) {
        this.availableBalance = availableBalance;
    }

    public String getCurrency() {
        return currency;
    }

    public void setCurrency(String currency) {
        this.currency = currency;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }
}
