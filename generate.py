# Spring Kafka Performance Testing - Complete Step-by-Step Guide

## 📋 Table of Contents
1. [Prerequisites Setup](#prerequisites-setup)
2. [Phase 1: Initial Setup & Integration Testing](#phase-1-initial-setup--integration-testing)
3. [Phase 2: Monitoring Setup](#phase-2-monitoring-setup)
4. [Phase 3: Load Testing with JMeter](#phase-3-load-testing-with-jmeter)
5. [Phase 4: Performance Analysis & Optimization](#phase-4-performance-analysis--optimization)
6. [Real-World Test Scenarios](#real-world-test-scenarios)

---

## Prerequisites Setup

### Required Tools & Dependencies
```xml
<!-- Spring Boot Kafka -->
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>

<!-- Testing -->
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka-test</artifactId>
    <scope>test</scope>
</dependency>

<!-- Monitoring -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>

<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>

<!-- For async testing -->
<dependency>
    <groupId>org.awaitility</groupId>
    <artifactId>awaitility</artifactId>
    <scope>test</scope>
</dependency>
```

### Test Environment Setup
```bash
# 1. Download and start Kafka using Docker
docker-compose up -d

# docker-compose.yml
version: '3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
```

---

## Phase 1: Initial Setup & Integration Testing

### Step 1.1: Create Your Spring Kafka Application

**Producer Service:**
```java
@Service
public class MessageProducerService {
    private final KafkaTemplate<String, String> kafkaTemplate;

    public MessageProducerService(KafkaTemplate<String, String> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void sendMessage(String topic, String key, String message) {
        kafkaTemplate.send(topic, key, message);
    }
}
```

**Consumer Service:**
```java
@Service
public class MessageConsumerService {
    private static final Logger log = LoggerFactory.getLogger(MessageConsumerService.class);

    @KafkaListener(topics = "test-topic", groupId = "test-group")
    public void consume(ConsumerRecord<String, String> record) {
        log.info("Consumed message: key={}, value={}", record.key(), record.value());
    }
}
```

### Step 1.2: Configure Application Properties

**src/main/resources/application.yml:**
```yaml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.apache.kafka.common.serialization.StringSerializer
      acks: 1
      batch-size: 16384
      linger-ms: 0
    consumer:
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      group-id: test-group
      auto-offset-reset: latest
      enable-auto-commit: false
    listener:
      ack-mode: manual

management:
  endpoints:
    web:
      exposure:
        include: "*"
  metrics:
    export:
      prometheus:
        enabled: true
```

**src/test/resources/application-test.yml:**
```yaml
spring:
  kafka:
    consumer:
      auto-offset-reset: earliest  # Important for testing
      properties:
        auto.offset.reset: earliest
```

### Step 1.3: Write Integration Tests

**Basic Integration Test with Embedded Kafka:**
```java
@SpringBootTest
@EmbeddedKafka(
    topics = {"test-topic"},
    partitions = 3,
    brokerProperties = {
        "listeners=PLAINTEXT://localhost:9093",
        "port=9093"
    }
)
@TestPropertySource(
    properties = {
        "spring.kafka.bootstrap-servers=${spring.embedded.kafka.brokers}",
        "spring.kafka.consumer.auto-offset-reset=earliest"
    }
)
@DirtiesContext
class KafkaIntegrationTest {

    @Autowired
    private MessageProducerService producer;

    @Autowired
    private EmbeddedKafkaBroker embeddedKafkaBroker;

    @Autowired
    private ConsumerFactory<String, String> consumerFactory;

    private Consumer<String, String> testConsumer;

    @BeforeEach
    void setUp() {
        Map<String, Object> configs = new HashMap<>(
            KafkaTestUtils.consumerProps("test-group", "true", embeddedKafkaBroker)
        );
        testConsumer = consumerFactory.createConsumer();
        testConsumer.subscribe(Collections.singletonList("test-topic"));
    }

    @AfterEach
    void tearDown() {
        if (testConsumer != null) {
            testConsumer.close();
        }
    }

    @Test
    void shouldProduceAndConsumeMessage() throws Exception {
        // Given
        String key = "test-key";
        String message = "test-message";

        // When
        producer.sendMessage("test-topic", key, message);

        // Then
        ConsumerRecords<String, String> records = 
            KafkaTestUtils.getRecords(testConsumer, Duration.ofSeconds(10));
        
        assertThat(records.count()).isEqualTo(1);
        ConsumerRecord<String, String> record = records.iterator().next();
        assertThat(record.key()).isEqualTo(key);
        assertThat(record.value()).isEqualTo(message);
    }
}
```

**Testing with Testcontainers (Recommended for realistic tests):**
```java
@SpringBootTest
@Testcontainers
class KafkaTestcontainersIntegrationTest {

    @Container
    @ServiceConnection
    static KafkaContainer kafka = new KafkaContainer(
        DockerImageName.parse("apache/kafka-native:3.8.0")
    ).withReuse(true);

    @Autowired
    private MessageProducerService producer;

    @Autowired
    private ConsumerFactory<String, String> consumerFactory;

    @Test
    void shouldHandleLargeMessageVolume() {
        // Test with realistic message volumes
        int messageCount = 1000;
        
        for (int i = 0; i < messageCount; i++) {
            producer.sendMessage("test-topic", "key-" + i, "message-" + i);
        }

        // Verify consumption using Awaitility
        await().atMost(Duration.ofSeconds(30))
               .untilAsserted(() -> {
                   // Verify all messages were consumed
                   assertThat(getConsumedMessageCount()).isEqualTo(messageCount);
               });
    }
}
```

---

## Phase 2: Monitoring Setup

### Step 2.1: Enable Prometheus Metrics

**Create prometheus.yml:**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'spring-boot-app'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets: ['host.docker.internal:8080']
```

### Step 2.2: Add Micrometer Configuration

```java
@Configuration
public class KafkaMetricsConfig {

    @Bean
    public KafkaTemplate<String, String> kafkaTemplate(
            ProducerFactory<String, String> producerFactory,
            MeterRegistry meterRegistry) {
        
        KafkaTemplate<String, String> template = new KafkaTemplate<>(producerFactory);
        template.setObservationEnabled(true);
        return template;
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, String> kafkaListenerContainerFactory(
            ConsumerFactory<String, String> consumerFactory,
            MeterRegistry meterRegistry) {
        
        ConcurrentKafkaListenerContainerFactory<String, String> factory = 
            new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory);
        factory.getContainerProperties().setObservationEnabled(true);
        return factory;
    }
}
```

### Step 2.3: Create Monitoring Dashboard

**Access Grafana:**
```bash
# Open browser to http://localhost:3000
# Default credentials: admin/admin

# Import Kafka dashboard ID: 7589
# Import JVM dashboard ID: 4701
```

### Step 2.4: Key Metrics to Monitor

Create a monitoring checklist script:
```bash
#!/bin/bash
# monitor-kafka.sh

echo "=== Kafka Performance Metrics ==="

# Consumer Lag
curl -s http://localhost:8080/actuator/prometheus | grep "kafka_consumer_fetch_manager_records_lag" | tail -5

# Producer Metrics
curl -s http://localhost:8080/actuator/prometheus | grep "kafka_producer_request_latency_avg" | tail -5

# Consumer Throughput
curl -s http://localhost:8080/actuator/prometheus | grep "kafka_consumer_records_consumed_total" | tail -5

# JVM Memory
curl -s http://localhost:8080/actuator/prometheus | grep "jvm_memory_used_bytes" | grep heap | tail -5

echo "================================"
```

---

## Phase 3: Load Testing with JMeter

### Step 3.1: Install JMeter and Kafka Plugin

```bash
# Download JMeter
wget https://dlcdn.apache.org//jmeter/binaries/apache-jmeter-5.6.3.tgz
tar -xzf apache-jmeter-5.6.3.tgz
cd apache-jmeter-5.6.3

# Download kafka-clients JAR
wget https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.6.0/kafka-clients-3.6.0.jar
cp kafka-clients-3.6.0.jar lib/

# Start JMeter
./bin/jmeter
```

### Step 3.2: Create JMeter Test Plan

**1. Add Thread Group:**
```
Test Plan → Add → Threads → Thread Group
```
Configure:
- Number of Threads: 10 (start small)
- Ramp-up Period: 10 seconds
- Loop Count: 100

**2. Add JSR223 Sampler for Producer:**
```groovy
import org.apache.kafka.clients.producer.*
import org.apache.kafka.common.serialization.StringSerializer
import java.util.Properties

// Initialize producer (once per thread)
if (!props.get("kafkaProducer")) {
    Properties configs = new Properties()
    configs.put("bootstrap.servers", "localhost:9092")
    configs.put("key.serializer", StringSerializer.class.getName())
    configs.put("value.serializer", StringSerializer.class.getName())
    configs.put("acks", "1")
    configs.put("batch.size", "16384")
    configs.put("linger.ms", "10")
    configs.put("compression.type", "lz4")
    
    KafkaProducer producer = new KafkaProducer(configs)
    props.put("kafkaProducer", producer)
}

try {
    KafkaProducer producer = props.get("kafkaProducer")
    
    // Create message
    String key = "key-" + ctx.getThreadNum() + "-" + vars.getIteration()
    String value = "message-" + System.currentTimeMillis()
    
    // Send message
    ProducerRecord record = new ProducerRecord("test-topic", key, value)
    RecordMetadata metadata = producer.send(record).get()
    
    // Mark as success
    SampleResult.setResponseOK()
    SampleResult.setResponseMessage("Message sent to partition " + metadata.partition())
    
} catch (Exception e) {
    SampleResult.setSuccessful(false)
    SampleResult.setResponseMessage("Error: " + e.getMessage())
}
```

**3. Add JSR223 PostProcessor (Cleanup):**
```groovy
// Close producer when test ends
if (ctx.getThreadNum() == 0 && vars.getIteration() == 0) {
    if (props.get("kafkaProducer")) {
        props.get("kafkaProducer").close()
        props.remove("kafkaProducer")
    }
}
```

### Step 3.3: Add Listeners for Results

Add these listeners to your test plan:
1. **View Results Tree** - For debugging
2. **Summary Report** - For quick overview
3. **Response Time Graph** - For visualization
4. **Aggregate Report** - For detailed statistics

### Step 3.4: Run Load Tests

**Test Scenario 1: Baseline Performance**
```
Threads: 10
Ramp-up: 10s
Duration: 60s
Message Size: 1KB
Expected: 1000+ msgs/sec
```

**Test Scenario 2: Peak Load**
```
Threads: 50
Ramp-up: 30s
Duration: 300s
Message Size: 1KB
Expected: 5000+ msgs/sec
```

**Test Scenario 3: Stress Test**
```
Threads: 100
Ramp-up: 60s
Duration: 600s
Message Size: 5KB
Expected: System limits
```

---

## Phase 4: Performance Analysis & Optimization

### Step 4.1: Establish Baseline

Before any optimization, run baseline tests:

```bash
# 1. Run JMeter test with default config
./run-baseline-test.sh

# 2. Document baseline metrics
echo "Baseline Results:" > baseline.txt
echo "Throughput: $(grep 'Throughput' jmeter-results.csv)" >> baseline.txt
echo "Avg Latency: $(grep 'Average' jmeter-results.csv)" >> baseline.txt
echo "Consumer Lag: $(check-consumer-lag.sh)" >> baseline.txt
```

### Step 4.2: Optimization Iterations

**Iteration 1: Optimize Producer**

Change configuration:
```yaml
spring:
  kafka:
    producer:
      batch-size: 65536
      linger-ms: 10
      compression-type: lz4
      buffer-memory: 67108864
```

Run test → Compare results → Keep or revert

**Iteration 2: Optimize Consumer**

```yaml
spring:
  kafka:
    consumer:
      fetch-min-size: 1048576
      fetch-max-wait: 500
      max-poll-records: 500
    listener:
      concurrency: 5
```

Run test → Compare results → Keep or revert

**Iteration 3: Optimize Broker (if you control broker)**

```properties
num.network.threads=8
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
```

### Step 4.3: Performance Comparison Script

```bash
#!/bin/bash
# compare-performance.sh

echo "Configuration,Throughput,Avg Latency,P95 Latency,Consumer Lag"

for config in baseline optimized-producer optimized-consumer optimized-all; do
    # Apply configuration
    apply_config $config
    
    # Run test
    ./run-jmeter-test.sh
    
    # Extract metrics
    throughput=$(extract_metric "throughput")
    avg_latency=$(extract_metric "avg_latency")
    p95_latency=$(extract_metric "p95_latency")
    consumer_lag=$(check_consumer_lag)
    
    echo "$config,$throughput,$avg_latency,$p95_latency,$consumer_lag"
done
```

---

## Real-World Test Scenarios

### Scenario 1: E-commerce Order Processing

**Setup:**
```java
@Service
public class OrderEventProducer {
    public void publishOrderEvent(Order order) {
        OrderEvent event = new OrderEvent(
            order.getId(),
            order.getCustomerId(),
            order.getItems(),
            order.getTotalAmount()
        );
        kafkaTemplate.send("orders", order.getId(), event);
    }
}
```

**Test Plan:**
- Simulate 1000 orders/minute
- Message size: 2-5KB
- Peak hours: 10x normal load
- Success criteria: < 100ms p95 latency, zero message loss

**JMeter Configuration:**
```groovy
// Simulate realistic order data
def orderData = [
    orderId: UUID.randomUUID().toString(),
    customerId: "CUST-" + (1..10000).random(),
    items: (1..5).collect { [
        productId: "PROD-" + (1..1000).random(),
        quantity: (1..5).random(),
        price: (10..1000).random()
    ]},
    timestamp: System.currentTimeMillis()
]

String jsonData = new groovy.json.JsonBuilder(orderData).toString()
```

### Scenario 2: IoT Sensor Data Streaming

**Setup:**
```java
@KafkaListener(topics = "sensor-data", concurrency = "10")
public void processSensorData(SensorReading reading) {
    // Process sensor data
    processMetrics(reading);
}
```

**Test Plan:**
- 10,000 devices sending data every 10 seconds
- Message size: 500 bytes
- 24/7 operation
- Success criteria: Consumer lag < 1000 messages

### Scenario 3: Log Aggregation System

**Setup:**
```yaml
spring:
  kafka:
    producer:
      compression-type: snappy  # Good for logs
      batch-size: 100000
      linger-ms: 100
```

**Test Plan:**
- High volume: 50,000 logs/second
- Variable message sizes: 200 bytes - 2KB
- Burst traffic patterns
- Success criteria: No data loss, < 5s p99 latency

---

## Performance Validation Checklist

### Pre-Test Checklist
- [ ] Kafka cluster is healthy
- [ ] All topics are created with correct partitions
- [ ] Monitoring tools are running
- [ ] Baseline metrics documented
- [ ] Test data prepared

### During Test Checklist
- [ ] Monitor CPU/Memory usage
- [ ] Watch consumer lag in real-time
- [ ] Check for errors in application logs
- [ ] Verify message delivery
- [ ] Monitor network I/O

### Post-Test Analysis
- [ ] Compare against baseline
- [ ] Document throughput achieved
- [ ] Analyze latency percentiles (p50, p95, p99)
- [ ] Check for any message loss
- [ ] Review error rates
- [ ] Identify bottlenecks

---

## Common Issues and Solutions

### Issue 1: High Consumer Lag
**Symptoms:** Messages piling up in topics
**Solutions:**
1. Increase consumer concurrency
2. Optimize message processing logic
3. Add more consumer instances
4. Increase partition count

### Issue 2: Low Throughput
**Symptoms:** Can't reach expected msgs/sec
**Solutions:**
1. Increase batch size
2. Tune linger.ms
3. Enable compression
4. Check network bandwidth

### Issue 3: High Latency
**Symptoms:** p95/p99 latency too high
**Solutions:**
1. Reduce batch size
2. Decrease linger.ms
3. Optimize processing logic
4. Check for blocking operations

### Issue 4: Memory Issues
**Symptoms:** OutOfMemoryError or high GC
**Solutions:**
1. Reduce fetch-max-bytes
2. Limit max.poll.records
3. Increase JVM heap size
4. Fix memory leaks in processing

---

## Quick Start Script

```bash
#!/bin/bash
# quick-start-perf-test.sh

echo "Starting Spring Kafka Performance Test..."

# 1. Start infrastructure
echo "Starting Docker containers..."
docker-compose up -d

# 2. Wait for Kafka to be ready
echo "Waiting for Kafka..."
sleep 10

# 3. Create test topic
kafka-topics.sh --create --topic test-topic \
  --partitions 10 --replication-factor 1 \
  --bootstrap-server localhost:9092

# 4. Start Spring Boot app
echo "Starting Spring Boot application..."
./mvnw spring-boot:run &
APP_PID=$!

# 5. Wait for app to be ready
sleep 20

# 6. Run JMeter test
echo "Running JMeter load test..."
jmeter -n -t kafka-load-test.jmx -l results.jtl

# 7. Generate report
echo "Generating HTML report..."
jmeter -g results.jtl -o report/

# 8. Show summary
echo "Test complete! Results in report/ directory"
echo "Access Grafana at http://localhost:3000"
echo "Access Prometheus at http://localhost:9090"

# Cleanup
kill $APP_PID
```

---

## Next Steps

1. **Start with Phase 1** - Get integration tests working
2. **Set up monitoring (Phase 2)** - Before load testing
3. **Run baseline tests (Phase 3)** - Document current performance
4. **Optimize iteratively (Phase 4)** - One change at a time
5. **Implement real scenarios** - Test with production-like data

Remember: **Measure first, optimize second!**
