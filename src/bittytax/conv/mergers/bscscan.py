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
    "0x14016e85a25aeb13065688cafb43044c2ef86784", # TUSD
    "0xe9e7cea3dedca5984780bafc599bd69add087d56", # BUSD
    "0x55d398326f99059ff775485246999027b3197955", # USDT
    "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d", # USDC
    "0x86Ef5e73EDB2Fea111909Fe35aFcC564572AcC06", # BananaSplitBar
    "0xD307e7CC6a302046b7D91D83aa4B8324cFB7a786", # Moo Ape BANANA
    "0x9273be9c180B0271cc2c90E5BF99477B573Fe904", # Moon Ticket CakeV2
    "0xF90BAA331Cfd40F094476E752Bf272892170d399", # Pancake LPs
    "0x3106d9B3d5e04ff5D575212140FAb1Cf17C8933F", # Moo CakeV2 POTS-BUSD
    "0xa178972A8FfeFd6661179666134A2ba9B3DbE3B1", # Moon Ticket POTS
    "0x2961aa26a1Cb3068E580099045cc79a5b7B9634c", # Pancake LPs
    "0x1F40e7Cb04Ec64Ef82568E49Db60858188641Bb1", # Moo HoneyFarm HONEY-BUSD
    "0xc3EAE9b061Aa0e1B9BD3436080Dc57D2d63FEdc1", # Bear
    "0x04C549551F536ceB015e79F2B242024800eeC206", # Moo HoneyFarm BEAR-BUSD
    "0x87f697905732c6FAa5Def3bfE23AaDA5eAC33Ee8", # Moon Ticket Banana
    "0x009cF7bC57584b7998236eff51b98A168DceA9B0", # SyrupBar Token
    "0x97e5d50Fe0632A95b9cf1853E744E02f7D816677", # Moo CakeV2
    "0xd7D069493685A581d27824Fc46EdA46B7EfC0063", # Interest Bearing BNB
    "0x7C9e73d4C71dae564d41F78d56439bB4ba87592f", # Interest Bearing BUSD
    "0x2170Ed0880ac9A755fd29B2688956BD959F933F8", # Binance-Peg Ethereum Token
    "0xbfF4a34A4644a113E8200D7F1D79b3555f723AfE", # Interest Bearing ETH


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