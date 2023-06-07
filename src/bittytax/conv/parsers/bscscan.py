# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2021

from decimal import Decimal

from ..dataparser import DataParser
from ..out_record import TransactionOutRecord
from .etherscan import _get_note

WALLET = "Binance Smart Chain"
WORKSHEET_NAME = "BscScan"


def parse_bscscan(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["UnixTimestamp"]))

    if row_dict["Status"] != "":
        # Failed transactions should not have a Value_OUT
        row_dict["Value_OUT(BNB)"] = 0

    if Decimal(row_dict["Value_IN(BNB)"]) > 0:
        if row_dict["Status"] == "":
            data_row.t_record = TransactionOutRecord(
                TransactionOutRecord.TYPE_DEPOSIT,
                data_row.timestamp,
                buy_quantity=row_dict["Value_IN(BNB)"],
                buy_asset="BNB",
                wallet=_get_wallet(row_dict["To"]),
                note=_get_note(row_dict),
            )
    elif Decimal(row_dict["Value_OUT(BNB)"]) > 0:
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=row_dict["Value_OUT(BNB)"],
            sell_asset="BNB",
            fee_quantity=row_dict["TxnFee(BNB)"],
            fee_asset="BNB",
            wallet=_get_wallet(row_dict["From"]),
            note=_get_note(row_dict),
        )
    else:
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_SPEND,
            data_row.timestamp,
            sell_quantity=row_dict["Value_OUT(BNB)"],
            sell_asset="BNB",
            fee_quantity=row_dict["TxnFee(BNB)"],
            fee_asset="BNB",
            wallet=_get_wallet(row_dict["From"]),
            note=_get_note(row_dict),
        )


def _get_wallet(address):
    return f"{WALLET}-{address.lower()[0 : TransactionOutRecord.WALLET_ADDR_LEN]}"


def parse_bscscan_internal(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["UnixTimestamp"]))

    # Failed internal transaction
    if row_dict["Status"] != "0":
        return

    if Decimal(row_dict["Value_IN(BNB)"]) > 0:
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_DEPOSIT,
            data_row.timestamp,
            buy_quantity=row_dict["Value_IN(BNB)"],
            buy_asset="BNB",
            wallet=_get_wallet(row_dict["TxTo"]),
        )
    elif Decimal(row_dict["Value_OUT(BNB)"]) > 0:
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=row_dict["Value_OUT(BNB)"],
            sell_asset="BNB",
            wallet=_get_wallet(row_dict["From"]),
        )


def parse_bscscan_tokens(data_row, _parser, **kwargs):
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


def parse_bscscan_nfts(data_row, _parser, **kwargs):
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
BSC_TXNS = DataParser(
    DataParser.TYPE_EXPLORER,
    "BscScan (BSC Transactions)",
    [
        "Txhash",
        "Blockno",
        "UnixTimestamp",
        "DateTime",
        "From",
        "To",
        "ContractAddress",
        "Value_IN(BNB)",
        "Value_OUT(BNB)",
        None,
        "TxnFee(BNB)",
        "TxnFee(USD)",
        "Historical $Price/BNB",
        "Status",
        "ErrCode",
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_bscscan,
)

DataParser(
    DataParser.TYPE_EXPLORER,
    "BscScan (BSC Transactions)",
    [
        "Txhash",
        "Blockno",
        "UnixTimestamp",
        "DateTime",
        "From",
        "To",
        "ContractAddress",
        "Value_IN(BNB)",
        "Value_OUT(BNB)",
        None,
        "TxnFee(BNB)",
        "TxnFee(USD)",
        "Historical $Price/BNB",
        "Status",
        "ErrCode",
        "PrivateNote",
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_bscscan,
)

DataParser(
    DataParser.TYPE_EXPLORER,
    "BscScan (BSC Transactions)",
    [
        "Txhash",
        "Blockno",
        "UnixTimestamp",
        "DateTime",
        "From",
        "To",
        "ContractAddress",
        "Value_IN(BNB)",
        "Value_OUT(BNB)",
        None,
        "TxnFee(BNB)",
        "TxnFee(USD)",
        "Historical $Price/BNB",
        "Status",
        "ErrCode",
        "Method",
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_bscscan,
)

DataParser(
    DataParser.TYPE_EXPLORER,
    "BscScan (BSC Transactions)",
    [
        "Txhash",
        "Blockno",
        "UnixTimestamp",
        "DateTime",
        "From",
        "To",
        "ContractAddress",
        "Value_IN(BNB)",
        "Value_OUT(BNB)",
        None,
        "TxnFee(BNB)",
        "TxnFee(USD)",
        "Historical $Price/BNB",
        "Status",
        "ErrCode",
        "Method",
        "PrivateNote",
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_bscscan,
)

BSC_INT = DataParser(
    DataParser.TYPE_EXPLORER,
    "BscScan (BSC Internal Transactions)",
    [
        "Txhash",
        "Blockno",
        "UnixTimestamp",
        "DateTime",
        "ParentTxFrom",
        "ParentTxTo",
        "ParentTxETH_Value",
        "From",
        "TxTo",
        "ContractAddress",
        "Value_IN(BNB)",
        "Value_OUT(BNB)",
        None,
        "Historical $Price/BNB",
        "Status",
        "ErrCode",
        "Type",
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_bscscan_internal,
)

DataParser(
    DataParser.TYPE_EXPLORER,
    "BscScan (BSC Internal Transactions)",
    [
        "Txhash",
        "Blockno",
        "UnixTimestamp",
        "DateTime",
        "ParentTxFrom",
        "ParentTxTo",
        "ParentTxETH_Value",
        "From",
        "TxTo",
        "ContractAddress",
        "Value_IN(BNB)",
        "Value_OUT(BNB)",
        None,
        "Historical $Price/BNB",
        "Status",
        "ErrCode",
        "Type",
        "PrivateNote",
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_bscscan_internal,
)

BSCSCAN_TOKENS = DataParser(
    DataParser.TYPE_EXPLORER,
    f"{WORKSHEET_NAME} (ERC-20 Tokens)",
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
    row_handler=parse_bscscan_tokens,
)

DataParser(
    DataParser.TYPE_EXPLORER,
    f"{WORKSHEET_NAME} (ERC-20 Tokens)",
    [
        "Txhash",
        "UnixTimestamp",
        "DateTime",
        "From",
        "To",
        "Value",
        "ContractAddress",
        "TokenName",
        "TokenSymbol",
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_bscscan_tokens,
)

BSCSCAN_NFTS = DataParser(
    DataParser.TYPE_EXPLORER,
    f"{WORKSHEET_NAME} (ERC-721 NFTs)",
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
    row_handler=parse_bscscan_nfts,
)

DataParser(
    DataParser.TYPE_EXPLORER,
    f"{WORKSHEET_NAME} (ERC-721 NFTs)",
    [
        "Txhash",
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
    row_handler=parse_bscscan_nfts,
)