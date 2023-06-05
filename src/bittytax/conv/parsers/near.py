# -*- coding: utf-8 -*-
# (c)

# Support for Near via nearblocks.io

import time

from ..out_record import TransactionOutRecord
from ..dataparser import DataParser

WALLET = "Near"
WORKSHEET_NAME = "Near"

def parse_near(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict['Time'])

    if row_dict['Status'] != 'Success':
        # Failed txns should not have a Value_OUT
        return

    if row_dict['Method'] in ['TRANSFER', 'deposit_and_stake', 'withdraw_all']:
        if get_wallet_address(_kwargs['filename']) == row_dict['To']:
            data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_DEPOSIT,
                                                     data_row.timestamp,
                                                     buy_quantity=abs(float(row_dict['Deposit Value'].replace(',', ''))),
                                                     buy_asset='NEAR',
                                                     fee_quantity=row_dict['Txn Fee'],
                                                     fee_asset='NEAR',
                                                     wallet=get_wallet(row_dict['To']))

        else:
            data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_WITHDRAWAL,
                                                     data_row.timestamp,
                                                     sell_quantity=abs(float(row_dict['Deposit Value'].replace(',', ''))),
                                                     sell_asset='NEAR',
                                                     fee_quantity=row_dict['Txn Fee'],
                                                     fee_asset='NEAR',
                                                     wallet=get_wallet(row_dict['From']))


def get_wallet(address):
    return "%s-%s" % (WALLET, address.lower()[0:TransactionOutRecord.WALLET_ADDR_LEN])

def get_wallet_address(filename):
    return filename.split('-')[0]


near_txns = DataParser(
    DataParser.TYPE_EXPLORER,
    "Near",
    ['Status','Txn Hash','Method','Deposit Value','Txn Fee','From','To','Block','Time'],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_near)
