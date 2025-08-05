package com.demo.mcp.payments.model;

public class RelationshipManagerResponse {
    private String clientId;
    private String rmName;
    private String rmEmail;
    private String rmContact;

    public RelationshipManagerResponse(String clientId, String rmName, String rmEmail, String rmContact) {
        this.clientId = clientId;
        this.rmName = rmName;
        this.rmEmail = rmEmail;
        this.rmContact = rmContact;
    }

    public String getClientId() {
        return clientId;
    }

    public void setClientId(String clientId) {
        this.clientId = clientId;
    }

    public String getRmName() {
        return rmName;
    }

    public void setRmName(String rmName) {
        this.rmName = rmName;
    }

    public String getRmEmail() {
        return rmEmail;
    }

    public void setRmEmail(String rmEmail) {
        this.rmEmail = rmEmail;
    }

    public String getRmContact() {
        return rmContact;
    }

    public void setRmContact(String rmContact) {
        this.rmContact = rmContact;
    }
}
