package com.demo.mcp.payments.controller;

import com.demo.mcp.payments.model.PaymentStatusResponse;
import com.demo.mcp.payments.model.AccountBalanceResponse;
import com.demo.mcp.payments.model.RelationshipManagerResponse;

import com.demo.mcp.payments.annotation.McpTool;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import jakarta.servlet.http.HttpServletRequest;
import java.util.Random;
import java.util.UUID;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@RestController
public class PaymentsController {
    private static final Logger logger = LoggerFactory.getLogger(PaymentsController.class);
    private final Random random = new Random();
    private final String[] currencies = {"USD", "EUR", "SGD", "INR", "GBP"};
    private final String[] statuses = {"active", "inactive", "blocked", "pending", "closed"};
    private final String[] rmNames = {"John Tan", "Priya Singh", "Alex Lee", "Maria Gomez", "David Chen"};
    private final String[] emails = {"john.tan@sc.com", "priya.singh@sc.com", "alex.lee@sc.com", "maria.gomez@sc.com", "david.chen@sc.com"};
    private final String[] contacts = {"+65-8123-4567", "+91-98765-43210", "+44-7700-900123", "+1-202-555-0173", "+86-138-00138000"};

    private String randomCurrency() { return currencies[random.nextInt(currencies.length)]; }
    private String randomStatus() { return statuses[random.nextInt(statuses.length)]; }
    private String randomDate() { return LocalDate.now().minusDays(random.nextInt(365)).format(DateTimeFormatter.ISO_DATE); }
    private String randomDateTime() { return LocalDate.now().minusDays(random.nextInt(365)).atTime(random.nextInt(24), random.nextInt(60)).format(DateTimeFormatter.ISO_DATE_TIME) + "Z"; }
    private String randomAccountId() { return String.valueOf(1000 + random.nextInt(9000)); }
    private double randomBalance() { return Math.round((1000 + random.nextDouble() * 100000) * 100.0) / 100.0; }
    private int randomIndex(int bound) { return random.nextInt(bound); }

    /**
     * Retrieves the status of a payment based on transaction ID.
     * @param transactionId Unique transaction identifier
     * @return Payment status response
     */
    @McpTool(name = "GetPaymentStatus", description = "Retrieves the status of a payment based on transaction ID.")
    @GetMapping("/api/payments/status")
    public ResponseEntity<PaymentStatusResponse> getPaymentStatus(@RequestParam String transactionId, HttpServletRequest request) {
        logger.info("Received GetPaymentStatus request: method={}, uri={}, params={}", request.getMethod(), request.getRequestURI(), request.getQueryString());
        PaymentStatusResponse response = new PaymentStatusResponse(
            transactionId != null ? transactionId : UUID.randomUUID().toString(),
            randomStatus(),
            randomDate(),
            randomBalance(),
            randomCurrency()
        );
        logger.info("Responding with: {}", response);
        return ResponseEntity.ok(response);
    }

    /**
     * Fetches current balance of a specified account.
     * @param accountId Client’s account ID
     * @param currency Currency to filter by (optional)
     * @return Account balance response
     */
    @McpTool(name = "GetAccountBalance", description = "Fetches current balance of a specified account.")
    @GetMapping("/api/payments/accounts/balance")
    public ResponseEntity<AccountBalanceResponse> getAccountBalance(
            @RequestParam String accountId,
            @RequestParam(required = false) String currency,
            HttpServletRequest request) {
        logger.info("Received GetAccountBalance request: method={}, uri={}, params={}", request.getMethod(), request.getRequestURI(), request.getQueryString());
        String curr = currency != null ? currency : randomCurrency();
        AccountBalanceResponse response = new AccountBalanceResponse(
            accountId != null ? accountId : randomAccountId(),
            curr,
            randomBalance(),
            curr,
            randomDateTime()
        );
        logger.info("Responding with: {}", response);
        return ResponseEntity.ok(response);
    }

    /**
     * Provides the assigned Relationship Manager details for a given client.
     * @param clientId Client unique ID
     * @return Relationship Manager details response
     */
    @McpTool(name = "GetRelationshipManager", description = "Provides the assigned Relationship Manager details for a given client.")
    @GetMapping("/api/payments/customers/relationship-manager")
    public ResponseEntity<RelationshipManagerResponse> getRelationshipManager(@RequestParam String clientId, HttpServletRequest request) {
        logger.info("Received GetRelationshipManager request: method={}, uri={}, params={}", request.getMethod(), request.getRequestURI(), request.getQueryString());
        int idx = randomIndex(rmNames.length);
        RelationshipManagerResponse response = new RelationshipManagerResponse(
            clientId != null ? clientId : UUID.randomUUID().toString(),
            rmNames[idx],
            emails[idx],
            contacts[idx]
        );
        logger.info("Responding with: {}", response);
        return ResponseEntity.ok(response);
    }

    // Add SSE endpoint for MCP server handshake
    @RequestMapping(value = "/sse", method = RequestMethod.GET)
    public SseEmitter sseEndpoint() {
        return new SseEmitter(0L); // 0L means no timeout
    }

    @RequestMapping(value = "/*", method = {RequestMethod.GET, RequestMethod.POST})
    public void logAllRequests(HttpServletRequest request) {
        logger.info("Incoming request: method={}, uri={}, params={}", request.getMethod(), request.getRequestURI(), request.getQueryString());
    }

    /**
     * Lists all discovered MCP tools with their name, description, and endpoint path.
     * @return List of MCP tools
     */
    @McpTool(name = "McpInspector", description = "Lists all discovered MCP tools with their name, description, and endpoint path.")
    @GetMapping("/api/payments/mcp-inspector")
    public ResponseEntity<List<Object>> mcpInspector() {
        List<Object> toolsList = new ArrayList<>();
        for (com.demo.mcp.payments.config.ToolDiscoveryConfig.DiscoveredTool tool : com.demo.mcp.payments.config.ToolDiscoveryConfig.discoveredTools) {
            var method = tool.method;
            String endpoint = "";
            if (method.isAnnotationPresent(GetMapping.class)) {
                String[] paths = method.getAnnotation(GetMapping.class).value();
                if (paths.length > 0) endpoint = paths[0];
            } else if (method.isAnnotationPresent(PostMapping.class)) {
                String[] paths = method.getAnnotation(PostMapping.class).value();
                if (paths.length > 0) endpoint = paths[0];
            }
            toolsList.add(Map.of(
                "name", tool.toolAnnotation.name(),
                "description", tool.toolAnnotation.description(),
                "endpoint", endpoint
            ));
        }
        return ResponseEntity.ok(toolsList);
    }
}