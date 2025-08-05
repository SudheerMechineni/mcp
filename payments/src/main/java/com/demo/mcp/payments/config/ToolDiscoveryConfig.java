package com.demo.mcp.payments.config;

import com.demo.mcp.payments.annotation.McpTool;
import org.springframework.beans.BeansException;
import org.springframework.beans.factory.config.BeanPostProcessor;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.annotation.AnnotationUtils;
import org.springframework.web.bind.annotation.RestController;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;

@Configuration
public class ToolDiscoveryConfig implements BeanPostProcessor {
    public static final List<DiscoveredTool> discoveredTools = new ArrayList<>();

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
        if (AnnotationUtils.findAnnotation(bean.getClass(), RestController.class) != null) {
            for (Method method : bean.getClass().getMethods()) {
                if (AnnotationUtils.findAnnotation(method, McpTool.class) != null) {
                    discoveredTools.add(new DiscoveredTool(bean, method, AnnotationUtils.findAnnotation(method, McpTool.class)));
                }
            }
        }
        return bean;
    }

    public static class DiscoveredTool {
        public final Object bean;
        public final Method method;
        public final McpTool toolAnnotation;
        public DiscoveredTool(Object bean, Method method, McpTool toolAnnotation) {
            this.bean = bean;
            this.method = method;
            this.toolAnnotation = toolAnnotation;
        }
    }
}
