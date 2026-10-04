import json

from confluent_kafka import Consumer

# ==========================================
# Kafka consumer configuration
# ==========================================

consumer = Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id": "insurance-claims-dlq-consumer",
    "auto.offset.reset": "earliest",
})

# ==========================================
# Subscribe to the DLQ topic
# ==========================================

consumer.subscribe(["insurance.claims.dlq"])

print("DLQ consumer started.")
print("Waiting for rejected claims...")


# ==========================================
# Read rejected messages
# ==========================================

try:
    while True:
        message = consumer.poll(1.0)

        # No message received
        if message is None:
            continue

        # Kafka reported an error
        if message.error():
            print(f"Kafka error: {message.error()}")
            continue

        # ==========================================
        # Convert JSON message to Python dictionary
        # ==========================================

        claim = json.loads(
            message.value().decode("utf-8")
        )

        print("\nRejected claim:")
        print(json.dumps(claim, indent=2))

        # ==========================================
        # Display validation errors
        # ==========================================

        print("\nValidation errors:")

        for error in claim.get("validation_errors", []):
            print(f"  - {error}")

except KeyboardInterrupt:
    print("\nDLQ consumer stopped by user.")


finally:
    consumer.close()
    print("DLQ consumer closed.")