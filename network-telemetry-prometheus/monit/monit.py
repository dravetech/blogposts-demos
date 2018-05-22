from nornir.core import InitNornir
from nornir.plugins.tasks.networking import napalm_get

from flask import Flask, Response

app = Flask(__name__)

# Nornir will be instantiated globally to persist the connection
nr = InitNornir(config_file="/monit/config.yaml", num_workers=100)


def _prometheus_metric(name, value, **kwargs):
    """ Emit a metric in prometheus format. """
    labels = ", ".join(f'{k}="{v}"' for k, v in kwargs.items())
    return f"{name} {{{labels}}} {value}\n"


def _napalm_iface_counters_to_prometheus(device_name, interface_counters):
    """
    Transform interface metrics gathered by napalm into a format
    suitable for prometheus.
    """
    metrics = ""
    for interface, counters in interface_counters.items():
        for counter, value in counters.items():
            c = counter.split("_")
            direction = c[0]
            metric = "_".join(c[1:])
            metrics += _prometheus_metric(
                name="network_device_interface_counter",
                value=value,
                net_device=device_name,
                interface=interface,
                direction=direction,
                metric=metric,
            )
    return metrics


def _napalm_bgp_neighbors_to_prometheus(device_name, bgp_neighbors):
    """
    Transform bgp metrics gathered by napalm into a format
    suitable for prometheus.
    """
    metrics = ""
    for peer, peer_data in bgp_neighbors["global"]["peers"].items():
        metrics += _prometheus_metric(
            name="bgp_session_up",
            value=int(peer_data["is_up"]),
            net_device=device_name,
            peer=peer,
        )
        for counter, value in peer_data["address_family"]["ipv4"].items():
            metrics += _prometheus_metric(
                name=f"bgp_prefixes",
                value=value,
                net_device=device_name,
                peer=peer,
                metric=counter,
            )
    return metrics


def _get_metrics(task):
    """
    Nornir job to gather the metrics using `napalm_get` task
    and transform napalm metrics into prometheus metrics.
    """
    result = task.run(
            task=napalm_get,
            getters=["interfaces_counters", "bgp_neighbors"]
    )
    metrics = _napalm_iface_counters_to_prometheus(
        task.host.name, result.result["interfaces_counters"]
    )
    metrics += _napalm_bgp_neighbors_to_prometheus(
        task.host.name, result.result["bgp_neighbors"]
    )
    return metrics


@app.route("/metrics")
def metrics():
    """
    /metrics endpoint

    Gather metrics from the network and presents it to prometheus
    """
    results = nr.run(
            task=_get_metrics,      # nornir task to run
            on_failed=True,         # Run the job is previous executions failed
    )
    metrics = "\n".join([r.result for r in results.values()])
    return Response(metrics, mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
