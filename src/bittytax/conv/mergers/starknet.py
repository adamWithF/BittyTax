# -*- coding: utf-8 -*-
# (c)

# Left as an example

import copy
import sys
from decimal import Decimal
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from colorama import Fore

from ...bt_types import FileId, TrType
from ...config import config
from ...constants import WARNING
from ..datamerge import DataMerge, MergeDataRow, ParserRequired
from ..exceptions import UnexpectedContentError
from ..out_record import TransactionOutRecord
from ..mergers.etherscan import (
    _get_ins_outs,
    _consolidate,
    _output_records,
    _do_etherscan_multi_sell,
    _do_etherscan_multi_buy,
    _do_fee_split,
    _method_handling,

)
from ..parsers.starknet import (
    WALLET, WORKSHEET_NAME, STARKNET_TXNS
)

if TYPE_CHECKING:
    from ..datafile import DataFile
    from ..datarow import DataRow

from ..datamerge import DataMerge, ParserRequired
from ..out_record import TransactionOutRecord
from .etherscan import TOKENS, TXNS, NFTS

STAKE_ADDRESSES = []

INTERNAL_ADDRESSES_TO_SKIP = []


def merge_starknet(data_files):
    # Do same merge as Etherscan
    merge = _do_merge_starknet(data_files, STAKE_ADDRESSES)

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

def _do_merge_starknet(
    data_files: Dict[FileId, "DataFile"], staking_addresses: List[str]
) -> bool:  # pylint: disable=too-many-locals
    merge = False
    tx_ids: Dict[str, Dict[str, List[MergeDataRow]]] = {}

    for file_id in data_files:
        for dr in data_files[file_id].data_rows:
            if not dr.t_record:
                continue

            wallet = dr.t_record.wallet
            if wallet not in tx_ids:
                tx_ids[wallet] = {}

            if "tx_hash" in dr.row_dict:
                dr.row_dict["Transaction Hash"] = dr.row_dict["tx_hash"]
                dr.row_dict["Status"] = "Success"

            if dr.row_dict["Transaction Hash"] not in tx_ids[wallet]:
                tx_ids[wallet][dr.row_dict["Transaction Hash"]] = []

            tx_ids[wallet][dr.row_dict["Transaction Hash"]].append(
                MergeDataRow(dr, data_files[file_id], file_id)
            )

    for _, wallet_tx_ids in tx_ids.items():
        for txn in wallet_tx_ids:
            if len(wallet_tx_ids[txn]) == 1:
                if config.debug:
                    sys.stderr.write(
                        f"{Fore.GREEN}merge: {wallet_tx_ids[txn][0].data_file_id:<5}:"
                        f"{wallet_tx_ids[txn][0].data_row}\n"
                    )
                continue

            for t in wallet_tx_ids[txn]:
                if config.debug:
                    sys.stderr.write(f"{Fore.GREEN}merge: {t.data_file_id:<5}:{t.data_row}\n")

            t_ins, t_outs, t_fee = _get_ins_outs(wallet_tx_ids[txn])

            if config.debug:
                _output_records(t_ins, t_outs, t_fee)
                sys.stderr.write(f"{Fore.YELLOW}merge:     consolidate:\n")

            # _consolidate(wallet_tx_ids[txn], [TXNS, INTERNAL_TXNS])

            t_ins, t_outs, t_fee = _get_ins_outs(wallet_tx_ids[txn])

            if config.debug:
                _output_records(t_ins, t_outs, t_fee)
                sys.stderr.write(f"{Fore.YELLOW}merge:     merge:\n")

            if t_fee:
                if not t_fee.t_record:
                    raise RuntimeError("Missing t_record")

                fee_quantity = t_fee.t_record.fee_quantity
                fee_asset = t_fee.t_record.fee_asset

            t_ins_orig = copy.copy(t_ins)
            if t_fee:
                _method_handling(t_ins, t_fee, staking_addresses)

            # t_outs = [tos for tos in t_outs if not bool(set(INTERNAL_ADDRESSES_TO_SKIP) & set(tos.row))]

            # if len(t_outs) == 2:
            #     count1 = sum(1 for value in t_outs[0].row_dict.values() if value != "" and value != 0)
            #     count2 = sum(1 for value in t_outs[1].row_dict.values() if value != "" and value != 0)
            #     if (count1 > count2):
            #         t_outs = [t_outs[0]]
            #     else:
            #         t_outs = [t_outs[1]]

            # Make trades
            if len(t_ins) == 1 and t_outs:
                _do_etherscan_multi_sell(t_ins, t_outs, t_fee)
            elif len(t_outs) == 1 and t_ins:
                _do_etherscan_multi_buy(t_ins, t_outs, t_fee)
            elif len(t_ins) > 1 and len(t_outs) > 1:
                # Multi-sell to multi-buy trade not supported
                sys.stderr.write(f"{WARNING} Merge failure for Transaction Hash: {txn}\n")

                for mdr in wallet_tx_ids[txn]:
                    if "tx_hash" in mdr.data_row.row_dict:
                        mdr.data_row.failure = UnexpectedContentError(
                            mdr.data_file.parser.in_header.index("tx_hash"),
                            "tx_hash",
                            mdr.data_row.row_dict["tx_hash"],
                        )
                    else:
                        mdr.data_row.failure = UnexpectedContentError(
                            mdr.data_file.parser.in_header.index("Transaction Hash"),
                            "Transaction Hash",
                            mdr.data_row.row_dict["Transaction Hash"],
                        )

                    if mdr.data_file.parser.in_header_row_num is None:
                        raise RuntimeError("Missing in_header_row_num")

                    sys.stderr.write(
                        f"{Fore.YELLOW}"
                        f"row[{mdr.data_file.parser.in_header_row_num + mdr.data_row.line_num}]"
                        f" {mdr.data_row}\n"
                    )
                continue

            if t_fee:
                if fee_quantity is None:
                    raise RuntimeError("Missing fee_quantity")

                # Split fees
                t_all = [t for t in t_ins_orig + t_outs if t.t_record]
                _do_fee_split(t_all, t_fee, fee_quantity, fee_asset)

            merge = True

            if config.debug:
                _output_records(t_ins_orig, t_outs, t_fee)

    return merge




DataMerge("StarkNet fees & multi-token transactions",
          {TXNS: {'req': ParserRequired.MANDATORY, 'obj': STARKNET_TXNS}},
          merge_starknet)