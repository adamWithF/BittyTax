# -*- coding: utf-8 -*-
# (c)

# Support for Arweave via viewblock.io

from ..out_record import TransactionOutRecord
from ..dataparser import DataParser, ParserType
from ...bt_types import TrType

WALLET = "Arweave"
WORKSHEET_NAME = "Arweave"

def parse_arweave(data_row, _parser, **kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict['time'])

    if not row_dict['hash']:
        # Failed txns should not have a Value_OUT
        return

    if row_dict['from'] in kwargs['filename']:
        data_row.t_record = TransactionOutRecord(TrType.DEPOSIT,
                                                 data_row.timestamp,
                                                 buy_quantity=get_quantity(row_dict),
                                                 buy_asset="AR",
                                                 fee_quantity=row_dict['fee'].split(' ')[0],
                                                 fee_asset="AR",
                                                 wallet=get_wallet(row_dict['to']))

    else:
        data_row.t_record = TransactionOutRecord(TrType.WITHDRAWAL,
                                                 data_row.timestamp,
                                                 sell_quantity=get_quantity(row_dict),
                                                 sell_asset="AR",
                                                 fee_quantity=row_dict['fee'].split(' ')[0],
                                                 fee_asset="AR",
                                                 wallet=get_wallet(row_dict['from']))

def get_quantity(row_dict):
    return abs(float(row_dict['value'].split(' ')[0].replace(',', '')))

def get_wallet(address):
    return "%s-%s" % (WALLET, address.lower()[0:TransactionOutRecord.WALLET_ADDR_LEN])

def get_wallet_address(filename):
    return filename.split('-')[0]

arweave_txns = DataParser(
    ParserType.EXPLORER,
    "Arweave",
    ["hash","timestamp","time","height","size","contentType","value","from","to","fee","apps"],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_arweave)