from werkzeug.exceptions import HTTPException


class InvalidPage(HTTPException):
    code = 404
    description = 'Invalid page number.'
