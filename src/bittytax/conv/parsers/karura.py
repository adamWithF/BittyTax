# -*- coding: utf-8 -*-
# (c)

# Support for Karura via SubScan

import time
import ntpath

from ..exceptions import DataFilenameError
from ..out_record import TransactionOutRecord
from ..dataparser import DataParser

WALLET = "Karura"
WORKSHEET_NAME = "Karura SubScan"


def get_wallet(address):
    return "%s-%s" % (WALLET, address.lower()[0:TransactionOutRecord.WALLET_ADDR_LEN])

def get_wallet_address(filename):
    return filename.split('-')[0]

def parse_subscan_transfers(data_row, _parser, **kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict["Date"])

    if row_dict["Result"] != "true":
        return

    if row_dict["To"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_DEPOSIT,
            data_row.timestamp,
            buy_quantity=row_dict["Value"],
            buy_asset=row_dict["Symbol"],
            wallet=get_wallet(row_dict["To"]),
        )
    else:
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=row_dict["Value"],
            sell_asset=row_dict["Symbol"],
            wallet=get_wallet(row_dict["From"]),
        )

# def parse_subscan_xcm(data_row, _parser, **kwargs):
#     row_dict = data_row.row_dict
#     data_row.timestamp = DataParser.parse_timestamp(row_dict["Block Timestamp"])

#     # TODO check if result fails
#     # if row_dict["Result"]:

#     if row_dict["To"].lower() in kwargs["filename"].lower():
#         data_row.t_record = TransactionOutRecord(
#             TransactionOutRecord.TYPE_DEPOSIT,
#             data_row.timestamp,
#             buy_quantity=row_dict["Value"].split()[0],
#             buy_asset=row_dict["Value"].split()[1],
#             wallet=get_wallet(row_dict["To"]),
#         )
#     elif row_dict["From"].lower() in kwargs["filename"].lower():
#         data_row.t_record = TransactionOutRecord(
#             TransactionOutRecord.TYPE_WITHDRAWAL,
#             data_row.timestamp,
#             sell_quantity=row_dict["Value"].split()[0],
#             sell_asset=row_dict["Value"].split()[1],
#             wallet=get_wallet(row_dict["From"]),
#         )
#     else:
#         filename = ntpath.basename(kwargs["filename"]).split('-')[1].lower()
#         raise DataFilenameError(filename, "Kusama address")


KUSAMA_TRANSFERS = DataParser(
    DataParser.TYPE_EXPLORER,
    f"{WORKSHEET_NAME} ({WALLET} Transfer History)",
    ["Extrinsic ID","Date","Block","Hash","Symbol","From","To","Value","Result"],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_subscan_transfers,
    filename_prefix="karura",
)

# KUSAMA_XCM = DataParser(
#     DataParser.TYPE_EXPLORER,
#     f"{WORKSHEET_NAME} ({WALLET} XCM Transfers)",
#     ["Transfer Hash","From","To","Value","Block Timestamp","Transport Protocol","Result"],
#     worksheet_name=WORKSHEET_NAME,
#     row_handler=parse_subscan_xcm,
#     filename_prefix="kusama",
# )
