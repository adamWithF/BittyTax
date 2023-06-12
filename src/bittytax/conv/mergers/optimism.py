# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2023

import copy

from ...config import config
from .etherscan import _consolidate, _get_ins_outs, _method_handling, _do_fee_split, _do_etherscan_multi_sell, _do_etherscan_multi_buy, TXNS, TOKENS, NFTS, INTERNAL_TXNS
from ..datamerge import DataMerge, MergeDataRow
from ..out_record import TransactionOutRecord
from ..parsers.optimism import OPTIMISM_TXNS, OPTIMISM_DEPOSITS, OPTIMISM_WITHDRAWALS, OPTIMISM_INT, OPTIMISM_TOKENS, OPTIMISM_NFTS, WALLET, WORKSHEET_NAME

STAKE_ADDRESSES = []

DEPOSITS = "deposits"
WITHDRAWALS = "withdrawals"

def merge_optimism(data_files):
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

def _do_merge_etherscan(data_files, staking_addresses):  # pylint: disable=too-many-locals
    merge = False
    tx_ids = {}

    for file_id in data_files:
        for dr in data_files[file_id].data_rows:
            if not dr.t_record:
                continue

            wallet = dr.t_record.wallet[-abs(TransactionOutRecord.WALLET_ADDR_LEN) :]
            if wallet not in tx_ids:
                tx_ids[wallet] = {}

            txhash = dr.row_dict["Txhash"] if "Txhash" in dr.row_dict else None
            if txhash == None and "L2 Txhash" in dr.row:
                txhash = dr.row_dict["L2 Txhash"]

            if txhash not in tx_ids[wallet]:
                tx_ids[wallet][txhash] = []

            tx_ids[wallet][txhash].append(
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

            _consolidate(wallet_tx_ids[txn], [TXNS, INTERNAL_TXNS, DEPOSITS, WITHDRAWALS])

            t_ins, t_outs, t_fee = _get_ins_outs(wallet_tx_ids[txn])

            if config.debug:
                _output_records(t_ins, t_outs, t_fee)
                sys.stderr.write(f"{Fore.YELLOW}merge:     merge:\n")

            if t_fee:
                fee_quantity = t_fee.t_record.fee_quantity
                fee_asset = t_fee.t_record.fee_asset

            t_ins_orig = copy.copy(t_ins)
            if t_fee:
                _method_handling(t_ins, t_fee, staking_addresses)

            # Make trades
            if len(t_ins) == 1 and t_outs:
                _do_etherscan_multi_sell(t_ins, t_outs, t_fee)
            elif len(t_outs) == 1 and t_ins:
                _do_etherscan_multi_buy(t_ins, t_outs, t_fee)
            elif len(t_ins) > 1 and len(t_outs) > 1:
                # Multi-sell to multi-buy trade not supported
                sys.stderr.write(f"{WARNING} Merge failure for Txhash: {txn}\n")

                for mdr in wallet_tx_ids[txn]:
                    mdr.data_row.failure = UnexpectedContentError(
                        mdr.data_file.parser.in_header.index("Txhash") or mdr.data_file.parser.in_header.index("L2 Txhash"),
                        "Txhash",
                        mdr.data_row.row_dict["Txhash"] or mdr.data_row.row_dict["L2 Txhash"],
                    )
                    sys.stderr.write(
                        f"{Fore.YELLOW}"
                        f"row[{mdr.data_file.parser.in_header_row_num + mdr.data_row.line_num}] "
                        f"{mdr.data_row}\n"
                    )
                continue

            if t_fee:
                # Split fees
                t_all = [t for t in t_ins_orig + t_outs if t.t_record]
                _do_fee_split(t_all, t_fee, fee_quantity, fee_asset)

            merge = True

            if config.debug:
                _output_records(t_ins_orig, t_outs, t_fee)

    return merge


DataMerge("Optimistic etherscan fees & multi-token transactions",
          {TXNS: {'req': DataMerge.MANDATORY, 'obj': OPTIMISM_TXNS},
           TOKENS: {'req': DataMerge.OPTIONAL, 'obj': OPTIMISM_TOKENS},
           NFTS: {'req': DataMerge.OPTIONAL, 'obj': OPTIMISM_NFTS},
           INTERNAL_TXNS: {'req': DataMerge.OPTIONAL, 'obj': OPTIMISM_INT},
           DEPOSITS: {'req': DataMerge.OPTIONAL, 'obj': OPTIMISM_DEPOSITS},
           WITHDRAWALS: {'req': DataMerge.OPTIONAL, 'obj': OPTIMISM_WITHDRAWALS}},
          merge_optimism)