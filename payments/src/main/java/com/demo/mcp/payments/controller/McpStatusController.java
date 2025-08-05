package com.demo.mcp.payments.controller;

import com.demo.mcp.payments.config.ToolDiscoveryConfig;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
public class McpStatusController {

    @GetMapping("/mcp/status")
    public Map<String, Object> getMcpStatus() {
        Map<String, Object> status = new HashMap<>();
        status.put("status", "running");
        status.put("endpoint", "/sse");
        status.put("discoveredTools", ToolDiscoveryConfig.discoveredTools.size());
        
        List<Map<String, String>> tools = ToolDiscoveryConfig.discoveredTools.stream()
            .map(tool -> Map.of(
                "name", tool.toolAnnotation.name(),
                "description", tool.toolAnnotation.description()
            ))
            .toList();
        
        status.put("tools", tools);
        return status;
    }

    @GetMapping("/mcp/health")
    public Map<String, String> getMcpHealth() {
        return Map.of("status", "healthy");
    }
} 