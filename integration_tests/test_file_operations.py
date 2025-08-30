"""
Integration tests demonstrating Langflow client file operations.
These tests serve as examples of how to use the file-related features.
"""
import os
from langflow_client import UserFile


def test_file_upload(client, test_file_path):
    """
    Example: Uploading a file to Langflow.
    
    This demonstrates how to upload a file that can be used
    in flows or stored for later use.
    """
    # Read file content
    with open(test_file_path, "rb") as f:
        # Upload file using the correct method signature
        response = client.files.upload(f, filename=os.path.basename(test_file_path))
    
    assert isinstance(response, UserFile)
    # The server may modify the filename (e.g. add counter for duplicates)
    # so just check that the base name is contained in the response name
    base_name = os.path.splitext(os.path.basename(test_file_path))[0]
    assert base_name in response.name
    assert response.id is not None


def test_list_files(client, test_file_path):
    """
    Example: Listing uploaded files.
    
    This shows how to retrieve a list of all files that have
    been uploaded to Langflow.
    """
    # First upload a file to ensure we have something to list
    with open(test_file_path, "rb") as f:
        client.files.upload(f, filename=os.path.basename(test_file_path))
    
    # List all files
    files = client.files.list()
    
    assert isinstance(files, list)
    assert len(files) > 0
    assert all(isinstance(f, UserFile) for f in files)


def test_file_lifecycle(client, test_file_path):
    """
    Example: Complete file lifecycle operations.
    
    This demonstrates the full lifecycle of a file:
    upload -> list -> delete -> verify deletion
    """
    # Upload new file
    with open(test_file_path, "rb") as f:
        uploaded = client.files.upload(f, filename=os.path.basename(test_file_path))
    
    file_id = uploaded.id
    assert file_id is not None
    
    # List files and verify our file is there
    files = client.files.list()
    assert any(f.id == file_id for f in files)
    
    # Delete the file
    client.files.delete(file_id)
    
    # List again and verify file is gone
    updated_files = client.files.list()
    assert not any(f.id == file_id for f in updated_files) 