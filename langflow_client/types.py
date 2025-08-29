from __future__ import annotations

from typing import Any, Dict, Mapping, MutableMapping, TypedDict, Union


Tweak = Dict[str, Union[str, int, float, bool, None]]
Tweaks = Dict[str, Union[Tweak, str]]


class TokenStreamEvent(TypedDict):
    event: str  # "token"
    data: Dict[str, str]


class AddMessageStreamEvent(TypedDict):
    event: str  # "add_message"
    data: Any


class EndStreamEvent(TypedDict):
    event: str  # "end"
    data: Dict[str, Any]


StreamEvent = Union[TokenStreamEvent, AddMessageStreamEvent, EndStreamEvent] 