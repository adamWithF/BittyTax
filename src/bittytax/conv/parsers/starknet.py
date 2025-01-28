# -*- coding: utf-8 -*-

# Support for StarkNet via voyager.online
# Not completed, need merger

from decimal import Decimal

from ..out_record import TransactionOutRecord
from ..dataparser import DataParser, ParserArgs, ParserType
from ...bt_types import TrType

WALLET = "StarkNet"
WORKSHEET_NAME = "StarkNet"

def parse_starknet(data_row, _parser, **kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["timestamp"]))

    if row_dict["transfer_to"].lower() in kwargs["filename"].lower():
        if row_dict["call"] == "transfer":
            data_row.t_record = TransactionOutRecord(
                TrType.DEPOSIT,
                data_row.timestamp,
                buy_quantity=Decimal(row_dict["transfer_amount"].replace(",", "")),
                buy_asset=row_dict["token_symbol"],
                wallet=_get_wallet(row_dict["transfer_to"]),
                note=_get_note(row_dict),
            )
        else:
            data_row.t_record = TransactionOutRecord(
                TrType.SPEND,
                data_row.timestamp,
                sell_quantity=Decimal(row_dict["transfer_amount"].replace(",", "")),
                sell_asset=row_dict["token_symbol"],
                # fee_quantity=Decimal(row_dict["TxnFee(ETH)"]),
                # fee_asset="ETH",
                wallet=_get_wallet(row_dict["transfer_to"]),
                note=_get_note(row_dict),
            )

    elif row_dict["transfer_from"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TrType.WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=Decimal(row_dict["transfer_amount"].replace(",", "")),
            sell_asset=row_dict["token_symbol"],
            # fee_quantity=Decimal(row_dict["TxnFee(ETH)"]),
            # fee_asset="ETH",
            wallet=_get_wallet(row_dict["transfer_from"]),
            note=_get_note(row_dict),
        )

def _get_wallet(address):
    return "%s-%s" % (WALLET, address.lower()[0:TransactionOutRecord.WALLET_ADDR_LEN])

def _get_note(row_dict):
    return str(row_dict)

DataParser(
    ParserType.EXCHANGE,
    "StarkNet",
    [
        "transfer_from",
        "transfer_to",
        "transfer_amount",
        "token_address",
        "token_symbol",
        "token_name",
        "transfer_type",
        "call",
        "tx_hash",
        "block_number",
        "from_alias",
        "to_alias",
        "timestamp"
    ],
    worksheet_name="StarkNet",
    row_handler=parse_starknet,
)