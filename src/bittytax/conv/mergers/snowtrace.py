# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2021

from ..datamerge import DataMerge
from ..out_record import TransactionOutRecord
from ..parsers.snowtrace import AVAX_INT, AVAX_TXNS, AVAX_TOKENS, AVAX_NFTS, WALLET, WORKSHEET_NAME
from .etherscan import INTERNAL_TXNS, NFTS, TOKENS, TXNS, _do_merge_etherscan

STAKE_ADDRESSES = []


def merge_snowtrace(data_files):
    # Do same merge as Etherscan
    merge = _do_merge_etherscan(data_files, STAKE_ADDRESSES)

    if merge:
        # Change Etherscan parsers to SnowTrace
        if TOKENS in data_files:
            data_files[TOKENS].parser.worksheet_name = WORKSHEET_NAME
            for data_row in data_files[TOKENS].data_rows:
                if data_row.t_record:
                    address = data_row.t_record.wallet[-abs(TransactionOutRecord.WALLET_ADDR_LEN) :]
                    data_row.t_record.wallet = f"{WALLET}-{address}"

        if NFTS in data_files:
            data_files[NFTS].parser.worksheet_name = WORKSHEET_NAME
            for data_row in data_files[NFTS].data_rows:
                if data_row.t_record:
                    address = data_row.t_record.wallet[-abs(TransactionOutRecord.WALLET_ADDR_LEN) :]
                    data_row.t_record.wallet = f"{WALLET}-{address}"

    return merge


DataMerge(
    "SnowTrace fees & multi-token transactions",
    {
        TXNS: {"req": DataMerge.MAN, "obj": AVAX_TXNS},
        TOKENS: {"req": DataMerge.OPT, "obj": AVAX_TOKENS},
        NFTS: {"req": DataMerge.OPT, "obj": AVAX_NFTS},
        INTERNAL_TXNS: {"req": DataMerge.OPT, "obj": AVAX_INT},
    },
    merge_snowtrace,
)
