from app.configs.logging import logging
from app.configs.tools import SonarConfigurations, SonarDomains, GitConfigurations
from app.telemetry import ToolsInstruments, Instrumentation, should_instrumentation

from dotenv import load_dotenv
import os


if should_instrumentation():
    resources_dict = {
        'service.name': 'gen.ai.tutorials',
    }

    instrumentor = Instrumentation(grpc=True, resource_attributes_dict=resources_dict, 
                    traces_exporter_url=os.environ['OTLP_TRACES_HOST'])