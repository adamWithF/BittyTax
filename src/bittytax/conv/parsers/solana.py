# -*- coding: utf-8 -*-
# (c)

# Support for Solana via solscan

import time

from ..out_record import TransactionOutRecord
from ..dataparser import DataParser, ParserArgs, ParserType

WALLET = "Solana"
WORKSHEET_NAME = "Solana SolScan"

def parse_solana(data_row, _parser, **kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict['BlockTime'])

    if row_dict['Type'] == 'SolTransfer':
        if row_dict['SolTransfer Destination'] in kwargs['filename']:
            data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_DEPOSIT,
                                                     data_row.timestamp,
                                                     buy_quantity=abs(float(row_dict['Amount (SOL)'].replace(',', ''))),
                                                     buy_asset=row_dict['Symbol(off-chain)'],
                                                     fee_quantity=row_dict['Fee (SOL)'],
                                                     fee_asset=row_dict['Symbol(off-chain)'],
                                                     wallet=get_wallet(row_dict['SolTransfer Destination']))

        else:
            data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_WITHDRAWAL,
                                                     data_row.timestamp,
                                                     sell_quantity=abs(float(row_dict['Amount (SOL)'].replace(',', ''))),
                                                     sell_asset=row_dict['Symbol(off-chain)'],
                                                     fee_quantity=row_dict['Fee (SOL)'],
                                                     fee_asset=row_dict['Symbol(off-chain)'],
                                                     wallet=get_wallet(row_dict['SolTransfer Source']))

def get_wallet(address):
    return "%s-%s" % (WALLET, address.lower()[0:TransactionOutRecord.WALLET_ADDR_LEN])

def get_wallet_address(filename):
    return filename.split('-')[0]


solscan_txns = DataParser(
    ParserType.EXPLORER,
    f"{WALLET} ({WORKSHEET_NAME} Transactions)",
    ['Type', 'Txhash', 'BlockTime Unix', 'BlockTime', 'Fee (SOL)', 'TokenAccount', 'ChangeType', 'SPL BalanceChange', 'PreBalancer', 'PostBalancer', 'TokenAddress', 'TokenName(off-chain)', 'Symbol(off-chain)', 'SolTransfer Source', 'SolTransfer Destination', 'Amount (SOL)'],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_solana)