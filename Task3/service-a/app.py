"""Service A - Order Service
Calls Service B (Calculation Service) and demonstrates distributed tracing
"""
import os
import requests
from flask import Flask, jsonify

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure OpenTelemetry
resource = Resource.create({"service.name": "service-a-orders"})
provider = TracerProvider(resource=resource)

otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "simplest-collector:4317"),
    insecure=True
)
processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

app = Flask(__name__)

# Auto-instrument Flask and requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

SERVICE_B_URL = os.getenv("SERVICE_B_URL", "http://service-b:8081")


@app.route("/")
def index():
    """Main endpoint - creates order and calls calculation service"""
    with tracer.start_as_current_span("create-order") as span:
        # Simulate order creation
        order_id = "ORD-12345"
        span.set_attribute("order.id", order_id)
        span.set_attribute("order.status", "INITIATED")

        # Call Service B for price calculation
        with tracer.start_as_current_span("call-calculation-service"):
            try:
                response = requests.get(f"{SERVICE_B_URL}/calculate?order_id={order_id}")
                price = response.json().get("price", 0)
                span.set_attribute("order.price", price)
            except Exception as e:
                span.record_exception(e)
                price = 0

        return jsonify({
            "service": "service-a (Order Service)",
            "order_id": order_id,
            "price": price,
            "status": "Order created and price calculated",
            "trace_info": "Check Jaeger UI for distributed trace"
        })


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
