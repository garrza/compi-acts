from typing import Any, Callable


class LexError(Exception):
    text: str


class LexToken:
    type: str
    value: Any
    lineno: int
    lexpos: int
    lexer: Lexer


class Lexer:
    lineno: int
    lexpos: int

    def input(self, s: str) -> None: ...
    def token(self) -> LexToken | None: ...
    def skip(self, n: int) -> None: ...
    def begin(self, state: str) -> None: ...
    def push_state(self, state: str) -> None: ...
    def pop_state(self) -> None: ...
    def current_state(self) -> str: ...
    def clone(self, object: Any | None = None) -> Lexer: ...


def lex(
    *,
    module: Any | None = None,
    object: Any | None = None,
    debug: bool = False,
    reflags: int = ...,
    debuglog: Any | None = None,
    errorlog: Any | None = None,
) -> Lexer: ...


def TOKEN(r: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...
def runmain(lexer: Lexer | None = None, data: str | None = None) -> None: ...
