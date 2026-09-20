from converter.core import convert_surge_to_shadowrocket


MAP_LOCAL_MODULE = """\
[General]
name = TestModule

[Map Local]
^https?://example.com/api/ads - reject-dict
^https?://example.com/track data/empty.json

[Script]
script1 = type=http-response, pattern=^https?://api.example.com, script-path=test.js
"""

URL_REWRITE_MODULE = """\
[General]
name = TestModule

[URL Rewrite]
^https?://example.com/api/ads - reject-dict
^https?://example.com/track - reject-dict
"""

SCRIPT_MODULE = """\
[Script]
s1 = type = http-response, pattern = ^https?://api.example.com, script-path=test.js
s2 = type=http-request,  pattern=^https?://other.com,  script-path=other.js
"""


def test_map_local_header_replaced():
    result = convert_surge_to_shadowrocket("[Map Local]\n")
    assert "[URL Rewrite]" in result
    assert "[Map Local]" not in result


def test_map_local_rule_converted_to_reject_dict():
    content = "[Map Local]\n^https?://example.com/ads some-response\n"
    result = convert_surge_to_shadowrocket(content)
    assert "^https?://example.com/ads - reject-dict" in result


def test_url_rewrite_header_preserved():
    content = "[URL Rewrite]\n^https?://example.com/ads - reject-dict\n"
    result = convert_surge_to_shadowrocket(content)
    assert result.count("[URL Rewrite]") == 1
    assert "[Map Local]" not in result


def test_url_rewrite_rule_converted():
    content = "[URL Rewrite]\n^https?://example.com/track data/empty.json\n"
    result = convert_surge_to_shadowrocket(content)
    assert "^https?://example.com/track - reject-dict" in result


def test_script_spacing_normalized():
    content = "[Script]\ns1 = type = http-response, pattern = ^https?://api.example.com, script-path=test.js\n"
    result = convert_surge_to_shadowrocket(content)
    assert " = " not in result.split("[Script]")[1]
    assert ",  " not in result


def test_comments_and_blank_lines_preserved():
    content = "# comment\n\n[General]\nname = Test\n"
    result = convert_surge_to_shadowrocket(content)
    assert "# comment" in result
    assert "\n\n" in result


def test_non_url_lines_in_url_rewrite_unchanged():
    content = "[URL Rewrite]\n# this is a comment line\nsome-other-config = value\n"
    result = convert_surge_to_shadowrocket(content)
    assert "# this is a comment line" in result
    assert "some-other-config = value" in result


def test_full_map_local_module():
    result = convert_surge_to_shadowrocket(MAP_LOCAL_MODULE)
    assert "[URL Rewrite]" in result
    assert "[Map Local]" not in result
    assert "^https?://example.com/api/ads - reject-dict" in result
    assert "[General]" in result
    assert "[Script]" in result
