import json

_author_ = "int_soumen"
_date_ = "28-09-2018"


class IOTPTransactionResponse:
    CODE_MATRIX = {
        '200': 'Success or OK',
        '400': 'Invalid Request',
        '405': 'Operand Not Found',
        '500': 'System Error',
        '503': 'Operand Unresponsive'
    }

    def __init__(self, code):
        self.__status_code = code
        self.__status_text = IOTPTransactionResponse.CODE_MATRIX[str(code)]
        self.__message = ""
        pass

    def set_status(self, code):
        self.__status_code = code
        self.__status_text = IOTPTransactionResponse.CODE_MATRIX[str(code)]

    def set_message(self, message):
        self.__message = message

    def get_json(self):
        return json.dumps({
            'status_code': self.__status_code,
            'status_text': self.__status_text,
            'message': self.__message
        })
