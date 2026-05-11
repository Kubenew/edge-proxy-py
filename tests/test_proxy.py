from edge_proxy_py.proxy import _filter_headers, HOP_BY_HOP_HEADERS


def test_filter_headers_removes_hop_by_hop():
    headers = {"host": "example.com", "connection": "keep-alive", "content-type": "application/json"}
    filtered = _filter_headers(headers)
    assert "host" in filtered
    assert "connection" not in filtered
    assert "content-type" in filtered


def test_filter_headers_case_insensitive():
    headers = {"Connection": "keep-alive", "Content-Type": "text/plain"}
    filtered = _filter_headers(headers)
    assert "Connection" not in filtered
    assert "Content-Type" in filtered


def test_filter_headers_all_hop_by_hop():
    headers = {h: "x" for h in HOP_BY_HOP_HEADERS}
    filtered = _filter_headers(headers)
    assert len(filtered) == 0


def test_filter_headers_empty():
    assert _filter_headers({}) == {}
