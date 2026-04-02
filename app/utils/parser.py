from urllib.parse import urlparse


def parse_uri_data(uri):
    result = urlparse(uri)
    raw_options = [d.split("=") for d in result.query.split("&") if d]
    options = dict(raw_options) if raw_options else dict()
    return result, options
