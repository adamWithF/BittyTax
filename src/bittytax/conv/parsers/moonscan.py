# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2021

from decimal import Decimal

from .etherscan import _get_note
from ..out_record import TransactionOutRecord
from ..dataparser import DataParser

WALLET = "Moonriver"
WORKSHEET_NAME = "MoonScan"

def parse_moonscan(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict['UnixTimestamp']))

    if row_dict['Status'] != '':
        # Failed txns should not have a Value_OUT
        row_dict['Value_OUT(MOVR)'] = 0

    if Decimal(row_dict['Value_IN(MOVR)']) > 0:
        if row_dict['Status'] == '':
            data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_DEPOSIT,
                                                     data_row.timestamp,
                                                     buy_quantity=row_dict['Value_IN(MOVR)'],
                                                     buy_asset="MOVR",
                                                     wallet=get_wallet(row_dict['To']),
                                                     note=_get_note(row_dict))
    elif Decimal(row_dict['Value_OUT(MOVR)']) > 0:
        data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_WITHDRAWAL,
                                                 data_row.timestamp,
                                                 sell_quantity=row_dict['Value_OUT(MOVR)'],
                                                 sell_asset="MOVR",
                                                 fee_quantity=row_dict['TxnFee(MOVR)'],
                                                 fee_asset="MOVR",
                                                 wallet=get_wallet(row_dict['From']),
                                                 note=_get_note(row_dict))
    else:
        data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_SPEND,
                                                 data_row.timestamp,
                                                 sell_quantity=row_dict['Value_OUT(MOVR)'],
                                                 sell_asset="MOVR",
                                                 fee_quantity=row_dict['TxnFee(MOVR)'],
                                                 fee_asset="MOVR",
                                                 wallet=get_wallet(row_dict['From']),
                                                 note=_get_note(row_dict))

def get_wallet(address):
    return "%s-%s" % (WALLET, address.lower()[0:TransactionOutRecord.WALLET_ADDR_LEN])

def parse_moonscan_internal(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict['UnixTimestamp']))

    # Failed internal txn
    if row_dict['Status'] != '0':
        return

    if Decimal(row_dict['Value_IN(MOVR)']) > 0:
        data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_DEPOSIT,
                                                 data_row.timestamp,
                                                 buy_quantity=row_dict['Value_IN(MOVR)'],
                                                 buy_asset="MOVR",
                                                 wallet=get_wallet(row_dict['TxTo']))
    elif Decimal(row_dict['Value_OUT(MOVR)']) > 0:
        data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_WITHDRAWAL,
                                                 data_row.timestamp,
                                                 sell_quantity=row_dict['Value_OUT(MOVR)'],
                                                 sell_asset="MOVR",
                                                 wallet=get_wallet(row_dict['From']))


def parse_moonscan_tokens(data_row, _parser, **kwargs):
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
            wallet=get_wallet(row_dict["To"]),
        )
    elif row_dict["From"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=quantity,
            sell_asset=asset,
            wallet=get_wallet(row_dict["From"]),
        )
    else:
        raise DataFilenameError(kwargs["filename"], "Ethereum address")


def parse_moonscan_nfts(data_row, _parser, **kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["UnixTimestamp"]))

    if row_dict["To"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_DEPOSIT,
            data_row.timestamp,
            buy_quantity=1,
            buy_asset=f'{row_dict["TokenName"]} #{row_dict["TokenId"]}',
            wallet=get_wallet(row_dict["To"]),
        )
    elif row_dict["From"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=1,
            sell_asset=f'{row_dict["TokenName"]} #{row_dict["TokenId"]}',
            wallet=get_wallet(row_dict["From"]),
        )
    else:
        raise DataFilenameError(kwargs["filename"], "Ethereum address")

MOONSCAN_TXNS = DataParser(
        DataParser.TYPE_EXPLORER,
        f"{WORKSHEET_NAME} ({WALLET} Transactions)",
        ['Txhash', 'Blockno', 'UnixTimestamp', 'DateTime', 'From', 'To', 'ContractAddress',
         'Value_IN(MOVR)', 'Value_OUT(MOVR)', None, 'TxnFee(MOVR)', 'TxnFee(USD)',
         'Historical $Price/MOVR', 'Status', 'ErrCode', 'Method'],
        worksheet_name=WORKSHEET_NAME,
        row_handler=parse_moonscan,
        filename_prefix="moonriver",
)

MOONSCAN_INT = DataParser(
        DataParser.TYPE_EXPLORER,
        f"{WORKSHEET_NAME} ({WALLET} Internal Transactions)",
        ["Txhash","Blockno","UnixTimestamp","DateTime","ParentTxFrom","ParentTxTo",
         "ParentTxMOVR_Value","From","TxTo","ContractAddress","Value_IN(MOVR)","Value_OUT(MOVR)",
         None,"Historical $Price/MOVR","Status","ErrCode","Type"],
        worksheet_name=WORKSHEET_NAME,
        row_handler=parse_moonscan_internal,
        filename_prefix="moonriver",
)

MOONSCAN_TOKENS = DataParser(
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
    row_handler=parse_moonscan_tokens,
    filename_prefix="moonriver",
)

MOONSCAN_NFTS = DataParser(
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
    row_handler=parse_moonscan_nfts,
    filename_prefix="moonriver",
)