from langflow_client.user_file import UserFile


def test_user_file_parses_dates():
    user_file_data = {
        "id": "b8fdff49-024e-48e2-acdd-7cd1e4d32d46",
        "name": "bodi",
        "path": "579f0128-52e1-4cf7-b5d4-5091d2697f1e/b8fdff49-024e-48e2-acdd-7cd1e4d32d46.jpg",
        "size": 29601,
        "provider": None,
        "created_at": "2025-06-11T07:34:43.603Z",
        "updated_at": "2025-06-11T07:34:43.603Z",
        "user_id": "user_id1234",
    }

    uf = UserFile(user_file_data)
    assert uf.created_at is not None
    assert uf.updated_at is not None 