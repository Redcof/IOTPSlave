from IOTPTransactionData import IOTPTransactionData, _LOC_MSG_BODY

_author_ = "int_soumen"
_date_ = "28-09-2018"

_LOC_MODE_OF_INTERROGATION = _LOC_MSG_BODY

_END_MODE_OF_INTERROGATION = 10

_LEN_MODE_OF_INTERROGATION = 1


class IOTPTransactionTypeInterrogation:

    def __init__(self, iotp_trans_data_obj):
        if not isinstance(iotp_trans_data_obj, IOTPTransactionData):
            raise Exception("First argument should be an instance of IOTPTransactionData")
        self.__raw_server_data = iotp_trans_data_obj.get_raw_trans_data()
        self.__mode_of_interrogation = 0xD
        self.__parse_data()

    def __parse_data(self):
        # parse number of operation to perform
        self.__mode_of_interrogation = int(self.__raw_server_data[
                                           _LOC_MODE_OF_INTERROGATION:
                                           _END_MODE_OF_INTERROGATION
                                           ],
                                           16)

    " Get the interrogation type "

    def is_connection_check(self):
        return self.__mode_of_interrogation is 0xC

    def is_status_check(self):
        return self.__mode_of_interrogation is 0xD
