"""Service B - Calculation Service
Receives requests from Service A and calculates price
"""
import os
import time
import random
from flask import Flask, jsonify, request

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure OpenTelemetry
resource = Resource.create({"service.name": "service-b-calculation"})
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

# Auto-instrument Flask
FlaskInstrumentor().instrument_app(app)


@app.route("/calculate")
def calculate():
    """Calculate price for the order"""
    order_id = request.args.get("order_id", "unknown")

    with tracer.start_as_current_span("calculate-price") as span:
        span.set_attribute("order.id", order_id)

        # Simulate price calculation (like MES does for 3D models)
        with tracer.start_as_current_span("fetch-model-data"):
            time.sleep(0.1)  # Simulate DB/S3 call
            model_complexity = random.randint(1000, 100000)  # polygons
            span.set_attribute("model.complexity", model_complexity)

        with tracer.start_as_current_span("compute-materials-cost"):
            time.sleep(0.05)
            materials_cost = random.uniform(100, 1000)

        with tracer.start_as_current_span("compute-labor-cost"):
            time.sleep(0.05)
            labor_cost = random.uniform(50, 500)

        total_price = round(materials_cost + labor_cost, 2)
        span.set_attribute("price.total", total_price)
        span.set_attribute("price.materials", round(materials_cost, 2))
        span.set_attribute("price.labor", round(labor_cost, 2))

        return jsonify({
            "service": "service-b (Calculation Service)",
            "order_id": order_id,
            "price": total_price,
            "breakdown": {
                "materials": round(materials_cost, 2),
                "labor": round(labor_cost, 2)
            }
        })


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
