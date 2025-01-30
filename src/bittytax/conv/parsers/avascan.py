# -*- coding: utf-8 -*-
# (c)

# Support for Avalanche via avascan.info

from ..out_record import TransactionOutRecord
from ..dataparser import DataParser, ParserType
from ...bt_types import TrType
from typing import Dict
from decimal import Decimal

WALLET = "Avalanche"
WORKSHEET_NAME = "Avalanche"

def parse_avascan_txs(data_row, _parser, **kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict['Timestamp'])

    if not row_dict['Tx hash']:
        # Failed txns should not have a Value_OUT
        return

    if row_dict['From'].lower() in kwargs['filename'].lower():
        data_row.t_record = TransactionOutRecord(TrType.SPEND,
                                                 data_row.timestamp,
                                                 buy_quantity=Decimal(0),
                                                 buy_asset="AVAX",
                                                 fee_quantity=row_dict['Fees'],
                                                 fee_asset="AVAX",
                                                 wallet=get_wallet(row_dict['From']),
                                                 note=_get_note(row_dict)
                                                 )

    else:
        data_row.t_record = TransactionOutRecord(TrType.WITHDRAWAL,
                                                 data_row.timestamp,
                                                 sell_quantity=Decimal(0),
                                                 sell_asset="AVAX",
                                                 fee_quantity=row_dict['Fees'],
                                                 fee_asset="AVAX",
                                                 wallet=get_wallet(row_dict['To']),
                                                 note=_get_note(row_dict)
                                                 )

def _get_note(row_dict: Dict[str, str]) -> str:
    return str(row_dict)

def get_wallet(address):
    return "%s-%s" % (WALLET, address.lower()[0:TransactionOutRecord.WALLET_ADDR_LEN])

def get_wallet_address(filename):
    return filename.split('-')[0]



avascan_txns = DataParser(
    ParserType.EXPLORER,
    "Avascan",
    ["Tx hash", "Block Number", "From", "To", "Timestamp", "Chain ID", "Value", "Fees"],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_avascan_txs)