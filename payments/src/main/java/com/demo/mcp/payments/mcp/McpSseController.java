package com.demo.mcp.payments.mcp;

import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.concurrent.CopyOnWriteArrayList;

@RestController
public class McpSseController {

    private final CopyOnWriteArrayList<SseEmitter> emitters = new CopyOnWriteArrayList<>();

    @GetMapping(value = "/sse", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter subscribe() {
        SseEmitter emitter = new SseEmitter(Long.MAX_VALUE);
        emitters.add(emitter);
        
        emitter.onCompletion(() -> emitters.remove(emitter));
        emitter.onTimeout(() -> emitters.remove(emitter));
        emitter.onError((ex) -> emitters.remove(emitter));
        
        try {
            // Send initial connection message
            emitter.send(SseEmitter.event()
                .name("connect")
                .data("MCP Server connected"));
        } catch (IOException e) {
            emitter.completeWithError(e);
        }
        
        return emitter;
    }

    public void broadcastMessage(String message) {
        emitters.forEach(emitter -> {
            try {
                emitter.send(SseEmitter.event()
                    .name("message")
                    .data(message));
            } catch (IOException e) {
                emitters.remove(emitter);
            }
        });
    }
} 