FROM prom/prometheus:v2.47.0

# Health Check -> http://localhost:<port>/-/healthy
ADD prometheus.yml /etc/prometheus


CMD ["--web.listen-address=:9090", "--config.file=/etc/prometheus/prometheus.yml", "--web.route-prefix=/prometheus/", "--web.external-url=/prometheus/"]
