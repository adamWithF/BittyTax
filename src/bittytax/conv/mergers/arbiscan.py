# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2023

from .etherscan import _do_merge_etherscan
from ..datamerge import DataMerge, ParserRequired
from ..out_record import TransactionOutRecord
from ..parsers.arbiscan import WALLET, WORKSHEET_NAME, ARBISCAN_TXNS, ARBISCAN_TOKENS, ARBISCAN_NFTS, ARBISCAN_INT
from .etherscan import TOKENS, TXNS, NFTS, INTERNAL_TXNS

STAKE_ADDRESSES = []

def merge_arbiscan(data_files):
    # Do same merge as Etherscan
    merge = _do_merge_etherscan(data_files, STAKE_ADDRESSES)

    if merge:
        # Change Etherscan parsers to FantomScan
        if TOKENS in data_files:
            data_files[TOKENS].parser.worksheet_name = WORKSHEET_NAME
            for data_row in data_files[TOKENS].data_rows:
                if data_row.t_record:
                    address = data_row.t_record.wallet[- abs(TransactionOutRecord.WALLET_ADDR_LEN):]
                    data_row.t_record.wallet = "%s-%s" % (WALLET, address)

        if NFTS in data_files:
            data_files[NFTS].parser.worksheet_name = WORKSHEET_NAME
            for data_row in data_files[NFTS].data_rows:
                if data_row.t_record:
                    address = data_row.t_record.wallet[- abs(TransactionOutRecord.WALLET_ADDR_LEN):]
                    data_row.t_record.wallet = "%s-%s" % (WALLET, address)

    return merge

DataMerge("ArbiScan fees & multi-token transactions",
          {TXNS: {'req': ParserRequired.MANDATORY, 'obj': ARBISCAN_TXNS},
           TOKENS: {'req': ParserRequired.OPTIONAL, 'obj': ARBISCAN_TOKENS},
           NFTS: {'req': ParserRequired.OPTIONAL, 'obj': ARBISCAN_NFTS},
           INTERNAL_TXNS: {'req': ParserRequired.OPTIONAL, 'obj': ARBISCAN_INT}},
          merge_arbiscan)