#!/usr/bin/env python
# Copyright (c) 2012-2024, Cenobit Technologies, Inc. http://cenobit.es/
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# * Neither the name of the Cenobit Technologies nor the names of
#    its contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
import os
import sys
import typing as t
import functools

from flask import Flask

# Python 3.11+
try:
    from typing import Self
except ImportError:  # pragma: no cover
    from typing_extensions import Self

try:
    from flask_jsonrpc import JSONRPC
except ModuleNotFoundError:
    project_dir, project_module_name = os.path.split(os.path.dirname(os.path.realpath(__file__)))
    flask_jsonrpc_project_dir = os.path.join(project_dir, os.pardir, os.pardir, 'src')
    if os.path.exists(flask_jsonrpc_project_dir) and flask_jsonrpc_project_dir not in sys.path:
        sys.path.append(flask_jsonrpc_project_dir)

    from flask_jsonrpc import JSONRPC


class App:
    def index(self: Self, name: str = 'Flask JSON-RPC') -> str:
        return f'Hello {name}'

    @staticmethod
    def greeting(name: str = 'Flask JSON-RPC') -> str:
        return f'Hello {name}'

    @classmethod
    def hello(cls: t.Type[Self], name: str = 'Flask JSON-RPC') -> str:
        return f'Hello {name}'

    def echo(self: Self, string: str, _some: t.Any = None) -> str:  # noqa: ANN401
        return string

    def notify(self: Self, _string: str = None) -> None:
        pass

    def not_allow_notify(self: Self, _string: str = None) -> str:
        return 'Now allow notify'

    def fails(self: Self, n: int) -> int:
        if n % 2 == 0:
            return n
        raise ValueError('number is odd')


def jsonrpc_decorator(fn: t.Callable[..., str]) -> t.Callable[..., str]:
    @functools.wraps(fn)
    def wrapped(*args, **kwargs) -> str:  # noqa: ANN002,ANN003
        rv = fn(*args, **kwargs)
        return f'{rv} from decorator, ;)'

    return wrapped


def create_app(test_config: t.Dict[str, t.Any] = None) -> Flask:  # noqa: C901  pylint: disable=W0612
    """Create and configure an instance of the Flask application."""
    flask_app = Flask('apptest', instance_relative_config=True)
    if test_config:
        flask_app.config.update(test_config)

    jsonrpc = JSONRPC(flask_app, '/api', enable_web_browsable_api=True)

    # pylint: disable=W0612
    @jsonrpc.method('jsonrpc.greeting')
    def greeting(name: str = 'Flask JSON-RPC') -> str:
        return f'Hello {name}'

    # pylint: disable=W0612
    @jsonrpc.method('jsonrpc.echo')
    def echo(string: str, _some: t.Any = None) -> str:  # noqa: ANN401
        return string

    # pylint: disable=W0612
    @jsonrpc.method('jsonrpc.notify')
    def notify(_string: str = None) -> None:
        pass

    # pylint: disable=W0612
    @jsonrpc.method('jsonrpc.not_allow_notify', notification=False)
    def not_allow_notify(_string: str = None) -> str:
        return 'Not allow notify'

    # pylint: disable=W0612
    @jsonrpc.method('jsonrpc.fails')
    def fails(n: int) -> int:
        if n % 2 == 0:
            return n
        raise ValueError('number is odd')

    # pylint: disable=W0612
    @jsonrpc.method('jsonrpc.strangeEcho')
    def strange_echo(
        string: str, omg: t.Dict[str, t.Any], wtf: t.List[str], nowai: int, yeswai: str = 'Default'
    ) -> t.List[t.Any]:
        return [string, omg, wtf, nowai, yeswai]

    # pylint: disable=W0612
    @jsonrpc.method('jsonrpc.sum')
    def sum_(a: t.Union[int, float], b: t.Union[int, float]) -> t.Union[int, float]:
        return a + b

    # pylint: disable=W0612
    @jsonrpc.method('jsonrpc.decorators')
    @jsonrpc_decorator
    def decorators(string: str) -> str:
        return f'Hello {string}'

    # pylint: disable=W0612
    @jsonrpc.method('jsonrpc.returnStatusCode')
    def return_status_code(s: str) -> t.Tuple[str, int]:
        return f'Status Code {s}', 201

    # pylint: disable=W0612
    @jsonrpc.method('jsonrpc.returnHeaders')
    def return_headers(s: str) -> t.Tuple[str, t.Dict[str, t.Any]]:
        return f'Headers {s}', {'X-JSONRPC': '1'}

    # pylint: disable=W0612
    @jsonrpc.method('jsonrpc.returnStatusCodeAndHeaders')
    def return_status_code_and_headers(s: str) -> t.Tuple[str, int, t.Dict[str, t.Any]]:
        return f'Status Code and Headers {s}', 400, {'X-JSONRPC': '1'}

    # pylint: disable=W0612
    @jsonrpc.method('jsonrpc.not_validate', validate=False)
    def not_validate(s='Oops!'):  # noqa: ANN001,ANN202
        return f'Not validate: {s}'

    @jsonrpc.method('jsonrpc.noReturn')
    def no_return(_string: t.Optional[str] = None) -> t.NoReturn:
        raise ValueError('no return')

    class_app = App()
    jsonrpc.register(class_app.index, name='classapp.index')
    jsonrpc.register(class_app.greeting)
    jsonrpc.register(class_app.hello)
    jsonrpc.register(class_app.echo)
    jsonrpc.register(class_app.notify)
    jsonrpc.register(class_app.not_allow_notify, notification=False)
    jsonrpc.register(class_app.fails)

    return flask_app


if __name__ == '__main__':
    app = create_app({'SERVER_NAME': os.getenv('FLASK_SERVER_NAME')})
    app.run(host='0.0.0.0')
