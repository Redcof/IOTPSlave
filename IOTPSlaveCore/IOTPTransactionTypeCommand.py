from IOTPSlaveMessage import IOTPSlaveMessage
from IOTPTransactionData import IOTPTransactionData, _LOC_MSG_BODY

_author_ = "int_soumen"
_date_ = "12-08-2018"

_LOC_NO_OPERATION = _LOC_MSG_BODY
_LOC_OPERAND_TYPE = 10
_LOC_OPERAND_ID = 11
_LOC_OPERAND_INSTRUCTION = 12
_LOC_NEXT_OPERAND_INFO = 16

_END_NO_OPERATION = _LOC_OPERAND_TYPE

_LEN_OPERAND_TYPE = 1
_LEN_OPERAND_ID = 1
_LEN_OPERAND_INSTRUCTION = 4

_MAX_NO_OPERATION = 8


class IOTPTransactionTypeCommand:

    def __init__(self, iotp_trans_data_obj):
        if not isinstance(iotp_trans_data_obj, IOTPTransactionData):
            raise Exception("First argument should be an instance of IOTPTransactionData")
        self.__raw_server_data = iotp_trans_data_obj.get_raw_trans_data()
        self.__no_opr = 0
        self.__operation_info = []
        self.__opr_ctr = -1
        self.__parse_data()

    def __parse_data(self):
        # parse number of operation to perform
        self.__no_opr = int(self.__raw_server_data[
                            _LOC_NO_OPERATION:
                            _END_NO_OPERATION
                            ],
                            16)
        if self.__no_opr > _MAX_NO_OPERATION:
            raise Exception(IOTPSlaveMessage.ResponseType.StatusCode.INVALID_REQUEST, "Maximum 8 operations are "
                                                                                      "allowed.")
        operation_info_offset = _LOC_OPERAND_TYPE

        for k in range(0, self.__no_opr, 1):
            # parse operand type
            opr_type = int(self.__raw_server_data[
                           operation_info_offset:
                           operation_info_offset + _LEN_OPERAND_TYPE
                           ],
                           16)
            operation_info_offset += _LEN_OPERAND_TYPE

            # parse operand id
            opr_id = int(self.__raw_server_data[
                         operation_info_offset:
                         operation_info_offset + _LEN_OPERAND_ID
                         ],
                         16)
            operation_info_offset += _LEN_OPERAND_ID

            # parse operand instruction
            instruction = int(self.__raw_server_data[
                              operation_info_offset:
                              operation_info_offset + _LEN_OPERAND_INSTRUCTION
                              ],
                              16)
            operation_info_offset += _LEN_OPERAND_INSTRUCTION

            self.__operation_info.append((opr_type, opr_id, instruction))

    " Get the next operand information "
    def next_operand_info(self):
        self.__opr_ctr += 1
        if self.__opr_ctr < self.__no_opr:
            return self.__operation_info[self.__opr_ctr]
        return None

    def has_next(self):
        return self.__opr_ctr < (self.__no_opr - 1)

    " Reset everything counter "
    def reset(self):
        self.__opr_ctr = -1
