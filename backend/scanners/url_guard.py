import ipaddress
import socket
from urllib.parse import urlsplit

from config import Config

BLOCKED_METADATA_HOSTS = {
    "169.254.169.254",
    "metadata.google.internal",
    "metadata.goog",
    "instance-data",
    "100.100.100.200",
    "fd00:ec2::254",
    "169.254.170.2",
}


class TargetValidationError(ValueError):
    pass


def normalize_target(raw_url):
    if not isinstance(raw_url, str) or not raw_url.strip():
        raise TargetValidationError("Target URL is required")
    target = raw_url.strip()
    if " " in target or "\\" in target:
        raise TargetValidationError("Target URL contains invalid characters")
    if not target.lower().startswith(("http://", "https://")):
        target = "http://" + target.lstrip("/")
    parts = urlsplit(target)
    if parts.scheme.lower() not in {"http", "https"}:
        raise TargetValidationError("Only http and https targets are supported")
    if parts.username or parts.password:
        raise TargetValidationError("Credentials in target URLs are not allowed")
    if not parts.hostname:
        raise TargetValidationError("Target URL has no hostname")
    host = parts.hostname.lower().rstrip(".")
    if len(target) > 2048:
        raise TargetValidationError("Target URL is too long")
    try:
        port = parts.port or (443 if parts.scheme.lower() == "https" else 80)
    except ValueError as exc:
        raise TargetValidationError("Invalid port in target URL") from exc
    if not 1 <= port <= 65535:
        raise TargetValidationError("Invalid port in target URL")
    path = parts.path or "/"
    from urllib.parse import urlunsplit

    host_display = f"[{host}]" if ":" in host else host
    if (parts.scheme.lower() == "http" and port != 80) or (parts.scheme.lower() == "https" and port != 443):
        host_display = f"{host_display}:{port}"
    normalized = urlunsplit((parts.scheme.lower(), host_display, path, parts.query, ""))
    return normalized, host, port, parts.scheme.lower()


def _is_loopback(ip):
    return ip.is_loopback


def _is_private_or_reserved(ip):
    return ip.is_private or ip.is_reserved or ip.is_link_local or ip.is_multicast or ip.is_unspecified


def check_ip(ip_text, host, port):
    try:
        ip = ipaddress.ip_address(ip_text)
    except ValueError as exc:
        raise TargetValidationError("Target resolved to an invalid IP address") from exc
    if host.lower() in BLOCKED_METADATA_HOSTS or str(ip) in BLOCKED_METADATA_HOSTS:
        raise TargetValidationError("Cloud metadata endpoints are blocked")
    if ip.version == 6 and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped

    lab_host = host.lower() in {h.lower() for h in Config.ALLOWED_LAB_HOSTS}
    lab_port_ok = port in Config.ALLOWED_LAB_PORTS

    if Config.LOCAL_LAB_MODE and lab_host:
        if not lab_port_ok:
            raise TargetValidationError(
                f"Port {port} is not in the local lab allowlist ({', '.join(map(str, Config.ALLOWED_LAB_PORTS))})"
            )
        return ip

    if _is_loopback(ip) or _is_private_or_reserved(ip):
        raise TargetValidationError("Private, loopback or internal IP addresses are blocked unless local lab mode is enabled for that host")

    if not Config.ALLOW_EXTERNAL_TARGETS:
        if host.lower() not in Config.PUBLIC_TARGET_ALLOWLIST:
            raise TargetValidationError(
                "External scanning is disabled. Enable lab mode with an authorized local target or configure PUBLIC_TARGET_ALLOWLIST"
            )
        return ip

    if not ip.is_global:
        raise TargetValidationError("Target IP is not a public global address")
    return ip


def resolve_target(host, port):
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise TargetValidationError(f"Could not resolve target host: {host}") from exc
    if not infos:
        raise TargetValidationError(f"Could not resolve target host: {host}")
    ips = []
    for info in infos:
        ip_text = info[4][0]
        check_ip(ip_text, host, port)
        if ip_text not in ips:
            ips.append(ip_text)
    return ips


def validate_target(raw_url):
    normalized, host, port, scheme = normalize_target(raw_url)
    ips = resolve_target(host, port)
    return {
        "url": normalized,
        "host": host,
        "port": port,
        "scheme": scheme,
        "resolved_ips": ips,
        "netloc": f"{host}:{port}",
    }
