# -*- coding: utf-8 -*-
# (c)

# Support for Bittensor via taostats.io

from ..out_record import TransactionOutRecord
from ..dataparser import DataParser, ParserType
from ...bt_types import TrType
from typing import Dict

WALLET = "Bittensor"
WORKSHEET_NAME = "Bittensor"

def parse_bittensor(data_row, _parser, **kwargs):
    row_dict = data_row.row_dict
    row_dict["value"] = str(abs(float(row_dict["()=>\"Amount\""])) * 0.000000001)
    data_row.timestamp = DataParser.parse_timestamp(row_dict["()=>\"Time\""])

    if not row_dict['From']:
        return

    if row_dict['From'] in kwargs['filename']:
        data_row.t_record = TransactionOutRecord(TrType.DEPOSIT,
                                                 data_row.timestamp,
                                                 buy_quantity=get_quantity(row_dict),
                                                 buy_asset="TAO",
                                                 # fee_quantity=row_dict['fee'].split(' ')[0],
                                                 # fee_asset="TAO",
                                                 wallet=get_wallet(row_dict['TO']),
                                                 note=_get_note(row_dict)
                                                 )

    else:
        data_row.t_record = TransactionOutRecord(TrType.WITHDRAWAL,
                                                 data_row.timestamp,
                                                 sell_quantity=get_quantity(row_dict),
                                                 sell_asset="TAO",
                                                 # fee_quantity=row_dict['fee'].split(' ')[0],
                                                 # fee_asset="TAO",
                                                 wallet=get_wallet(row_dict['From']),
                                                 note=_get_note(row_dict)
                                                 )

def _get_note(row_dict: Dict[str, str]) -> str:
    return str(row_dict)

def get_quantity(row_dict):
    return abs(float(row_dict['value'].split(' ')[0].replace(',', '')))

def get_wallet(address):
    return "%s-%s" % (WALLET, address.lower()[0:TransactionOutRecord.WALLET_ADDR_LEN])

def get_wallet_address(filename):
    return filename.split('-')[0]

arweave_txns = DataParser(
    ParserType.EXPLORER,
    "Bittensor",
    ["","Extrinsic","From","TO", "()=>\"Amount\"", "()=>\"Time\""],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_bittensor)