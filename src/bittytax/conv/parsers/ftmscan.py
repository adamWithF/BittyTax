# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2021

from decimal import Decimal

from .etherscan import get_note
from ..out_record import TransactionOutRecord
from ..dataparser import DataParser

WALLET = "Fantom chain"
WORKSHEET_NAME = "FtmScan"

def parse_fantomscan(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict['UnixTimestamp']))

    if row_dict['Status'] != '':
        # Failed txns should not have a Value_OUT
        row_dict['Value_OUT(FTM)'] = 0

    if Decimal(row_dict['Value_IN(FTM)']) > 0:
        if row_dict['Status'] == '':
            data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_DEPOSIT,
                                                     data_row.timestamp,
                                                     buy_quantity=row_dict['Value_IN(FTM)'],
                                                     buy_asset="FTM",
                                                     wallet=get_wallet(row_dict['To']),
                                                     note=get_note(row_dict))
    elif Decimal(row_dict['Value_OUT(FTM)']) > 0:
        data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_WITHDRAWAL,
                                                 data_row.timestamp,
                                                 sell_quantity=row_dict['Value_OUT(FTM)'],
                                                 sell_asset="FTM",
                                                 fee_quantity=row_dict['TxnFee(FTM)'],
                                                 fee_asset="FTM",
                                                 wallet=get_wallet(row_dict['From']),
                                                 note=get_note(row_dict))
    else:
        data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_SPEND,
                                                 data_row.timestamp,
                                                 sell_quantity=row_dict['Value_OUT(FTM)'],
                                                 sell_asset="FTM",
                                                 fee_quantity=row_dict['TxnFee(FTM)'],
                                                 fee_asset="FTM",
                                                 wallet=get_wallet(row_dict['From']),
                                                 note=get_note(row_dict))

def get_wallet(address):
    return "%s-%s" % (WALLET, address.lower()[0:TransactionOutRecord.WALLET_ADDR_LEN])

def parse_fantomscan_internal(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict['UnixTimestamp']))

    # Failed internal txn
    if row_dict['Status'] != '0':
        return

    if Decimal(row_dict['Value_IN(FTM)']) > 0:
        data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_DEPOSIT,
                                                 data_row.timestamp,
                                                 buy_quantity=row_dict['Value_IN(FTM)'],
                                                 buy_asset="FTM",
                                                 wallet=get_wallet(row_dict['TxTo']))
    elif Decimal(row_dict['Value_OUT(FTM)']) > 0:
        data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_WITHDRAWAL,
                                                 data_row.timestamp,
                                                 sell_quantity=row_dict['Value_OUT(FTM)'],
                                                 sell_asset="FTM",
                                                 wallet=get_wallet(row_dict['From']))

fantom_txns = DataParser(
        DataParser.TYPE_EXPLORER,
        "FtmScan (FTM Transactions)",
        ['Txhash', 'Blockno', 'UnixTimestamp', 'DateTime', 'From', 'To', 'ContractAddress',
         'Value_IN(FTM)', 'Value_OUT(FTM)', None, 'TxnFee(FTM)', 'TxnFee(USD)',
         'Historical $Price/FTM', 'Status', 'ErrCode', 'Method'],
        worksheet_name=WORKSHEET_NAME,
        row_handler=parse_fantomscan)

DataParser(DataParser.TYPE_EXPLORER,
           "FtmScan (FTM Transactions)",
           ['Txhash', 'Blockno', 'UnixTimestamp', 'DateTime', 'From', 'To', 'ContractAddress',
            'Value_IN(FTM)', 'Value_OUT(FTM)', None, 'TxnFee(FTM)', 'TxnFee(USD)',
            'Historical $Price/FTM', 'Status', 'ErrCode', 'Method', 'PrivateNote'],
           worksheet_name=WORKSHEET_NAME,
           row_handler=parse_fantomscan)

fantom_int = DataParser(
        DataParser.TYPE_EXPLORER,
        "FtmScan (FTM Internal Transactions)",
        ['Txhash', 'Blockno', 'UnixTimestamp', 'DateTime', 'ParentTxFrom', 'ParentTxTo',
         'ParentTxFTM_Value', 'From', 'TxTo', 'ContractAddress', 'Value_IN(FTM)',
         'Value_OUT(FTM)', None, 'Historical $Price/FTM', 'Status', 'ErrCode', 'Type'],
        worksheet_name=WORKSHEET_NAME,
        row_handler=parse_fantomscan_internal)

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
