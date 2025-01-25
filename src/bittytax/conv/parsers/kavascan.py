# -*- coding: utf-8 -*-

# KAVA via kavascan.com

from decimal import Decimal
from typing import TYPE_CHECKING

from typing_extensions import Unpack

from ...bt_types import TrType
from ..dataparser import DataParser, ParserArgs, ParserType
from ..datarow import TxRawPos
from ..exceptions import DataFilenameError
from ..out_record import TransactionOutRecord
from .etherscan import _get_note

if TYPE_CHECKING:
    from ..datarow import DataRow

WALLET = "Kava"
WORKSHEET_NAME = "KavaScan"

def parse_kavascan(data_row: "DataRow", parser: DataParser, **_kwargs: Unpack[ParserArgs]) -> None:
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict["DateTime (UTC)"])
    data_row.tx_raw = TxRawPos(
        parser.in_header.index("Transaction Hash"),
        parser.in_header.index("From"),
        parser.in_header.index("To"),
    )

    if row_dict["Status"] != "":
        # Failed transactions should not have a Value_OUT
        row_dict["Value (KAVA)"] = "0"

    if Decimal(row_dict["Value (KAVA)"]) > 0:
        if row_dict["Status"] == "":
            data_row.t_record = TransactionOutRecord(
                TrType.DEPOSIT,
                data_row.timestamp,
                buy_quantity=Decimal(row_dict["Value (KAVA)"]),
                buy_asset="AVAX",
                wallet=_get_wallet(row_dict["To"]),
                note=_get_note(row_dict),
            )
    elif Decimal(row_dict["Value (KAVA)"]) > 0:
        data_row.t_record = TransactionOutRecord(
            TrType.WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=Decimal(row_dict["Value (KAVA)"]),
            sell_asset="AVAX",
            fee_quantity=Decimal(row_dict["TxnFee (KAVA)"]),
            fee_asset="AVAX",
            wallet=_get_wallet(row_dict["From"]),
            note=_get_note(row_dict),
        )
    else:
        data_row.t_record = TransactionOutRecord(
            TrType.SPEND,
            data_row.timestamp,
            sell_quantity=Decimal(row_dict["Value (KAVA)"]),
            sell_asset="AVAX",
            fee_quantity=Decimal(row_dict["TxnFee (KAVA)"]),
            fee_asset="AVAX",
            wallet=_get_wallet(row_dict["From"]),
            note=_get_note(row_dict),
        )


def _get_wallet(address: str) -> str:
    return f"{WALLET}-{address.lower()[0 : TransactionOutRecord.WALLET_ADDR_LEN]}"


def parse_kavascan_tokens(
    data_row: "DataRow", parser: DataParser, **kwargs: Unpack[ParserArgs]
) -> None:
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict["DateTime (UTC)"])
    # row_dict["Transaction Hash"] = row_dict["tx_hash"]
    data_row.tx_raw = TxRawPos(
        parser.in_header.index("Transaction Hash"),
        parser.in_header.index("From"),
        parser.in_header.index("To"),
    )

    if row_dict["TokenSymbol"].endswith("-LP"):
        asset = row_dict["TokenSymbol"] + "-" + row_dict["ContractAddress"][0:10]
    else:
        asset = row_dict["TokenSymbol"]

    quantity = Decimal(row_dict["TokenValue"].replace(",", ""))

    if row_dict["To"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TrType.DEPOSIT,
            data_row.timestamp,
            buy_quantity=quantity,
            buy_asset=asset,
            wallet=_get_wallet(row_dict["To"]),
        )
    elif row_dict["From"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TrType.WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=quantity,
            sell_asset=asset,
            wallet=_get_wallet(row_dict["From"]),
        )
    else:
        raise DataFilenameError(kwargs["filename"], "Kava address")


DataParser(
    ParserType.EXPLORER,
    f"{WORKSHEET_NAME} ({WALLET} Transactions)",
    [
        "Transaction Hash",
        "Status",
        "Method",
        "Blockno",
        "DateTime (UTC)",
        "From",
        "FromNameTag",
        "To",
        "ToNameTag",
        "Value (KAVA)",
        "TxnFee (KAVA)"
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_kavascan,
    filename_prefix="kava",
)


DataParser(
    ParserType.EXPLORER,
    f"{WORKSHEET_NAME} ({WALLET} Token Transfers ERC-20)",
    [
        "Transaction Hash",
        "Blockno",
        "DateTime (UTC)",
        "Status",
        "From",
        "FromNameTag",
        "To",
        "ToNameTag",
        "ContractAddress",
        "TokenName",
        "TokenSymbol",
        "TokenValue",
        "TokenID"
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_kavascan_tokens,
    filename_prefix="kava",
)