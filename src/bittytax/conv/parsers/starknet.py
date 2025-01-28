# -*- coding: utf-8 -*-

# Not working

from decimal import Decimal

from .etherscan import _get_note
from ..out_record import TransactionOutRecord
from ..dataparser import DataParser, ParserArgs, ParserType

WALLET = "StarkNet"
WORKSHEET_NAME = "StarkNet"

def parse_starknet(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["timestamp"]))

    if Decimal(row_dict["Value_IN(ETH)"]) > 0:
        if row_dict["Status"] == "":
            data_row.t_record = TransactionOutRecord(
                TrType.DEPOSIT,
                data_row.timestamp,
                buy_quantity=Decimal(row_dict["Value_IN(ETH)"]),
                buy_asset="AVAX",
                wallet=_get_wallet(row_dict["To"]),
                note=_get_note(row_dict),
            )
    elif Decimal(row_dict["Value_OUT(ETH)"]) > 0:
        data_row.t_record = TransactionOutRecord(
            TrType.WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=Decimal(row_dict["Value_OUT(ETH)"]),
            sell_asset="AVAX",
            fee_quantity=Decimal(row_dict["TxnFee(ETH)"]),
            fee_asset="AVAX",
            wallet=_get_wallet(row_dict["From"]),
            note=_get_note(row_dict),
        )
    else:
        data_row.t_record = TransactionOutRecord(
            TrType.SPEND,
            data_row.timestamp,
            sell_quantity=Decimal(row_dict["Value_OUT(ETH)"]),
            sell_asset="AVAX",
            fee_quantity=Decimal(row_dict["TxnFee(ETH)"]),
            fee_asset="AVAX",
            wallet=_get_wallet(row_dict["From"]),
            note=_get_note(row_dict),
        )





def get_wallet(address):
    return "%s-%s" % (WALLET, address.lower()[0:TransactionOutRecord.WALLET_ADDR_LEN])



# 0x0706cec1f577fc51492148aedec5ccf84dea1c02e5812806b3d38e7cf0cf9a9f,
# 0x01176a1bd84444c89232ec27754698e5d2e7e1a7f1539f12027f28b23ec9f3d8,
# 0.00008513304849258,
# 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7,
# ETH,
# Ether,
# fee_transfer,
# transfer,
# 0x2a60132a360829e20875ae5afec59095e5efb9a2bc6d40ebac42db54fe38a76,
# 546235,
# null,
# StarkWare: Sequencer,
# 1707915227


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
    all_handler=parse_starknet,
)