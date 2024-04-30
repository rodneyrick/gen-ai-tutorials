from genai_core.telemetry.instrumentation import (
    Instrumentation, 
    TraceInstruments, 
    should_instrumentation, 
    instrumented_trace)
from opentelemetry.sdk.resources import SERVICE_NAME
from dotenv import load_dotenv
import os

load_dotenv()

if should_instrumentation():
    resources_dict = {
        SERVICE_NAME: 'genai',
    }

    Instrumentation(grpc=True, resource_attributes_dict=resources_dict, 
                    traces_exporter_url=os.environ['OTLP_TRACES_HOST'])


__all__ = [
    "Instrumentation",
    "TraceInstruments",
    "should_instrumentation",
    "instrumented_trace"
]