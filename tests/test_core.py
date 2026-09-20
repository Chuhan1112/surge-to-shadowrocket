from converter.core import convert_surge_to_shadowrocket


# ── [Map Local] ──────────────────────────────────────────────────────────────

def test_map_local_header_preserved():
    result = convert_surge_to_shadowrocket("[Map Local]\n")
    assert "[Map Local]" in result


def test_map_local_status_code_stripped():
    content = "[Map Local]\n^https?://example.com/api data-type=text data=\"{}\" status-code=200\n"
    result = convert_surge_to_shadowrocket(content)
    assert "status-code" not in result
    assert "^https?://example.com/api" in result
    assert 'data-type=text' in result


def test_map_local_without_status_code_unchanged():
    content = "[Map Local]\n^https?://example.com/img data-type=tiny-gif\n"
    result = convert_surge_to_shadowrocket(content)
    assert "^https?://example.com/img data-type=tiny-gif" in result


def test_map_local_comment_preserved():
    content = "[Map Local]\n# this is a comment\n^https?://example.com/ data-type=tiny-gif status-code=200\n"
    result = convert_surge_to_shadowrocket(content)
    assert "# this is a comment" in result


# ── [Rule] ───────────────────────────────────────────────────────────────────

def test_rule_simple_domain_suffix_preserved():
    content = "[Rule]\nDOMAIN-SUFFIX,example.com,REJECT\n"
    result = convert_surge_to_shadowrocket(content)
    assert "DOMAIN-SUFFIX,example.com,REJECT" in result


def test_rule_compound_and_dropped():
    content = "[Rule]\nAND,((PROTOCOL,QUIC),(DOMAIN-SUFFIX,example.com)),REJECT\n"
    result = convert_surge_to_shadowrocket(content)
    assert "AND," not in result


def test_rule_compound_or_dropped():
    content = "[Rule]\nOR,((DOMAIN-SUFFIX,a.com),(DOMAIN-SUFFIX,b.com)),REJECT\n"
    result = convert_surge_to_shadowrocket(content)
    assert "OR," not in result


# ── [Script] ─────────────────────────────────────────────────────────────────

def test_script_spacing_normalised():
    content = "[Script]\ns1 = type = http-response, pattern = ^https?://api.example.com, script-path=test.js\n"
    result = convert_surge_to_shadowrocket(content)
    script_body = result.split("[Script]")[1]
    assert " = " not in script_body
    assert ",  " not in script_body


def test_script_engine_field_removed():
    content = "[Script]\ns1 = type=http-response,pattern=^https?://a.com,engine=webview,script-path=test.js\n"
    result = convert_surge_to_shadowrocket(content)
    assert "engine=" not in result


def test_script_max_size_field_removed():
    content = "[Script]\ns1 = type=http-response,pattern=^https?://a.com,max-size=-1,script-path=test.js\n"
    result = convert_surge_to_shadowrocket(content)
    assert "max-size=" not in result


def test_script_binary_body_mode_normalised():
    content = "[Script]\ns1 = type=http-response,pattern=^https?://a.com,binary-body-mode=1,script-path=test.js\n"
    result = convert_surge_to_shadowrocket(content)
    assert "binary-body-mode=true" in result
    assert "binary-body-mode=1" not in result


# ── General ──────────────────────────────────────────────────────────────────

def test_comments_and_blank_lines_preserved():
    content = "# comment\n\n[General]\nname = Test\n"
    result = convert_surge_to_shadowrocket(content)
    assert "# comment" in result
    assert "\n\n" in result


def test_url_rewrite_unchanged():
    content = "[URL Rewrite]\n^https?://example.com/ads - reject\n# comment\n"
    result = convert_surge_to_shadowrocket(content)
    assert "^https?://example.com/ads - reject" in result
    assert "# comment" in result

