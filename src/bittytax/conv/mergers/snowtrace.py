# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2021

from typing import TYPE_CHECKING, Dict, List
from ...bt_types import FileId
from ..datamerge import DataMerge, ParserRequired
from ..out_record import TransactionOutRecord
from ..parsers.snowtrace import avax_int, avax_txns, avax_tokens, avax_nfts

from .etherscan import _do_merge_etherscan
from .etherscan import TOKENS, TXNS, NFTS, INTERNAL_TXNS

STAKE_ADDRESSES: List[str] = []

if TYPE_CHECKING:
    from ..datafile import DataFile


def merge_snowtrace(data_files: Dict[FileId, "DataFile"]) -> bool:
    # Do same merge as Etherscan
    return _do_merge_etherscan(data_files, STAKE_ADDRESSES)


DataMerge(
    "Snowtrace fees & multi-token transactions",
    {
        TXNS: {"req": ParserRequired.MANDATORY, "obj": avax_txns},
        TOKENS: {"req": ParserRequired.MANDATORY, "obj": avax_tokens},
        NFTS: {"req": ParserRequired.OPTIONAL, "obj": avax_nfts},
        INTERNAL_TXNS: {"req": ParserRequired.OPTIONAL, "obj": avax_int},
    },
    merge_snowtrace,
)