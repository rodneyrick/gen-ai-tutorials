FROM grafana/grafana:10.4.1

# Config Datasources
ADD datasource.yml /etc/grafana/provisioning/datasources/

ENV GF_AUTH_ANONYMOUS_ENABLED true
ENV GF_AUTH_ANONYMOUS_ORG_ROLE Admin

# ADD grafana.ini /etc/grafana/