from app.configs.logging import logging
from app.configs.tools import SonarConfigurations, SonarDomains, GitConfigurations
from app.telemetry import Instrumentation, should_instrumentation
from opentelemetry.sdk.resources import SERVICE_NAME

from dotenv import load_dotenv
import os


if should_instrumentation():
    resources_dict = {
        SERVICE_NAME: 'gen.ai.tutorials',
    }

    Instrumentation(grpc=True, resource_attributes_dict=resources_dict, 
                    traces_exporter_url=os.environ['OTLP_TRACES_HOST'])