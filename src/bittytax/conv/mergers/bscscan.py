# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2021

from ..datamerge import DataMerge
from ..out_record import TransactionOutRecord
from ..parsers.bscscan import BSC_INT, BSC_TXNS, BSC_NFTS, BSC_TOKENS, WALLET, WORKSHEET_NAME
from .etherscan import _do_merge_etherscan

STAKE_ADDRESSES = [
    "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82", # CAKE
    "0x603c7f932ED1fc6575303D8Fb018fDCBb0f39a95", # APE BANANA
    "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c", # WBNB
    "0xC9849E6fdB743d08fAeE3E34dd2D1bc69EA11a51", # BUNNY
    "0x3Fcca8648651E5b974DD6d3e50F61567779772A8", # POTS
    "0xd9025e25bb6cf39f8c926a704039d2dd51088063", # CYT
    "0x8f0528ce5ef7b51152a59745befdd91d97091d2f", # ALPACA
    "0xfa363022816abf82f18a9c2809dcd2bb393f6ac5", # HONEY
    "0x14016e85a25aeb13065688cafb43044c2ef86784", # TUSDT
    "0xe9e7cea3dedca5984780bafc599bd69add087d56", # BUSD
    "0x55d398326f99059ff775485246999027b3197955", # USDT
    "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d", # USDC
]

def merge_bscscan(data_files):
    # Do same merge as Etherscan
    merge = _do_merge_etherscan(data_files, STAKE_ADDRESSES)

    if merge:
        # Change Etherscan parsers to BscScan
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
    "BscScan fees & multi-token transactions",
    {
        TXNS: {"req": DataMerge.MANDATORY, "obj": BSC_TXNS},
        TOKENS: {"req": DataMerge.OPTIONAL, "obj": BSC_TOKENS},
        NFTS: {"req": DataMerge.OPTIONAL, "obj": BSC_NFTS},
        INTERNAL_TXNS: {"req": DataMerge.OPTIONAL, "obj": BSC_INT},
    },
    merge_bscscan,
)