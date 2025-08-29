from langflow_client.ndjson import iter_ndjson_objects


def test_ndjson_single_object():
    chunks = ["{" + '"test": "value"' + "}"]
    results = list(iter_ndjson_objects(chunks))
    assert results == [{"test": "value"}]


def test_ndjson_multiple_objects():
    chunks = [
        "{" + '"test": "value1"' + "}\n{" + '"test": "value2"' + "}",
    ]
    results = list(iter_ndjson_objects(chunks))
    assert results == [{"test": "value1"}, {"test": "value2"}]


def test_ndjson_partial_across_chunks():
    chunks = ['{"test": "val', 'ue"}\n']
    results = list(iter_ndjson_objects(chunks))
    assert results == [{"test": "value"}]


def test_ndjson_ignores_invalid_lines():
    chunks = ['{"valid": "json"}\ninvalid\n{"also": "valid"}\n']
    results = list(iter_ndjson_objects(chunks))
    assert results == [{"valid": "json"}, {"also": "valid"}]


def test_ndjson_does_not_ignore_strings_inside_json():
    chunks = ['{"valid": "json \ninvalid\n valid"}\n']
    results = list(iter_ndjson_objects(chunks))
    assert results == [{"valid": "json invalid valid"}]


def test_ndjson_empty_input():
    chunks = []
    results = list(iter_ndjson_objects(chunks))
    assert results == []


def test_ndjson_whitespace_between_objects():
    chunks = ['{"test": "value1"}\n\n\n{"test": "value2"}\n']
    results = list(iter_ndjson_objects(chunks))
    assert results == [{"test": "value1"}, {"test": "value2"}] 