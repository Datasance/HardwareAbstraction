#********************************************************************************
#  Copyright (c) 2023 Datasance Teknoloji A.S.
#
#  This program and the accompanying materials are made available under the
#  terms of the Eclipse Public License v. 2.0 which is available at
#  http://www.eclipse.org/legal/epl-2.0
#
#  SPDX-License-Identifier: EPL-2.0
#********************************************************************************

class HALBaseException(Exception):
    def __init__(self, *args, **kwargs):
        super(HALBaseException, self).__init__(*args, **kwargs)


class HALException(HALBaseException):
    def __init__(self, code=0, message='Unexpected error.'):
        self.code = code
        self.message = message

    def __str__(self):
        return 'Error code: {}, reason: {}'.format(self.code, self.message)

    def to_json(self):
        return {'code': self.code, 'reason': self.message}
