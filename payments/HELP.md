# Payments API with MCP Integration

This project is a Spring Boot application providing payment-related APIs with Model Context Protocol (MCP) integration. It demonstrates:
- REST endpoints for payment status, account balance, and relationship manager details
- MCP tool auto-discovery and server integration
- SSE endpoint for MCP server handshake
- Randomized demo data for realistic responses
- Logging of all requests and responses for traceability

## 🚀 How to Run

### Prerequisites
- Java 17 or higher
- Maven (or use the included Maven wrapper)

### 1. Compile and Run
```bash
./mvnw clean package
./mvnw spring-boot:run
```
Or run the JAR directly:
```bash
java -jar target/payments-0.0.1-SNAPSHOT.jar
```

The API will be available at: http://localhost:8080

## 🛠️ Endpoints

- **Get Payment Status**
  - `GET/POST /api/payments/status?transactionId=txn001`
- **Get Account Balance**
  - `GET/POST /api/payments/accounts/balance?accountId=1234`
- **Get Relationship Manager Details**
  - `GET/POST /api/payments/customers/relationship-manager?clientId=acc123`
- **MCP Inspector**
  - `GET /api/payments/mcp-inspector` (lists all MCP tools)
- **SSE for MCP Server**
  - `GET /sse`

## 📋 Example Requests

```bash
curl -X GET "http://localhost:8080/api/payments/status?transactionId=txn001"
curl -X GET "http://localhost:8080/api/payments/accounts/balance?accountId=1234"
curl -X GET "http://localhost:8080/api/payments/customers/relationship-manager?clientId=acc123"
curl -X GET "http://localhost:8080/api/payments/mcp-inspector"
curl -X GET "http://localhost:8080/sse" -H "Accept: text/event-stream"
```

## 📝 Description

This project is designed for demo, development, and MCP integration testing. All responses are randomized for realism. The MCP Inspector endpoint helps you discover available MCP tools and their metadata. Logging is enabled for all requests and responses to aid debugging and traceability.

For troubleshooting, building, and more details, see the rest of this file.

---

# Payments API with MCP Integration

This project demonstrates a Spring Boot application with Model Context Protocol (MCP) integration for payment-related APIs.

## 🚀 Quick Start

### Prerequisites

- **Java 17** or higher
- **Maven** (included with Maven wrapper)
- **Git** (for cloning the repository)

### 1. Clone and Navigate to Project

```bash
git clone <repository-url>
cd payments
```

### 2. Compile the Project

```bash
# Clean and compile
./mvnw clean compile

# Or just compile
./mvnw compile
```

### 3. Run the Application

```bash
# Run with Spring Boot Maven plugin
./mvnw spring-boot:run
```

The application will start on **http://localhost:8080**

## 📋 Project Structure

```
payments/
├── src/main/java/com/demo/mcp/payments/
│   ├── annotation/
│   │   └── McpTool.java              # Custom MCP tool annotation
│   ├── config/
│   │   ├── SecurityConfig.java       # Spring Security configuration
│   │   └── ToolDiscoveryConfig.java  # MCP tool discovery
│   ├── controller/
│   │   └── PaymentsController.java   # REST API endpoints
│   ├── mcp/
│   │   └── McpServerManager.java     # MCP server management
│   └── model/
│       ├── AccountBalanceResponse.java
│       ├── PaymentStatusResponse.java
│       └── RelationshipManagerResponse.java
├── src/main/resources/
│   └── application.properties        # Application configuration
├── pom.xml                          # Maven dependencies
└── HELP.md                          # This file
```

## 🔧 Configuration

### Application Properties

The application is configured with:

- **Port**: 8080
- **Database**: H2 in-memory database
- **Security**: Disabled for development
- **MCP**: Custom tool discovery enabled

### Key Dependencies

- **Spring Boot 3.5.4**
- **Spring Security** (configured to allow all requests)
- **Spring Data JPA** with H2 database
- **MCP SDK** (Model Context Protocol)
- **H2 Database** (in-memory)

## 🛠️ API Endpoints

### 1. Payment Status
```bash
GET /api/payments/status?transactionId=12345
```

**Response:**
```json
{
  "transactionId": "12345",
  "status": "Settled",
  "settlementDate": "2025-07-24",
  "amount": 50000.0,
  "currency": "USD"
}
```

### 2. Account Balance
```bash
GET /api/payments/accounts/balance?accountId=ACC123&currency=USD
```

**Response:**
```json
{
  "accountId": "ACC123",
  "requestedCurrency": "USD",
  "availableBalance": 1000000.0,
  "currency": "USD",
  "timestamp": "2025-08-01T10:15:00Z"
}
```

