# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2021

# Support for Terra Luna, Lunc

import time

from ..out_record import TransactionOutRecord
from ..dataparser import DataParser, ParserArgs, ParserType

WALLET = "Terra"
WORKSHEET_NAME = "Terra StakeTax"

def parse_terra(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict['Timestamp'])

    if get_wallet_address(_kwargs['filename']) == row_dict['Recipient']:
        data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_DEPOSIT,
                                                 data_row.timestamp,
                                                 buy_quantity=abs(float(row_dict['Amount'].replace(',', ''))),
                                                 buy_asset=row_dict['Currency'],
                                                 fee_quantity=row_dict['Fee Amount'],
                                                 fee_asset=row_dict['Fee Currency'],
                                                 wallet=get_wallet(row_dict['Recipient']))

    else:
        data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_WITHDRAWAL,
                                                 data_row.timestamp,
                                                 sell_quantity=abs(float(row_dict['Amount'].replace(',', ''))),
                                                 sell_asset=row_dict['Currency'],
                                                 fee_quantity=row_dict['Fee Amount'],
                                                 fee_asset=row_dict['Fee Currency'],
                                                 wallet=get_wallet(row_dict['Sender']))

def get_wallet(address):
    return "%s-%s" % (WALLET, address.lower()[0:TransactionOutRecord.WALLET_ADDR_LEN])

def get_wallet_address(filename):
    return filename.split('-')[0]



terra_txns = DataParser(
    ParserType.EXPLORER,
    "Terra",
    ['Timestamp','Transaction Hash','Tracked Address','Transaction Type','Sender','Recipient','Amount','Currency','Fee Amount','Fee Currency'],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_terra)