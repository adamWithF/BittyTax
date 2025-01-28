# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2023

import os
import re
from decimal import Decimal
from typing import TYPE_CHECKING

from typing_extensions import Unpack

from ...bt_types import TrType
from ..dataparser import DataParser, ParserArgs, ParserType
from ..datarow import TxRawPos
from ..exceptions import DataFilenameError, UnknownCryptoassetError
from ..out_record import TransactionOutRecord
from typing import Dict

if TYPE_CHECKING:
    from ..datarow import DataRow

NETWORK_TO_TOKEN = {
    "Polkadot": "DOT",
    "Kusama": "KSM",
}


def parse_subscan_crosschain_transfers(
    data_row: "DataRow", parser: DataParser, **kwargs: Unpack[ParserArgs]
) -> None:
    row_dict = data_row.row_dict

    data_row.timestamp = DataParser.parse_timestamp(row_dict["Time"])

    data_row.tx_raw = TxRawPos(
        parser.in_header.index("Message Hash"),
        parser.in_header.index("From Account"),
        parser.in_header.index("To Account"),
    )

    if row_dict["Status"].lower() != "success":
        return

    network = _get_network(kwargs["filename"])

    if row_dict["To Account"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TrType.DEPOSIT,
            data_row.timestamp,
            buy_quantity=Decimal(row_dict["Value"].split(' ')[0]),
            buy_asset=row_dict["Value"].split(' ')[1],
            wallet=_get_wallet(network, row_dict["To Account"]),
            note=_get_note(row_dict)
        )
    elif row_dict["From Account"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TrType.WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=Decimal(row_dict["Value"].split(' ')[0]),
            sell_asset=row_dict["Value"].split(' ')[1],
            wallet=_get_wallet(network, row_dict["From Account"]),
            note=_get_note(row_dict)
        )
    else:
        print("address", network)
        raise DataFilenameError(kwargs["filename"], f"{network} address")



def parse_subscan_transfers(
    data_row: "DataRow", parser: DataParser, **kwargs: Unpack[ParserArgs]
) -> None:
    row_dict = data_row.row_dict

    if "Date" in row_dict:
        data_row.timestamp = DataParser.parse_timestamp(row_dict["Date"])
    else:
        data_row.timestamp = DataParser.parse_timestamp(
            re.sub(r" \(\+?UTC\)", "", row_dict["Block Timestamp"])
        )

    data_row.tx_raw = TxRawPos(
        parser.in_header.index("Hash"),
        parser.in_header.index("From"),
        parser.in_header.index("To"),
    )

    if row_dict["Result"].lower() != "true":
        return

    network = _get_network(kwargs["filename"])

    if row_dict["To"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TrType.DEPOSIT,
            data_row.timestamp,
            buy_quantity=Decimal(row_dict["Value"]),
            buy_asset=row_dict["Symbol"],
            wallet=_get_wallet(network, row_dict["To"]),
            note=_get_note(row_dict)
        )
    elif row_dict["From"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TrType.WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=Decimal(row_dict["Value"]),
            sell_asset=row_dict["Symbol"],
            wallet=_get_wallet(network, row_dict["From"]),
            note=_get_note(row_dict)
        )
    else:
        raise DataFilenameError(kwargs["filename"], f"{network} address")

def _get_note(row_dict: Dict[str, str]) -> str:
    return str(row_dict)

def _get_network(filename: str) -> str:
    for network in NETWORK_TO_TOKEN:
        if os.path.basename(filename).startswith(network):
            return network
    raise DataFilenameError(filename, "Network name")


def _get_wallet(network: str, address: str) -> str:
    return f"{network}-{address.lower()[0 : TransactionOutRecord.WALLET_ADDR_LEN]}"


def parse_subscan_paidout_v2(
    data_row: "DataRow", _parser: DataParser, **kwargs: Unpack[ParserArgs]
) -> None:
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(re.sub(r" \(\+?UTC\)", "", row_dict["Date"]))
    network = _get_network(kwargs["filename"])
    token = _get_token(network, **kwargs)

    data_row.t_record = TransactionOutRecord(
        TrType.STAKING,
        data_row.timestamp,
        buy_quantity=Decimal(row_dict["Value"]),
        buy_asset=token,
        wallet=_get_wallet(network, row_dict["Reward Account"]),
        note=_get_note(row_dict)
    )

def parse_subscan_paidout(
    data_row: "DataRow", _parser: DataParser, **kwargs: Unpack[ParserArgs]
) -> None:
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(re.sub(r" \(\+?UTC\)", "", row_dict["Time"]))
    network = _get_network(kwargs["filename"])
    token = _get_token(network, **kwargs)

    data_row.t_record = TransactionOutRecord(
        TrType.STAKING,
        data_row.timestamp,
        buy_quantity=Decimal(row_dict["Value"]),
        buy_asset=token,
        wallet=_get_wallet(network, row_dict["Pool"]),
        note=_get_note(row_dict)
    )


def _get_token(network: str, **kwargs: Unpack[ParserArgs]) -> str:
    if network in NETWORK_TO_TOKEN:
        return NETWORK_TO_TOKEN[network]

    if kwargs["cryptoasset"]:
        return kwargs["cryptoasset"]
    raise UnknownCryptoassetError(kwargs["filename"], kwargs.get("worksheet", ""))

DataParser(
    ParserType.EXPLORER,
    "Subscan Crosschain Transfers",
    [
        "Message Hash",
        "From Account",
        "To Account",
        "Block",
        "Origin Event Index",
        "Dest Event Index",
        "Time",
        "From Chain ID",
        "Destination Chain ID",
        "Value",
        "Protocol",
        "Status"
    ],
    worksheet_name="Subscan",
    row_handler=parse_subscan_crosschain_transfers,
)



DataParser(
    ParserType.EXPLORER,
    "Subscan Transfers",
    ["Extrinsic ID", "Block", "Block Timestamp", "From", "To", "Value", "Symbol", "Result", "Hash"],
    worksheet_name="Subscan",
    row_handler=parse_subscan_transfers,
)

DataParser(
    ParserType.EXPLORER,
    "Subscan Transfers",
    ["Extrinsic ID", "Date", "Block", "Hash", "Symbol", "From", "To", "Value", "Result"],
    worksheet_name="Subscan",
    row_handler=parse_subscan_transfers,
)

DataParser(
    ParserType.EXPLORER,
    "Subscan Pool Paidout",
    ["Event Index","Era","Date","Block","Extrinsic Index","Value","Action","Stash","Reward Account","Validator Stash"],
    worksheet_name="Subscan",
    row_handler=parse_subscan_paidout_v2,
)

DataParser(
    ParserType.EXPLORER,
    "Subscan Pool Paidout",
    ["Event ID", "Block", "Extrinsic ID", "Pool", "Pool", "Value", "Action", "Time"],
    worksheet_name="Subscan",
    row_handler=parse_subscan_paidout,
)

# The legacy format only contains the Pool, not the Address.
DataParser(
    ParserType.EXPLORER,
    "Subscan Pool Paidout",
    ["Event ID", "Extrinsic ID", "Pool", "Value", "Action", "Time"],
    worksheet_name="Subscan",
    row_handler=parse_subscan_paidout,
)