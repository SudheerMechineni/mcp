package com.demo.mcp.payments.mcp;

import com.demo.mcp.payments.config.ToolDiscoveryConfig;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Component
public class McpServerHandler {

    @Autowired
    private McpSseController sseController;

    private final ObjectMapper objectMapper = new ObjectMapper();

    public void handleMcpRequest(String request) {
        try {
            Map<String, Object> requestMap = objectMapper.readValue(request, Map.class);
            String method = (String) requestMap.get("method");
            
            switch (method) {
                case "initialize":
                    handleInitialize(requestMap);
                    break;
                case "tools/list":
                    handleToolsList(requestMap);
                    break;
                case "tools/call":
                    handleToolsCall(requestMap);
                    break;
                default:
                    sendError("Unknown method: " + method);
            }
        } catch (Exception e) {
            sendError("Error processing request: " + e.getMessage());
        }
    }

    private void handleInitialize(Map<String, Object> request) {
        Map<String, Object> response = new HashMap<>();
        response.put("jsonrpc", "2.0");
        response.put("id", request.get("id"));
        
        Map<String, Object> result = new HashMap<>();
        result.put("protocolVersion", "2024-11-05");
        result.put("capabilities", Map.of(
            "tools", Map.of(
                "listChanged", true
            )
        ));
        result.put("serverInfo", Map.of(
            "name", "payments-mcp-server",
            "version", "1.0.0"
        ));
        
        response.put("result", result);
        sendResponse(response);
    }

    private void handleToolsList(Map<String, Object> request) {
        Map<String, Object> response = new HashMap<>();
        response.put("jsonrpc", "2.0");
        response.put("id", request.get("id"));
        
        List<ToolDiscoveryConfig.DiscoveredTool> tools = ToolDiscoveryConfig.discoveredTools;
        Map<String, Object>[] toolsArray = new Map[tools.size()];
        
        for (int i = 0; i < tools.size(); i++) {
            ToolDiscoveryConfig.DiscoveredTool tool = tools.get(i);
            Map<String, Object> toolMap = new HashMap<>();
            toolMap.put("name", tool.toolAnnotation.name());
            toolMap.put("description", tool.toolAnnotation.description());
            toolMap.put("inputSchema", Map.of(
                "type", "object",
                "properties", new HashMap<>()
            ));
            toolsArray[i] = toolMap;
        }
        
        response.put("result", Map.of("tools", toolsArray));
        sendResponse(response);
    }

    private void handleToolsCall(Map<String, Object> request) {
        Map<String, Object> params = (Map<String, Object>) request.get("params");
        String name = (String) params.get("name");
        
        Map<String, Object> response = new HashMap<>();
        response.put("jsonrpc", "2.0");
        response.put("id", request.get("id"));
        
        // Simulate tool execution based on name
        Map<String, Object> result = new HashMap<>();
        result.put("content", List.of(Map.of(
            "type", "text",
            "text", "Tool '" + name + "' executed successfully"
        )));
        
        response.put("result", result);
        sendResponse(response);
    }

    private void sendResponse(Map<String, Object> response) {
        try {
            String responseJson = objectMapper.writeValueAsString(response);
            sseController.broadcastMessage(responseJson);
        } catch (Exception e) {
            sendError("Error sending response: " + e.getMessage());
        }
    }

    private void sendError(String message) {
        Map<String, Object> error = new HashMap<>();
        error.put("jsonrpc", "2.0");
        error.put("error", Map.of(
            "code", -1,
            "message", message
        ));
        
        try {
            String errorJson = objectMapper.writeValueAsString(error);
            sseController.broadcastMessage(errorJson);
        } catch (Exception e) {
            // Log error
        }
    }
} 