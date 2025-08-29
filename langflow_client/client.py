from __future__ import annotations

import platform
import sys
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, Mapping, Optional
from urllib.parse import urlencode, urljoin

import requests

from .errors import LangflowError, LangflowRequestError
from .ndjson import iter_ndjson_objects


@dataclass
class LangflowClientOptions:
    base_url: str
    api_key: Optional[str] = None
    session: Optional[requests.Session] = None
    default_headers: Optional[Mapping[str, str]] = None


class LangflowClient:
    def __init__(self, opts: LangflowClientOptions | Mapping[str, Any]):
        if isinstance(opts, Mapping):
            opts = LangflowClientOptions(**opts)
        
        if not opts.base_url or opts.base_url.strip() == "":
            raise TypeError("baseUrl is required")
            
        self.base_url = opts.base_url
        self.base_path = "/api"
        self.api_key = opts.api_key
        self.session = opts.session or requests.Session()
        self.default_headers: Dict[str, str] = dict(opts.default_headers or {})

        if "User-Agent" not in {k.title(): v for k, v in self.default_headers.items()}:
            self.default_headers["User-Agent"] = self._get_user_agent()

        # sub-clients are set lazily to avoid circular imports
        from .logs import Logs
        from .files import Files

        self.logs = Logs(self)
        self.files = Files(self)

    def _get_user_agent(self) -> str:
        try:
            from importlib.metadata import version

            pkg_version = version("langflow-client")
        except Exception:
            pkg_version = "0.0.0"
        return (
            f"langflow-client-python/{pkg_version} "
            f"({platform.system()} {platform.machine()}) "
            f"python/{platform.python_version()}"
        )

    def _set_api_key(self, headers: Dict[str, str]):
        if not self.api_key:
            return
        headers["x-api-key"] = self.api_key

    def _merge_headers(self, headers: Optional[Mapping[str, str]]) -> Dict[str, str]:
        merged: Dict[str, str] = {}
        # default headers
        for k, v in self.default_headers.items():
            merged[k] = v
        # call specific
        for k, v in (headers or {}).items():
            merged[k] = v
        # api key
        self._set_api_key(merged)
        return merged

    def _set_url(self, path: str) -> str:
        if path in ("/logs", "/logs-stream"):
            return urljoin(self.base_url, path)
        return urljoin(self.base_url, f"{self.base_path}{path}")

    def flow(self, flow_id: str, tweaks: Optional[Dict[str, Any]] = None):
        from .flow import Flow

        return Flow(self, flow_id, tweaks or {})

    def request(
        self,
        *,
        path: str,
        method: str,
        query: Optional[Mapping[str, str]] = None,
        body: Optional[Any] = None,
        headers: Optional[Mapping[str, str]] = None,
        signal: Optional[Any] = None,
        timeout: Optional[float | tuple] = None,
    ) -> Any:
        url = self._set_url(path)
        if query:
            url = f"{url}?{urlencode(query)}"
        req_headers = self._merge_headers(headers)
        try:
            if hasattr(signal, "throw_if_aborted"):
                signal.throw_if_aborted()
            resp = self.session.request(
                method,
                url,
                data=body if isinstance(body, (str, bytes)) else None,
                json=None,
                headers=req_headers,
                files=body if isinstance(body, dict) and any(
                    isinstance(v, tuple) for v in body.values()
                )
                else None,
                timeout=timeout,
            )
            if not resp.ok:
                raise LangflowError(f"{resp.status_code} - {resp.reason}", resp)
            if hasattr(signal, "throw_if_aborted"):
                signal.throw_if_aborted()
            return resp.json()
        except LangflowError:
            raise
        except Exception as error:  # transport-level
            message = str(error)
            raise LangflowRequestError(message, error)

    def stream(
        self,
        *,
        path: str,
        method: str,
        body: Optional[Any] = None,
        headers: Optional[Mapping[str, str]] = None,
        signal: Optional[Any] = None,
        timeout: Optional[float | tuple] = None,
    ) -> Iterator[dict]:
        # ensure stream=true for flow run endpoint
        url = self._set_url(path)
        sep = "?" if "?" not in url else "&"
        url = f"{url}{sep}stream=true"
        req_headers = self._merge_headers(headers)
        try:
            if hasattr(signal, "throw_if_aborted"):
                signal.throw_if_aborted()
            resp = self.session.request(
                method,
                url,
                data=body if isinstance(body, (str, bytes)) else None,
                headers=req_headers,
                stream=True,
                timeout=timeout,
            )
            if not resp.ok:
                raise LangflowError(f"{resp.status_code} - {resp.reason}", resp)
            # Iterate over lines and parse NDJSON
            for obj in iter_ndjson_objects(resp.iter_lines(decode_unicode=True)):
                if hasattr(signal, "throw_if_aborted"):
                    signal.throw_if_aborted()
                yield obj
        except LangflowError:
            raise
        except Exception as error:
            message = str(error)
            raise LangflowRequestError(message, error) 