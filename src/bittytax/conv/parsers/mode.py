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

WALLET = "Mode"
WORKSHEET_NAME = "Mode Explorer"

def parse_mode_explorer(data_row: "DataRow", parser: DataParser, **_kwargs: Unpack[ParserArgs]) -> None:
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
                buy_quantity=Decimal(row_dict["Value_IN(ETH)"]) / 10**18,
                buy_asset="ETH",
                wallet=_get_wallet(row_dict["To"]),
                note=_get_note(row_dict),
            )
    elif Decimal(row_dict["Value_OUT(ETH)"]) > 0:
        data_row.t_record = TransactionOutRecord(
            TrType.WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=Decimal(row_dict["Value_OUT(ETH)"]) / 10**18,
            sell_asset="ETH",
            fee_quantity=Decimal(row_dict["TxnFee(ETH)"]),
            fee_asset="ETH",
            wallet=_get_wallet(row_dict["From"]),
            note=_get_note(row_dict),
        )
    else:
        data_row.t_record = TransactionOutRecord(
            TrType.SPEND,
            data_row.timestamp,
            sell_quantity=Decimal(row_dict["Value_OUT(ETH)"]),
            sell_asset="ETH",
            fee_quantity=Decimal(row_dict["TxnFee(ETH)"]),
            fee_asset="ETH",
            wallet=_get_wallet(row_dict["From"]),
            note=_get_note(row_dict),
        )


def _get_wallet(address: str) -> str:
    return f"{WALLET}-{address.lower()[0 : TransactionOutRecord.WALLET_ADDR_LEN]}"


def parse_mode_tokens(
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

def parse_mode_tokens(data_row, _parser, **kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict["block_datetime"])

    if row_dict["token_symbol"].endswith("-LP"):
        asset = row_dict["token_symbol"] + "-" + row_dict["token_address"][0:10]
    else:
        asset = row_dict["token_symbol"]

    if "token_value" in row_dict:
        quantity = row_dict["token_value"].replace(",", "")
    else:
        quantity = row_dict["token_value"].replace(",", "")

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

def parse_mode_internal(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict['UnixTimestamp']))

    # Failed internal txn
    if row_dict['Status'] != '0':
        return

    if Decimal(row_dict['Value_IN(ETH)']) > 0:
        data_row.t_record = TransactionOutRecord(TrType.DEPOSIT,
                                                 data_row.timestamp,
                                                 buy_quantity=row_dict['Value_IN(FTM)'],
                                                 buy_asset="FTM",
                                                 wallet=get_wallet(row_dict['TxTo']))
    elif Decimal(row_dict['Value_OUT(FTM)']) > 0:
        data_row.t_record = TransactionOutRecord(TrType.WITHDRAWAL,
                                                 data_row.timestamp,
                                                 sell_quantity=row_dict['Value_OUT(FTM)'],
                                                 sell_asset="FTM",
                                                 wallet=get_wallet(row_dict['From']))

def parse_mode_nfts(data_row, _parser, **kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["UnixTimestamp"]))

    if row_dict["To"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TrType.DEPOSIT,
            data_row.timestamp,
            buy_quantity=1,
            buy_asset=f'{row_dict["TokenName"]} #{row_dict["TokenId"]}',
            wallet=_get_wallet(row_dict["To"]),
        )
    elif row_dict["From"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TrType.WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=1,
            sell_asset=f'{row_dict["TokenName"]} #{row_dict["TokenId"]}',
            wallet=_get_wallet(row_dict["From"]),
        )
    else:
        raise DataFilenameError(kwargs["filename"], "Ethereum address")


# Tokens and internal transactions have the same header as Etherscan
mode_txns = DataParser(
    ParserType.EXPLORER,
    f"{WORKSHEET_NAME} ({WALLET} Transactions)",
    ["Transaction Hash","Blockno","UnixTimestamp","DateTime","From","To","ContractAddress","Value_IN(ETH)","Value_OUT(ETH)","CurrentValue/ETH","TxnFee(ETH)","TxnFee(USD)","Historical $Price/ETH","Status","ErrCode","Method", "ChainId", "Chain", "Value(ETH)"],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_mode_explorer,
    filename_prefix="mode",
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
        "Value_IN(ETH)",
        "Value_OUT(ETH)",
        "CurrentValue/Eth",
        "TxnFee(ETH)",
        "TxnFee(USD)",
        "Historical $Price/Eth",
        "Status",
        "ErrCode",
        "Method",
        "ChainId",
        "Chain",
        "Value(ETH)",
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_mode_explorer,
    filename_prefix="mode",
)

mode_tokens = DataParser(
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
    row_handler=parse_mode_tokens,
    filename_prefix="mode",
)

mode_int = DataParser(
    ParserType.EXPLORER,
    f"{WORKSHEET_NAME} ({WALLET} Internal Transactions)",
    ["Txhash","Blockno","UnixTimestamp","DateTime","ParentTxFrom","ParentTxTo","ParentTxETH_Value","From","TxTo","ContractAddress","Value_IN(ETH)","Value_OUT(ETH)","CurrentValue @ $11.51/ETH","Historical $Price/ETH","Status","ErrCode","Type"],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_mode_internal,
    filename_prefix="mode",
)

mode_nfts = DataParser(
    ParserType.EXPLORER,
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
    row_handler=parse_mode_nfts,
    filename_prefix="mode",
)