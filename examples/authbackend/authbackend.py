#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020, Cenobit Technologies, Inc. http://cenobit.es/
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
from functools import wraps

from flask import Flask

from flask_jsonrpc import JSONRPC, InvalidParamsError, InvalidCredentialsError  # noqa: E402

PROJECT_DIR, PROJECT_MODULE_NAME = os.path.split(os.path.dirname(os.path.realpath(__file__)))

FLASK_JSONRPC_PROJECT_DIR = os.path.join(PROJECT_DIR, os.pardir)
if os.path.exists(FLASK_JSONRPC_PROJECT_DIR) and FLASK_JSONRPC_PROJECT_DIR not in sys.path:
    sys.path.append(FLASK_JSONRPC_PROJECT_DIR)


app = Flask(__name__)


def authenticate(f, f_check_auth):
    @wraps(f)
    def _f(*args, **kwargs):
        is_auth = False
        try:
            creds = args[:2]
            is_auth = f_check_auth(creds[0], creds[1])
            if is_auth:
                args = args[2:]
        except IndexError:
            if 'username' in kwargs and 'password' in kwargs:
                is_auth = f_check_auth(kwargs['username'], kwargs['password'])
                if is_auth:
                    kwargs.pop('username')
                    kwargs.pop('password')
            else:
                raise InvalidParamsError(
                    'Authenticated methods require at least ' '[username, password] or {username: password:} arguments'
                )
        if not is_auth:
            raise InvalidCredentialsError()
        return f(*args, **kwargs)

    return _f


jsonrpc = JSONRPC(app, '/api', auth_backend=authenticate)


def check_auth(_username, _password):
    return True


@jsonrpc.method('App.index', authenticated=check_auth)
def index():
    return u'Welcome to Flask JSON-RPC'


@jsonrpc.method('App.echo(name=str)', authenticated=check_auth)
def echo(name=''):
    return u'Hello {0}'.format(name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
