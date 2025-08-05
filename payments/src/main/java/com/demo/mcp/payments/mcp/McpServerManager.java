package com.demo.mcp.payments.mcp;

import com.demo.mcp.payments.config.ToolDiscoveryConfig;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import java.util.List;

@Component
public class McpServerManager {

    @Autowired
    private ToolDiscoveryConfig toolDiscoveryConfig;

    @PostConstruct
    public void initializeMcpServer() {
        // Log discovered tools
        System.out.println("MCP Server initialized with " + ToolDiscoveryConfig.discoveredTools.size() + " tools:");
        ToolDiscoveryConfig.discoveredTools.forEach(discoveredTool -> 
            System.out.println("  - " + discoveredTool.toolAnnotation.name() + ": " + discoveredTool.toolAnnotation.description())
        );
    }

    public List<ToolDiscoveryConfig.DiscoveredTool> getDiscoveredTools() {
        return ToolDiscoveryConfig.discoveredTools;
    }
} 