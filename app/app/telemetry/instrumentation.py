from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as OTLPgrpcExporter
from opentelemetry.instrumentation.utils import _SUPPRESS_INSTRUMENTATION_KEY
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry import context as context_api
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import get_current_span
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper
from opentelemetry import trace
from typing import Collection
from pathlib import Path
import json
import os

from app.configs import logging
logger = logging.getLogger()

class ToolsInstruments():
    TOOLS_SONAR_ANALYSIS = "tools_sonar_analysis.json"
    TOOLS_SONAR_SCAN = "tools_sonar_scan.json"
    TOOLS_GIT = "tools_git.json"

class Instrumentation():

    def __init__(self, **kwargs):
        self.grpc: bool = kwargs['grpc']
        self.resource_attributes_dict: dict = kwargs['resource_attributes_dict']
        self.traces_exporter_url: str = kwargs['traces_exporter_url']
        self.setting_otlp()

    def setting_otlp(self) -> None:
        resource = Resource.create(attributes=self.resource_attributes_dict)
        tracer = TracerProvider(resource=resource)
        
        if self.grpc:
            logger.debug("Configurando OTLP GRPC Exporter")
            tracer.add_span_processor(
                BatchSpanProcessor(
                    OTLPgrpcExporter(
                        endpoint=self.traces_exporter_url,
                        insecure=True
                    )
                )
            )
       
        trace.set_tracer_provider(tracer)
    
    def setting_instrumentation_tools(self, type):
        Instrumentor().instrument(type=type)

class Instrumentor(BaseInstrumentor):

    def instrumentation_dependencies(self) -> Collection[str]:
        return []
    
    def _instrument(self, **kwargs):
        wrapped_methods = self.load_configuration(kwargs["type"])
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, tracer_provider)
        
        for wrapped_method in wrapped_methods:
            wrap_package = wrapped_method.get("package")
            wrap_object = wrapped_method.get("object")
            wrap_method = wrapped_method.get("method")
            wrap_function_wrapper(
                wrap_package,
                f"{wrap_object}.{wrap_method}" if wrap_object else wrap_method,
                _wrap(tracer, wrapped_method),
            )

    def _uninstrument(self, **kwargs):
        wrapped_methods = self.load_configuration(kwargs["type"])
        for wrapped_method in wrapped_methods:
            wrap_package = wrapped_method.get("package")
            wrap_object = wrapped_method.get("object")
            wrap_method = wrapped_method.get("method")
            unwrap(
                f"{wrap_package}.{wrap_object}" if wrap_object else wrap_package,
                wrap_method,
            )
    
    def load_configuration(self, type):
        p = Path(__file__).with_name(type)
        with open(p, "r") as f:
            wrapped_methods = json.loads(f.read())
            
        return wrapped_methods
    
def _with_tracer_wrapper(func):
    """Helper for providing tracer for wrapper functions."""

    def _with_tracer(tracer, to_wrap):
        def wrapper(wrapped, instance, args, kwargs):
            return func(tracer, to_wrap, wrapped, instance, args, kwargs)

        return wrapper

    return _with_tracer

@_with_tracer_wrapper
def _wrap(tracer, to_wrap, wrapped, instance, args, kwargs):
    """Instruments and calls every function defined in TO_WRAP."""
    
    if context_api.get_value(_SUPPRESS_INSTRUMENTATION_KEY):
        return wrapped(*args, **kwargs)

    config = args[1] if len(args) > 1 else {}
    run_name = config.get("run_name") or instance.get_name()
    name = f"tool.{run_name}" if run_name else to_wrap.get("span_name")

    wrap_type = to_wrap.get("type")

    if wrap_type == "event":
        return set_event(to_wrap, wrapped, args, kwargs)
    
    return set_trace(tracer, to_wrap, wrapped, args, kwargs, name)

def set_trace(tracer, to_wrap, wrapped, args, kwargs, name):
    kind = to_wrap.get("kind") or "tools"
    wrap_method = to_wrap.get("method")
    
    with tracer.start_as_current_span(name) as span:
        span.set_attribute("context", kind)
        span.set_attribute("context.class", name)
        span.set_attribute('method', wrap_method)
        
        attributes = to_wrap.get("attributes")

        if attributes is not None:
            for label, data in attributes.items():
                if isinstance(data, dict):
                    span.set_attribute(label, kwargs[data['value']].value)
                else:
                    span.set_attribute(label, str(kwargs[data]))
        return_value = wrapped(*args, **kwargs)

    return return_value

def set_event(to_wrap, wrapped, args, kwargs):
    wrap_method = to_wrap.get("method")
    attributes = to_wrap.get("attributes")
    
    current_span = get_current_span()
    if current_span is not None:
        if attributes is not None:
            for label, data in attributes.items():
                if isinstance(data, dict):
                    current_span.add_event(wrap_method, attributes={label: kwargs[data['value']].value})
                if isinstance(kwargs[data], list):
                    current_span.add_event(wrap_method, attributes={label: kwargs[data]})
                else:
                    current_span.add_event(wrap_method, attributes={label: str(kwargs[data])})
        else:
            current_span.add_event(wrap_method)
    
    return wrapped(*args, **kwargs)

def should_instrumentation():
    return (
        os.getenv("OTLP_INSTRUMENTATION_DISABLE") or "false"
    ).lower() == "false" or context_api.get_value("override_enable_content_tracing")