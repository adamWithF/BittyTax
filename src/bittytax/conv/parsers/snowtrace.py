# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2021

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

WALLET = "Avalanche"
WORKSHEET_NAME = "Snowtrace"

def parse_snowtrace(data_row: "DataRow", parser: DataParser, **_kwargs: Unpack[ParserArgs]) -> None:
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["UnixTimestamp"]))
    data_row.tx_raw = TxRawPos(
        parser.in_header.index("Transaction Hash"),
        parser.in_header.index("From"),
        parser.in_header.index("To"),
    )

    if row_dict["Status"] != "":
        # Failed transactions should not have a Value_OUT
        row_dict["Value_OUT(ETH)"] = "0"

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


def _get_wallet(address: str) -> str:
    return f"{WALLET}-{address.lower()[0 : TransactionOutRecord.WALLET_ADDR_LEN]}"


def parse_snowtrace_tokens(
    data_row: "DataRow", parser: DataParser, **kwargs: Unpack[ParserArgs]
) -> None:
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["block_unix_timestamp"]) / 1000)
    row_dict["Transaction Hash"] = row_dict["tx_hash"]
    data_row.tx_raw = TxRawPos(
        parser.in_header.index("tx_hash"),
        parser.in_header.index("from"),
        parser.in_header.index("to"),
    )

    if row_dict["token_symbol"].endswith("-LP"):
        asset = row_dict["token_symbol"] + "-" + row_dict["ContractAddress"][0:10]
    else:
        asset = row_dict["token_symbol"]

    quantity = Decimal(row_dict["token_value"].replace(",", ""))

    if row_dict["to"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TrType.DEPOSIT,
            data_row.timestamp,
            buy_quantity=quantity,
            buy_asset=asset,
            wallet=_get_wallet(row_dict["to"]),
        )
    elif row_dict["from"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TrType.WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=quantity,
            sell_asset=asset,
            wallet=_get_wallet(row_dict["from"]),
        )
    else:
        raise DataFilenameError(kwargs["filename"], "Ethereum address")

def parse_snowtrace_tokens(data_row, _parser, **kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["UnixTimestamp"]))

    if row_dict["TokenSymbol"].endswith("-LP"):
        asset = row_dict["TokenSymbol"] + "-" + row_dict["ContractAddress"][0:10]
    else:
        asset = row_dict["TokenSymbol"]

    if "Value" in row_dict:
        quantity = row_dict["Value"].replace(",", "")
    else:
        quantity = row_dict["TokenValue"].replace(",", "")

    if row_dict["To"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_DEPOSIT,
            data_row.timestamp,
            buy_quantity=quantity,
            buy_asset=asset,
            wallet=_get_wallet(row_dict["To"]),
        )
    elif row_dict["From"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=quantity,
            sell_asset=asset,
            wallet=_get_wallet(row_dict["From"]),
        )
    else:
        raise DataFilenameError(kwargs["filename"], "Ethereum address")


def parse_snowtrace_nfts(data_row, _parser, **kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["UnixTimestamp"]))

    if row_dict["To"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_DEPOSIT,
            data_row.timestamp,
            buy_quantity=1,
            buy_asset=f'{row_dict["TokenName"]} #{row_dict["TokenId"]}',
            wallet=_get_wallet(row_dict["To"]),
        )
    elif row_dict["From"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=1,
            sell_asset=f'{row_dict["TokenName"]} #{row_dict["TokenId"]}',
            wallet=_get_wallet(row_dict["From"]),
        )
    else:
        raise DataFilenameError(kwargs["filename"], "Ethereum address")


    # ["Txhash","Blockno","UnixTimestamp","DateTime","From","To","ContractAddress","Value_IN(AVAX)","Value_OUT(AVAX)",None,"TxnFee(AVAX)","TxnFee(USD)","Historical $Price/AVAX","Status","ErrCode","Method"],


# Tokens and internal transactions have the same header as Etherscan
avax_txns = DataParser(
    DataParser.EXPLORER,
    f"{WORKSHEET_NAME} ({WALLET} Transactions)",
    ["Transaction Hash","Blockno","UnixTimestamp","DateTime","From","To","ContractAddress","Value_IN(AVAX)","Value_OUT(AVAX)",CurrentValue/AVAX,"TxnFee(AVAX)","TxnFee(USD)","Historical $Price/AVAX","Status","ErrCode","Method", "ChainId", "Chain", "Value(AVAX)"],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_snowtrace,
    filename_prefix="avalanche",
)

DataParser(
    ParserType.EXPLORER,
    f"{WORKSHEET_NAME} ({WALLET} Transactions)",
    [
        "Transaction Hash",
        "Blockno",
        "UnixTimestamp",
        "DateTime (UTC)",
        "From",
        "To",
        "ContractAddress",
        "Value_IN(AVAX)",
        "Value_OUT(AVAX)",
        "CurrentValue/AVAX",
        "TxnFee(AVAX)",
        "TxnFee(USD)",
        "Historical $Price/AVAX",
        "Status",
        "ErrCode",
        "Method",
        "ChainId",
        "Chain",
        "Value(AVAX)",
        "PrivateNote",
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_snowtrace,
    filename_prefix="avalanche",
)

avax_tokens = DataParser(
    ParserType.EXPLORER,
    f"{WORKSHEET_NAME} ({WALLET} Token Transfers ERC-20)",
    [
        "chain_id",
        "tx_hash",
        "block_number",
        "block_unix_timestamp",
        "block_datetime",
        "from",
        "to",
        "token_value",
        "token_address",
        "token_name",
        "token_symbol",
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_snowtrace_tokens,
    filename_prefix="avalanche",
)

avax_int = DataParser(
    DataParser.EXPLORER,
    f"{WORKSHEET_NAME} ({WALLET} Internal Transactions)",
    ["Txhash","Blockno","UnixTimestamp","DateTime","ParentTxFrom","ParentTxTo","ParentTxAVAX_Value","From","TxTo","ContractAddress","Value_IN(AVAX)","Value_OUT(AVAX)","CurrentValue @ $11.51/AVAX","Historical $Price/AVAX","Status","ErrCode","Type"],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_snowtrace_internal,
    filename_prefix="avalanche",
)


avax_nfts = DataParser(
    DataParser.EXPLORER,
    f"{WORKSHEET_NAME} ({WALLET} ERC-721 NFTs)",
    [
        "Txhash",
        "Blockno",  # New field
        "UnixTimestamp",
        "DateTime",
        "From",
        "To",
        "ContractAddress",
        "TokenId",
        "TokenName",
        "TokenSymbol",
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_snowtrace_nfts,
    filename_prefix="avalanche",
)