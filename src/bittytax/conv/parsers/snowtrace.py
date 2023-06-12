# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2021

from decimal import Decimal

from ..dataparser import DataParser
from ..out_record import TransactionOutRecord
from .etherscan import _get_note

WALLET = "Avalanche"
WORKSHEET_NAME = "SnowTrace"


def parse_snowtrace(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["UnixTimestamp"]))

    if row_dict["Status"] != "":
        # Failed transactions should not have a Value_OUT
        row_dict["Value_OUT(AVAX)"] = 0

    if Decimal(row_dict["Value_IN(AVAX)"]) > 0:
        if row_dict["Status"] == "":
            data_row.t_record = TransactionOutRecord(
                TransactionOutRecord.TYPE_DEPOSIT,
                data_row.timestamp,
                buy_quantity=row_dict["Value_IN(AVAX)"],
                buy_asset="AVAX",
                wallet=_get_wallet(row_dict["To"]),
                note=_get_note(row_dict),
            )
    elif Decimal(row_dict["Value_OUT(AVAX)"]) > 0:
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=row_dict["Value_OUT(AVAX)"],
            sell_asset="AVAX",
            fee_quantity=row_dict["TxnFee(AVAX)"],
            fee_asset="AVAX",
            wallet=_get_wallet(row_dict["From"]),
            note=_get_note(row_dict),
        )
    else:
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_SPEND,
            data_row.timestamp,
            sell_quantity=row_dict["Value_OUT(AVAX)"],
            sell_asset="AVAX",
            fee_quantity=row_dict["TxnFee(AVAX)"],
            fee_asset="AVAX",
            wallet=_get_wallet(row_dict["From"]),
            note=_get_note(row_dict),
        )


def _get_wallet(address):
    return f"{WALLET}-{address.lower()[0 : TransactionOutRecord.WALLET_ADDR_LEN]}"


def parse_snowtrace_internal(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["UnixTimestamp"]))

    # Failed internal transaction
    if row_dict["Status"] != "0":
        return

    if Decimal(row_dict["Value_IN(AVAX)"]) > 0:
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_DEPOSIT,
            data_row.timestamp,
            buy_quantity=row_dict["Value_IN(AVAX)"],
            buy_asset="AVAX",
            wallet=_get_wallet(row_dict["TxTo"]),
        )
    elif Decimal(row_dict["Value_OUT(AVAX)"]) > 0:
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=row_dict["Value_OUT(AVAX)"],
            sell_asset="AVAX",
            wallet=_get_wallet(row_dict["From"]),
        )

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


# Tokens and internal transactions have the same header as Etherscan
AVAX_TXNS = DataParser(
    DataParser.TYPE_EXPLORER,
    f"{WORKSHEET_NAME} ({WALLET} Transactions)",
    ["Txhash","Blockno","UnixTimestamp","DateTime","From","To","ContractAddress","Value_IN(AVAX)","Value_OUT(AVAX)",None,"TxnFee(AVAX)","TxnFee(USD)","Historical $Price/AVAX","Status","ErrCode","Method"],

    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_snowtrace,
    filename_prefix="avalanche",
)

AVAX_INT = DataParser(
    DataParser.TYPE_EXPLORER,
    f"{WORKSHEET_NAME} ({WALLET} Internal Transactions)",
    ["Txhash","Blockno","UnixTimestamp","DateTime","ParentTxFrom","ParentTxTo","ParentTxAVAX_Value","From","TxTo","ContractAddress","Value_IN(AVAX)","Value_OUT(AVAX)","CurrentValue @ $11.51/AVAX","Historical $Price/AVAX","Status","ErrCode","Type"],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_snowtrace_internal,
    filename_prefix="avalanche",
)

AVAX_TOKENS = DataParser(
    DataParser.TYPE_EXPLORER,
    f"{WORKSHEET_NAME} ({WALLET} ERC-20 Tokens)",
    [
        "Txhash",
        "Blockno",  # New field
        "UnixTimestamp",
        "DateTime",
        "From",
        "To",
        "TokenValue",  # Renamed
        "USDValueDayOfTx",  # New field
        "ContractAddress",  # New field
        "TokenName",
        "TokenSymbol",
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_snowtrace_tokens,
    filename_prefix="avalanche",
)

AVAX_NFTS = DataParser(
    DataParser.TYPE_EXPLORER,
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