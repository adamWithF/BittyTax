# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2021

from .etherscan import _do_merge_etherscan
from ..datamerge import DataMerge
from ..out_record import TransactionOutRecord
from ..parsers.moonscan import MOONSCAN_TXNS, MOONSCAN_INT, MOONSCAN_TOKENS, MOONSCAN_NFTS, WALLET, WORKSHEET_NAME

STAKE_ADDRESSES = [
    "0x98878b06940ae243284ca214f92bb71a2b032b8a", # MOVR
]

def merge_moonscan(data_files):
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

DataMerge("FantomScan fees & multi-token transactions",
          {TXNS: {'req': DataMerge.MANDATORY, 'obj': MOONSCAN_TXNS},
           TOKENS: {'req': DataMerge.OPTIONAL, 'obj': MOONSCAN_TOKENS},
           NFTS: {'req': DataMerge.OPTIONAL, 'obj': MOONSCAN_NFTS},
           INTERNAL_TXNS: {'req': DataMerge.OPTIONAL, 'obj': MOONSCAN_INT}},
          merge_moonscan)