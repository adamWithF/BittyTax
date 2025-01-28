# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2023

import ntpath
from decimal import Decimal

from .etherscan import _get_note
from ..out_record import TransactionOutRecord
from ..dataparser import DataParser, ParserType

WALLET = "Optimism"
WORKSHEET_NAME = "Optimistic Ethereum Scanner"

def parse_optimism(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict['UnixTimestamp']))

    if row_dict['Status'] != '':
        # Failed txns should not have a Value_OUT
        row_dict['Value_OUT(ETH)'] = 0

    if Decimal(row_dict['Value_IN(ETH)']) > 0:
        if row_dict['Status'] == '':
            data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_DEPOSIT,
                                                     data_row.timestamp,
                                                     buy_quantity=row_dict['Value_IN(ETH)'],
                                                     buy_asset="ETH",
                                                     wallet=get_wallet(row_dict['To']),
                                                     note=_get_note(row_dict))
    elif Decimal(row_dict['Value_OUT(ETH)']) > 0:
        data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_WITHDRAWAL,
                                                 data_row.timestamp,
                                                 sell_quantity=row_dict['Value_OUT(ETH)'],
                                                 sell_asset="ETH",
                                                 fee_quantity=row_dict['TxnFee(ETH)'],
                                                 fee_asset="ETH",
                                                 wallet=get_wallet(row_dict['From']),
                                                 note=_get_note(row_dict))
    else:
        data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_SPEND,
                                                 data_row.timestamp,
                                                 sell_quantity=row_dict['Value_OUT(ETH)'],
                                                 sell_asset="ETH",
                                                 fee_quantity=row_dict['TxnFee(ETH)'],
                                                 fee_asset="ETH",
                                                 wallet=get_wallet(row_dict['From']),
                                                 note=_get_note(row_dict))

def get_wallet(address):
    return "%s-%s" % (WALLET, address.lower()[0:TransactionOutRecord.WALLET_ADDR_LEN])

def parse_optimism_internal(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["UnixTimestamp"]))

    # Failed internal transaction
    if row_dict["Status"] != "0":
        return

    if Decimal(row_dict["Value_IN(ETH)"]) > 0:
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_DEPOSIT,
            data_row.timestamp,
            buy_quantity=row_dict["Value_IN(ETH)"],
            buy_asset="ETH",
            wallet=get_wallet(row_dict["TxTo"]),
        )
    elif Decimal(row_dict["Value_OUT(ETH)"]) > 0:
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=row_dict["Value_OUT(ETH)"],
            sell_asset="ETH",
            wallet=get_wallet(row_dict["From"]),
        )


def parse_optimism_tokens(data_row, _parser, **kwargs):
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


def parse_optimism_nfts(data_row, _parser, **kwargs):
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

def parse_optimism_deposits(data_row, _parser, **kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["UnixTimestamp"]))

    if row_dict["Token Symbol"].endswith("-LP"):
        asset = row_dict["Token Symbol"] + "-" + row_dict["Contract Address"][0:10]
    else:
        asset = row_dict["Token Symbol"]

    quantity = row_dict["Value"].replace(",", "")

    to = ntpath.basename(kwargs["filename"]).split('-')[1].lower()

    data_row.t_record = TransactionOutRecord(
        TransactionOutRecord.TYPE_DEPOSIT,
        data_row.timestamp,
        buy_quantity=quantity,
        buy_asset=asset,
        wallet=get_wallet(to),
    )

def parse_optimism_withdrawals(data_row, _parser, **kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["UnixTimestamp"]))

    # TODO probably check if status is not failed
    # if row_dict["Status"]:

    if row_dict["Token Symbol"].endswith("-LP"):
        asset = row_dict["Token Symbol"] + "-" + row_dict["Contract Address"][0:10]
    else:
        asset = row_dict["Token Symbol"]

    quantity = row_dict["Value"].replace(",", "")

    to = ntpath.basename(kwargs["filename"]).split('-')[1].lower()

    data_row.t_record = TransactionOutRecord(
        TransactionOutRecord.TYPE_WITHDRAWAL,
        data_row.timestamp,
        sell_quantity=quantity,
        sell_asset=asset,
        wallet=get_wallet(to), # assume same wallet
    )


OPTIMISM_TXNS = DataParser(
        ParserType.EXPLORER,
        f"{WORKSHEET_NAME} ({WALLET} Transactions)",
    ["Txhash","Blockno","UnixTimestamp","DateTime","From","To","ContractAddress","Value_IN(ETH)","Value_OUT(ETH)", None, "TxnFee(ETH)","TxnFee(USD)","Historical $Price/Eth","Status","ErrCode","Method"],
        worksheet_name=WORKSHEET_NAME,
        row_handler=parse_optimism,
        filename_prefix="optimism",
)

OPTIMISM_INT = DataParser(
        ParserType.EXPLORER,
        f"{WORKSHEET_NAME} ({WALLET} Internal Transactions)",
    ["Txhash","Blockno","UnixTimestamp","DateTime","ParentTxFrom","ParentTxTo","ParentTxETH_Value","From","TxTo","ContractAddress","Value_IN(ETH)","Value_OUT(ETH)",None,"Historical $Price/Eth","Status","ErrCode","Type"],
        worksheet_name=WORKSHEET_NAME,
        row_handler=parse_optimism_internal,
        filename_prefix="optimism",
)

OPTIMISM_DEPOSITS = DataParser(
        ParserType.EXPLORER,
        f"{WORKSHEET_NAME} ({WALLET} Deposits)",
        ["L1 Deposit Txhash","L2 Txhash","UnixTimestamp","DateTime","Value","Token Name","Token Symbol","Contract Address"],
        worksheet_name=WORKSHEET_NAME,
        row_handler=parse_optimism_deposits,
        filename_prefix="optimism",
)

OPTIMISM_WITHDRAWALS = DataParser(
        ParserType.EXPLORER,
        f"{WORKSHEET_NAME} ({WALLET} Withdrawals)",
        ["L2 Txhash","UnixTimestamp","DateTime","L1 Txhash","Value","Token Name","Token Symbol","Contract Address","Status"],
        worksheet_name=WORKSHEET_NAME,
        row_handler=parse_optimism_withdrawals,
        filename_prefix="optimism",
)

OPTIMISM_TOKENS = DataParser(
    ParserType.EXPLORER,
    f"{WORKSHEET_NAME} ({WALLET} Address - ERC20 Token Transfers)",
    [
        "Txhash",
        "UnixTimestamp",
        "DateTime",
        "From",
        "To",
        "TokenValue",
        "USDValueDayOfTx",
        "ContractAddress",
        "TokenName",
        "TokenSymbol",
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_optimism_tokens,
    filename_prefix="optimism",
)

OPTIMISM_NFTS = DataParser(
    ParserType.EXPLORER,
    f"{WORKSHEET_NAME} ({WALLET} Address - ERC721 Token Transfers)",
    ["Txhash","UnixTimestamp","DateTime","From","To","ContractAddress","TokenId","TokenName","TokenSymbol"],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_optimism_nfts,
    filename_prefix="optimism",
)