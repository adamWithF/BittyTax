# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2021

from .etherscan import _do_merge_etherscan, TXNS, TOKENS, NFTS, INTERNAL_TXNS
from ..datamerge import DataMerge
from ..out_record import TransactionOutRecord
from ..parsers.ftmscan import FANTOM_TXNS, FANTOM_INT, FANTOM_TOKENS, FANTOM_NFTS, WALLET, WORKSHEET_NAME

STAKE_ADDRESSES = [
    "0xFC00FACE00000000000000000000000000000000"
]

def merge_fantomscan(data_files):
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
          {TXNS: {'req': DataMerge.MAN, 'obj': FANTOM_TXNS},
           TOKENS: {'req': DataMerge.OPT, 'obj': FANTOM_TOKENS},
           NFTS: {'req': DataMerge.OPT, 'obj': FANTOM_NFTS},
           INTERNAL_TXNS: {'req': DataMerge.OPT, 'obj': FANTOM_INT}},
          merge_fantomscan)
