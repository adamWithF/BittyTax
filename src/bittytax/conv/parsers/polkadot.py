# -*- coding: utf-8 -*-
# (c)

# Support for Polkadot

import time

from ..out_record import TransactionOutRecord
from ..dataparser import DataParser

WALLET = "Polkadot"
WORKSHEET_NAME = f"{WALLET} SubScan"

def parse_subscan(data_row, _parser, **kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict['Date'])

    if row_dict['Result'] != 'true':
        # Failed txns should not have a Value_OUT
        return

    # depending on To From values, compare to local address below
    if row_dict['To'].lower() in kwargs['filename'].lower():
        data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_DEPOSIT,
                                                 data_row.timestamp,
                                                 buy_quantity=row_dict['Value'],
                                                 buy_asset=row_dict['Symbol'],
                                                 wallet=get_wallet(row_dict['To']))

    else:
        data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_WITHDRAWAL,
                                                 data_row.timestamp,
                                                 sell_quantity=row_dict['Value'],
                                                 sell_asset=row_dict['Symbol'],
                                                 wallet=get_wallet(row_dict['From']))

def get_wallet(address):
    return "%s-%s" % (WALLET, address.lower()[0:TransactionOutRecord.WALLET_ADDR_LEN])

POLKADOT_TXNS = DataParser(
    DataParser.TYPE_EXPLORER,
    f"{WORKSHEET_NAME} ({WALLET} Transfer History)",
    ['Extrinsic ID','Date','Block','Hash','Symbol','From','To','Value','Result'],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_subscan,
    filename_prefix="polkadot",
)
