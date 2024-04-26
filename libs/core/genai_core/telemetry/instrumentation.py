from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as OTLPgrpcExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry import context as context_api
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import get_current_span
from typing import Callable, Dict, List
from opentelemetry import trace
from functools import wraps
import asyncio
import inspect
import os

from genai_core.logging import logging
logger = logging.getLogger()

attributes_black_list: List[str] = [
    'data',
    'token'
]

class TraceInstruments():
    INSTRUMENTS_EVENT = "event"
    INSTRUMENTS_TRACE = "trace"
    SPAN_KIND_CLIENT = trace.SpanKind.CLIENT
    SPAN_KIND_SERVER = trace.SpanKind.SERVER
    SPAN_KIND_INTERNAL = trace.SpanKind.INTERNAL
    SPAN_KIND_PRODUCER = trace.SpanKind.PRODUCER
    SPAN_KIND_CONSUMER = trace.SpanKind.CONSUMER
    
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

class TracingOptions:
    
    class Attributes:
        @staticmethod
        def function_qualified_name(func: Callable):
            return func.__qualname__.split('.')[0] if '.' in func.__qualname__ else "span.no_name"

        @staticmethod
        def function_attributes(func: Callable, user_attributes, span_parameters,**kwargs):
            attributes = {
                "module": func.__module__,
                "method": func.__name__
            }
            
            if span_parameters:
                for key, value in kwargs.items():
                    if key not in attributes_black_list:
                        if (lambda value: type(value) in {bool, str, bytes, int, float}):
                            value = str(value)
                    
                        attributes[key] = value
            
            if user_attributes is not None:
                for key in user_attributes:
                    attributes[key] = user_attributes[key]
            
            return attributes
        
        default_scheme = function_qualified_name
        attributes = function_attributes
  
    naming_scheme: Callable[[Callable], str] = Attributes.default_scheme
    attributes: Callable[[Callable], str] = Attributes.attributes


def instrumented_trace(_func=None, *,  span_name: str = "", record_exception: bool = True,
               attributes: Dict[str, str] = None, type: TraceInstruments = TraceInstruments.INSTRUMENTS_TRACE,
               kind: TraceInstruments = TraceInstruments.SPAN_KIND_INTERNAL,
               span_parameters: bool = True):

    def span_decorator(func):
        tracer = trace.get_tracer(func.__module__)

        def _set_attributes(span, attributes_dict):
            if attributes_dict:
                for att in attributes_dict:
                    span.set_attribute(att, attributes_dict[att])
                    
        @wraps(func)
        def wrap_with_span_sync(*args, **kwargs):
            name = span_name or TracingOptions.naming_scheme(func)
            span_attributes = TracingOptions.attributes(func, attributes, span_parameters, **kwargs)
            
            def span_event(name, span_attributes, *args, **kwargs):
                current_span = get_current_span()
                if current_span is not None:
                    current_span.add_event(name ,attributes=span_attributes)
                
                return func(*args, **kwargs)
            
            def span(name, span_attributes,  kind, *args, **kwargs):
                with tracer.start_as_current_span(name, record_exception=record_exception, kind=kind) as span:
                    _set_attributes(span, span_attributes)
                    return func(*args, **kwargs)
            
            if type == TraceInstruments.INSTRUMENTS_EVENT:
                return span_event(name, span_attributes, *args, **kwargs)
            
            return span(name, span_attributes, kind, *args, **kwargs)
    
        @wraps(func)
        async def wrap_with_span_async(*args, **kwargs):
            name = span_name or TracingOptions.naming_scheme(func)
            span_attributes = TracingOptions.attributes(func, attributes, span_parameters, **kwargs)
            
            async def span_event(name, span_attributes, *args, **kwargs):
                current_span = get_current_span()
                if current_span is not None:
                    current_span.add_event(name ,attributes=span_attributes)
                
                return await func(*args, **kwargs)
            
            async def span(name, span_attributes,  kind, *args, **kwargs):
                with tracer.start_as_current_span(name, record_exception=record_exception, kind=kind) as span:
                    _set_attributes(span, span_attributes)
                    return await func(*args, **kwargs)
            
            if type == TraceInstruments.INSTRUMENTS_EVENT:
                return await span_event(name, span_attributes, *args, **kwargs)
            
            return await span(name, span_attributes, kind, *args, **kwargs)
        
        wrapper = wrap_with_span_async if asyncio.iscoroutinefunction(func) else wrap_with_span_sync
        wrapper.__signature__ = inspect.signature(func)
        return wrapper
    
    if not should_instrumentation():
        return _func if _func is not None else lambda func: func

    return span_decorator if _func is None else span_decorator(_func)

def should_instrumentation():
    return (
        os.getenv("OTLP_INSTRUMENTATION_DISABLE") or "false"
    ).lower() == "false" or context_api.get_value("override_enable_content_tracing")
  