### 3. Relationship Manager
```bash
GET /api/payments/customers/relationship-manager?clientId=CLIENT456
```

**Response:**
```json
{
  "clientId": "CLIENT456",
  "rmName": "John Tan",
  "rmEmail": "john.tan@sc.com",
  "rmContact": "+65-8123-4567"
}
```

## 🔍 MCP Integration

### Custom MCP Tool Annotation

The project uses a custom `@McpTool` annotation to mark API methods as MCP tools:

```java
@McpTool(name = "GetPaymentStatus", description = "Retrieves the status of a payment based on transaction ID.")
@GetMapping("/api/payments/status")
public ResponseEntity<PaymentStatusResponse> getPaymentStatus(@RequestParam String transactionId) {
    // Implementation
}
```

### Tool Discovery

The `ToolDiscoveryConfig` automatically discovers methods annotated with `@McpTool` and logs them at startup:

```
MCP Server initialized with 3 tools:
  - GetPaymentStatus: Retrieves the status of a payment based on transaction ID.
  - GetAccountBalance: Fetches current balance of a specified account.
  - GetRelationshipManager: Provides the assigned Relationship Manager details for a given client.
```

### MCP Server Endpoints

The application provides several MCP-related endpoints:

#### 1. MCP Status
```bash
GET /mcp/status
```

**Response:**
```json
{
  "status": "running",
  "endpoint": "/sse",
  "discoveredTools": 3,
  "tools": [
    {
      "name": "GetPaymentStatus",
      "description": "Retrieves the status of a payment based on transaction ID."
    },
    {
      "name": "GetAccountBalance",
      "description": "Fetches current balance of a specified account."
    },
    {
      "name": "GetRelationshipManager",
      "description": "Provides the assigned Relationship Manager details for a given client."
    }
  ]
}
```

#### 2. MCP Health
```bash
GET /mcp/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

#### 3. SSE Endpoint (MCP Communication)
```bash
GET /sse
```

This endpoint provides Server-Sent Events for MCP protocol communication. It responds with:
- **Content-Type**: `text/event-stream`
- **Initial Event**: `event:connect` with `data:MCP Server connected`

### Testing MCP Server

```bash
# Check MCP server status
curl -X GET "http://localhost:8080/mcp/status"

# Test MCP health endpoint
curl -X GET "http://localhost:8080/mcp/health"

# Test SSE endpoint (will show connection message)
curl -X GET "http://localhost:8080/sse" -H "Accept: text/event-stream"
```

## 🧪 Testing

### Test API Endpoints

```bash
# Test payment status
curl -X GET "http://localhost:8080/api/payments/status?transactionId=12345"

# Test account balance
curl -X GET "http://localhost:8080/api/payments/accounts/balance?accountId=ACC123&currency=USD"

# Test relationship manager
curl -X GET "http://localhost:8080/api/payments/customers/relationship-manager?clientId=CLIENT456"
```

### Health Check

```bash
curl -X GET "http://localhost:8080/actuator/health"
```

## 🛑 Stopping the Application

### Method 1: Graceful Shutdown
Press `Ctrl+C` in the terminal where the application is running.

### Method 2: Kill Process
```bash
# Find the process
ps aux | grep "PaymentsApplication"

# Kill by process ID
kill <PID>

# Or kill all Java processes (be careful!)
pkill -f "PaymentsApplication"
```

## 🔧 Troubleshooting

### Port Already in Use
If port 8080 is already in use:

```bash
# Find processes using port 8080
lsof -i :8080

# Kill the process
lsof -ti:8080 | xargs kill -9
```

### Compilation Errors
If you encounter compilation errors:

```bash
# Clean and recompile
./mvnw clean compile

# Check for dependency issues
./mvnw dependency:tree
```

### Database Issues
The application uses H2 in-memory database. If you see database-related errors:

1. Check `application.properties` for database configuration
2. Ensure H2 dependency is included in `pom.xml`
3. Restart the application

### Security Issues
If you get 401 Unauthorized errors:

1. Check `SecurityConfig.java` is properly configured
2. Ensure the security configuration allows all requests
3. Restart the application

## 📦 Building JAR

To create a standalone JAR file:

```bash
# Build the JAR
./mvnw clean package

# Run the JAR
java -jar target/payments-0.0.1-SNAPSHOT.jar
```

## 🔄 Development Workflow

1. **Make Changes**: Edit source files
2. **Compile**: `./mvnw compile`
3. **Run**: `./mvnw spring-boot:run`
4. **Test**: Use curl commands or browser
5. **Stop**: `Ctrl+C` or kill process

## 📚 Additional Resources

- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
- [H2 Database](https://www.h2database.com/)
- [Maven Documentation](https://maven.apache.org/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

