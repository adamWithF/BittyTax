# -*- coding: utf-8 -*-
# (c)

# Support for mintscan.io

from ..out_record import TransactionOutRecord
from ..dataparser import DataParser, ParserType
from ...bt_types import TrType

WALLET = "Mintscan"
WORKSHEET_NAME = "Mintscan"

def parse_mintscan(data_row, _parser, **kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict['timestamp'])

    if not row_dict['txhash']:
        return

    if row_dict['to'] in kwargs['filename']:
        data_row.t_record = TransactionOutRecord(TrType.DEPOSIT,
                                                 data_row.timestamp,
                                                 buy_quantity=row_dict['amount'],
                                                 buy_asset=row_dict['token'],
                                                 # fee_quantity=row_dict['fee'].split(' ')[0],
                                                 # fee_asset="AR",
                                                 wallet=get_wallet(row_dict['to']))

    elif row_dict['from'] in kwargs['filename']:
        data_row.t_record = TransactionOutRecord(TrType.WITHDRAWAL,
                                                 data_row.timestamp,
                                                 sell_quantity=row_dict['amount'],
                                                 sell_asset=row_dict['token'],
                                                 # fee_quantity=row_dict['fee'].split(' ')[0],
                                                 # fee_asset="AR",
                                                 wallet=get_wallet(row_dict['from']))

# def get_quantity(row_dict):
#     return abs(float(row_dict['amount'].split(' ')[0].replace(',', '')))

def get_wallet(address):
    return "%s-%s" % (WALLET, address.lower()[0:TransactionOutRecord.WALLET_ADDR_LEN])

def get_wallet_address(filename):
    return filename.split('-')[0]

DataParser(
    ParserType.EXPLORER,
    "Mintscan",
    [
"index","type","from","to","txhash","amount","token","denom","timestamp","unitPrice","totalPrice"
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_mintscan)