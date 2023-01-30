# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2021

# Support for Polkadot, Kusama and others via SubScan

import time
from decimal import Decimal

from .etherscan import get_note
from ..out_record import TransactionOutRecord
from ..dataparser import DataParser

WALLET = "SubScan"
WORKSHEET_NAME = "SubScan"

def parse_subscan(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    # data_row.timestamp = row_dict['Date']
    # data_row.timestamp = time.mktime(time.strptime())
    data_row.timestamp = DataParser.parse_timestamp(row_dict['Date'])
    # print("parse_subscan", _kwargs['filename'].split('-'))

    if row_dict['Result'] != 'true':
        # Failed txns should not have a Value_OUT
        return

    # depending on To From values, compare to local address below
    if get_wallet_address(_kwargs['filename']) == row_dict['To']:
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

def get_wallet_address(filename):
    return filename.split('-')[0]


subscan_txns = DataParser(
    DataParser.TYPE_EXPLORER,
    "SubScan",
    ['Extrinsic ID','Date','Block','Hash','Symbol','From','To','Value','Result'],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_subscan)
