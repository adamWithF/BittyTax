# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2021

from ..datamerge import DataMerge
from ..out_record import TransactionOutRecord
from ..parsers.polygonscan import POLYGON_INT, POLYGON_TXNS, POLYGON_TOKENS, POLYGON_NFTS, WALLET, WORKSHEET_NAME
from .etherscan import _do_merge_etherscan

STAKE_ADDRESSES = []


def merge_polygonscan(data_files):
    # Do same merge as Etherscan
    merge = _do_merge_etherscan(data_files, STAKE_ADDRESSES)

    if merge:
        # Change Etherscan parsers to PolygonScan
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
    "PolygonScan fees & multi-token transactions",
    {
        TXNS: {"req": DataMerge.MANDATORY, "obj": POLYGON_TXNS},
        TOKENS: {"req": DataMerge.OPTIONAL, "obj": POLYGON_TOKENS},
        NFTS: {"req": DataMerge.OPTIONAL, "obj": POLYGON_NFTS},
        INTERNAL_TXNS: {"req": DataMerge.OPTIONAL, "obj": POLYGON_INT},
    },
    merge_polygonscan,
)