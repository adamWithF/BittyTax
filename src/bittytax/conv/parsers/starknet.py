# -*- coding: utf-8 -*-

# Support for StarkNet via voyager.online

from decimal import Decimal

from ..out_record import TransactionOutRecord
from ..dataparser import DataParser, ParserArgs, ParserType
from ...bt_types import TrType
from typing_extensions import Unpack
from typing import TYPE_CHECKING, Dict, List
from ...config import config
from ..exceptions import DataRowError
import sys
from decimal import Decimal
from typing import TYPE_CHECKING, Dict, List
from colorama import Fore
from typing_extensions import Unpack
from ...bt_types import TrType
from ...config import config
from ..dataparser import DataParser, ParserArgs, ParserType
from ..out_record import TransactionOutRecord


if TYPE_CHECKING:
    from ..datarow import DataRow

WALLET = "StarkNet"
WORKSHEET_NAME = "StarkNet"

def parse_starknet(data_rows: List["DataRow"], parser: DataParser, **kwargs: Unpack[ParserArgs]):
    ref_ids: Dict[str, List["DataRow"]] = {}

    for dr in data_rows:
        dr.timestamp = DataParser.parse_timestamp(int(dr.row_dict["timestamp"]))

        if dr.row_dict["tx_hash"] in ref_ids:
            ref_ids[dr.row_dict["tx_hash"]].append(dr)
        else:
            ref_ids[dr.row_dict["tx_hash"]] = [dr]

    for row_index, data_row in enumerate(data_rows):
        if config.debug:
            if parser.in_header_row_num is None:
                raise RuntimeError("Missing in_header_row_num")

            sys.stderr.write(
                f"{Fore.YELLOW}conv: "
                f"row[{parser.in_header_row_num + data_row.line_num}] {data_row}\n"
            )

        if data_row.parsed:
            continue

        try:
            _parse_kraken_ledgers_row(ref_ids, data_rows, parser, data_row, row_index, **kwargs)
        except DataRowError as e:
            data_row.failure = e
        except (ValueError, ArithmeticError) as e:
            if config.debug:
                raise
            data_row.failure = e


def _parse_kraken_ledgers_row(
    ref_ids: Dict[str, List["DataRow"]],
    data_rows: List["DataRow"],
    parser: DataParser,
    data_row: "DataRow",
    row_index: int,
    **kwargs: Unpack[ParserArgs]
) -> None:
    row_dict = data_row.row_dict

    if data_row.t_record is not None:
        return

    if row_dict["call"] == "claim":
        data_row.t_record = TransactionOutRecord(
            TrType.STAKING,
            data_row.timestamp,
            buy_quantity=Decimal(row_dict["transfer_amount"].replace(",", "")),
            buy_asset=row_dict["token_symbol"],
            wallet=_get_wallet(row_dict["transfer_to"]),
            note=_get_note(row_dict),
        )
    elif row_dict["call"] in ["swap", "swapExactTokensForTokens", "swapExactTokensForTokensSupportingFeeOnTransferTokens", "multi_route_swap", "clear_minimum"]:
        _make_trade(ref_ids[data_row.row_dict["tx_hash"]], **kwargs)
        pass
    else:
        if row_dict["transfer_from"].lower() in kwargs["filename"].lower():
            data_row.t_record = TransactionOutRecord(
                TrType.SPEND,
                data_row.timestamp,
                sell_quantity=Decimal(0),
                sell_asset=row_dict["token_symbol"],
                fee_quantity=Decimal(row_dict["transfer_amount"].replace(",", "")),
                fee_asset=row_dict["token_symbol"],
                wallet=_get_wallet(row_dict["transfer_from"]),
                note=_get_note(row_dict),
            )

def _make_trade(ref_ids: List["DataRow"], **kwargs: Unpack[ParserArgs]) -> None:
    filename = kwargs["filename"].lower()
    buy_quantity = sell_quantity = None
    buy_asset = sell_asset = None

    for data_row in ref_ids:
        row_dict = data_row.row_dict

        if data_row.t_record:
            continue

        if row_dict["call"] == "swap" or row_dict["call"] ==  "swapExactTokensForTokens" or row_dict["call"] == "swapExactTokensForTokensSupportingFeeOnTransferTokens" or row_dict["call"] == "multi_route_swap" or row_dict["call"] == "clear_minimum":

            if row_dict["transfer_from"].lower() in filename:
                sell_asset = row_dict["token_symbol"]
                sell_quantity = Decimal(row_dict["transfer_amount"].replace(",", ""))
            else:
                buy_asset = row_dict["token_symbol"]
                buy_quantity = Decimal(row_dict["transfer_amount"].replace(",", ""))

            if buy_quantity and sell_quantity and buy_asset and sell_asset:
                data_row.t_record = TransactionOutRecord(
                    TrType.TRADE,
                    data_row.timestamp,
                    buy_quantity=buy_quantity,
                    buy_asset=buy_asset,
                    sell_quantity=sell_quantity,
                    sell_asset=sell_asset,
                    wallet=_get_wallet(row_dict["transfer_from"]),
                    note=_get_note(row_dict),
                )
                buy_quantity = sell_quantity = None
                buy_asset = sell_asset = None
        else:
            if row_dict["transfer_from"].lower() in filename:
                data_row.t_record = TransactionOutRecord(
                    TrType.SPEND,
                    data_row.timestamp,
                    sell_quantity=Decimal(0),
                    sell_asset=row_dict["token_symbol"],
                    fee_quantity=Decimal(row_dict["transfer_amount"].replace(",", "")),
                    fee_asset=row_dict["token_symbol"],
                    wallet=_get_wallet(row_dict["transfer_from"]),
                    note=_get_note(row_dict),
                )

def _get_wallet(address):
    return "%s-%s" % (WALLET, address.lower()[0:TransactionOutRecord.WALLET_ADDR_LEN])

def _get_note(row_dict):
    return str(row_dict)

STARKNET_TXNS = DataParser(
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