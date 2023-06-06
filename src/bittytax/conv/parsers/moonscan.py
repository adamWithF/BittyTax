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

moonscan_txns = DataParser(
        DataParser.TYPE_EXPLORER,
        "MoonScan (MOVR Transactions)",
        ['Txhash', 'Blockno', 'UnixTimestamp', 'DateTime', 'From', 'To', 'ContractAddress',
         'Value_IN(MOVR)', 'Value_OUT(MOVR)', None, 'TxnFee(MOVR)', 'TxnFee(USD)',
         'Historical $Price/MOVR', 'Status', 'ErrCode', 'Method'],
        worksheet_name=WORKSHEET_NAME,
        row_handler=parse_moonscan)

# DataParser(DataParser.TYPE_EXPLORER,
#            "FtmScan (MOVR Transactions)",
#            ['Txhash', 'Blockno', 'UnixTimestamp', 'DateTime', 'From', 'To', 'ContractAddress',
#             'Value_IN(MOVR)', 'Value_OUT(MOVR)', None, 'TxnFee(MOVR)', 'TxnFee(USD)',
#             'Historical $Price/MOVR', 'Status', 'ErrCode', 'Method', 'PrivateNote'],
#            worksheet_name=WORKSHEET_NAME,
#            row_handler=parse_moonscan)

moonscan_int = DataParser(
        DataParser.TYPE_EXPLORER,
        "FtmScan (MOVR Internal Transactions)",
        ["Txhash","Blockno","UnixTimestamp","DateTime","ParentTxFrom","ParentTxTo",
         "ParentTxMOVR_Value","From","TxTo","ContractAddress","Value_IN(MOVR)","Value_OUT(MOVR)",
         None,"Historical $Price/MOVR","Status","ErrCode","Type"],
        worksheet_name=WORKSHEET_NAME,
        row_handler=parse_moonscan_internal)

# Same header as Etherscan
#DataParser(DataParser.TYPE_EXPLORER,
#           "FtmScan (ERC-20 Tokens)",
#           ['Txhash', 'UnixTimestamp', 'DateTime', 'From', 'To', 'Value', 'ContractAddress',
#            'TokenName', 'TokenSymbol'],
#           worksheet_name=WORKSHEET_NAME,
#           row_handler=parse_fantomscan_tokens)

# Same header as Etherscan
#DataParser(DataParser.TYPE_EXPLORER,
#           "FtmScan (ERC-721 NFTs)",
#           ['Txhash', 'UnixTimestamp', 'DateTime', 'From', 'To', 'ContractAddress', 'TokenId',
#            'TokenName', 'TokenSymbol'],
#           worksheet_name=WORKSHEET_NAME,
#           row_handler=parse_fantomscan_nfts)
