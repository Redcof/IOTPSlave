from IOTPSlaveMessage import IOTPSlaveMessage

_author_ = "int_soumen"
_date_ = "12-08-2018"

_LOC_TRANS_TYPE_ID = 0
_LOC_TRANS_ID = 1
_LOC_SLAVE_ID = 5
_LOC_MSG_BODY = 9

# _LEN_TRANS_TYPE_ID = 1
# _LEN_TRANS_ID = 4
# _LEN_SLAVE_ID = 4

_END_TRANS_TYPE_ID = _LOC_TRANS_ID
_END_TRANS_ID = _LOC_SLAVE_ID
_END_SLAVE_ID = _LOC_MSG_BODY


class IOTPTransactionData(IOTPSlaveMessage):

    def __init__(self, trans_data, my_slave_id):
        IOTPSlaveMessage.__init__(self)
        self.__raw_server_data = trans_data
        self.__transaction_type_id = 0x0
        self.__transaction_id = 0x0000
        self.__slave_id = 0x0000
        self.__my_slave_id = int(my_slave_id, 10)
        self.__parse_data()

    def __parse_data(self):
        # parse transaction type
        self.__transaction_type_id = int(self.__raw_server_data[
                                         _LOC_TRANS_TYPE_ID:
                                         _END_TRANS_TYPE_ID
                                         ],
                                         16)
        if self.__transaction_type_id not in self._trans_types:
            raise Exception(IOTPSlaveMessage.ResponseType.StatusCode.INVALID_REQUEST, "Transaction Type ID is "
                                                                                      "invalid")

        # parse transaction id
        self.__transaction_id = int(self.__raw_server_data[
                                    _LOC_TRANS_ID:
                                    _END_TRANS_ID
                                    ],
                                    16)
        if self.__transaction_id is 0:
            raise Exception(IOTPSlaveMessage.ResponseType.StatusCode.INVALID_REQUEST, "Transaction ID is "
                                                                                      "0")

        # parse slave id
        self.__slave_id = int(self.__raw_server_data[
                              _LOC_SLAVE_ID:
                              _END_SLAVE_ID
                              ],
                              16)
        if self.__my_slave_id is not self.__slave_id:
            raise Exception(IOTPSlaveMessage.ResponseType.StatusCode.INVALID_REQUEST, "Slave ID is "
                                                                                      "wrong")

    def get_raw_trans_data(self):
        return self.__raw_server_data

    def get_trans_type_id(self):
        return self.__transaction_type_id

    def get_trans_id(self):
        return self.__transaction_id

    def get_slave_id(self):
        return self.__slave_id

    def get_hardware_slave_id(self):
        return self.__my_slave_id
