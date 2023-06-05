# -*- coding: utf-8 -*-
# (c)

from decimal import Decimal

from .etherscan import get_note
from ..out_record import TransactionOutRecord
from ..dataparser import DataParser

WALLET = "Optimism"
WORKSHEET_NAME = "OptimismScan"

def parse_optimismscan(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict['UnixTimestamp']))

    if row_dict['Status'] != '':
        # Failed txns should not have a Value_OUT
        row_dict['Value_OUT(ETH)'] = 0

    if Decimal(row_dict['Value_IN(ETH)']) > 0:
        if row_dict['Status'] == '':
            data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_DEPOSIT,
                                                     data_row.timestamp,
                                                     buy_quantity=row_dict['Value_IN(ETH)'],
                                                     buy_asset="ETH",
                                                     wallet=get_wallet(row_dict['To']),
                                                     note=get_note(row_dict))
    elif Decimal(row_dict['Value_OUT(ETH)']) > 0:
        data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_WITHDRAWAL,
                                                 data_row.timestamp,
                                                 sell_quantity=row_dict['Value_OUT(ETH)'],
                                                 sell_asset="ETH",
                                                 fee_quantity=row_dict['TxnFee(ETH)'],
                                                 fee_asset="ETH",
                                                 wallet=get_wallet(row_dict['From']),
                                                 note=get_note(row_dict))
    else:
        data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_SPEND,
                                                 data_row.timestamp,
                                                 sell_quantity=row_dict['Value_OUT(ETH)'],
                                                 sell_asset="ETH",
                                                 fee_quantity=row_dict['TxnFee(ETH)'],
                                                 fee_asset="ETH",
                                                 wallet=get_wallet(row_dict['From']),
                                                 note=get_note(row_dict))

def get_wallet(address):
    return "%s-%s" % (WALLET, address.lower()[0:TransactionOutRecord.WALLET_ADDR_LEN])

def parse_optimismscan_internal(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["UnixTimestamp"]))

    # Failed internal transaction
    if row_dict["Status"] != "0":
        return

    if Decimal(row_dict["Value_IN(ETH)"]) > 0:
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_DEPOSIT,
            data_row.timestamp,
            buy_quantity=row_dict["Value_IN(ETH)"],
            buy_asset="ETH",
            wallet=_get_wallet(row_dict["TxTo"]),
        )
    elif Decimal(row_dict["Value_OUT(ETH)"]) > 0:
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=row_dict["Value_OUT(ETH)"],
            sell_asset="ETH",
            wallet=_get_wallet(row_dict["From"]),
        )


def parse_optimismscan_tokens(data_row, _parser, **kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["UnixTimestamp"]))

    if row_dict["TokenSymbol OP"].endswith("-LP"):
        asset = row_dict["TokenSymbol OP"] + "-" + row_dict["ContractAddress"][0:10]
    else:
        asset = row_dict["TokenSymbol OP"]

    if "Value" in row_dict:
        quantity = row_dict["Value"].replace(",", "")
    else:
        quantity = row_dict["TokenValue"].replace(",", "")

    if row_dict["To"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_DEPOSIT,
            data_row.timestamp,
            buy_quantity=quantity,
            buy_asset=asset,
            wallet=_get_wallet(row_dict["To"]),
        )
    elif row_dict["From"].lower() in kwargs["filename"].lower():
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=quantity,
            sell_asset=asset,
            wallet=_get_wallet(row_dict["From"]),
        )
    else:
        raise DataFilenameError(kwargs["filename"], "Ethereum address")




optimismscan_txns = DataParser(
        DataParser.TYPE_EXPLORER,
        "OptimismScan (Optimism Transactions)",
    ["Txhash","Blockno","UnixTimestamp","DateTime","From","To","ContractAddress","Value_IN(ETH)","Value_OUT(ETH)",None,"TxnFee(ETH)","TxnFee(USD)","Historical $Price/ETH","Status","ErrCode","Method OP"],
        worksheet_name=WORKSHEET_NAME,
        row_handler=parse_optimismscan)



optimismscan_tokens = DataParser(DataParser.TYPE_EXPLORER,
           "OptimismScan (Optimism Tokens)",
           ["Txhash","Blockno","UnixTimestamp","DateTime","From","To","TokenValue","USDValueDayOfTx","ContractAddress","TokenName","TokenSymbol OP"],
           worksheet_name=WORKSHEET_NAME,
           row_handler=parse_optimismscan_tokens)


# DataParser(DataParser.TYPE_EXPLORER,
#            "ArbiScan (Arbitrum Transactions)",
#            ['Txhash', 'Blockno', 'UnixTimestamp', 'DateTime', 'From', 'To', 'ContractAddress',
#             'Value_IN(ETH)', 'Value_OUT(ETH)', None, 'TxnFee(ETH)', 'TxnFee(USD)',
#             'Historical $Price/ETH', 'Status', 'ErrCode', 'PrivateNote'],
#            worksheet_name=WORKSHEET_NAME,
#            row_handler=parse_optimismscan)

# DataParser(DataParser.TYPE_EXPLORER,
#            "ArbiScan (Arbitrum Transactions)",
#            ['Txhash', 'Blockno', 'UnixTimestamp', 'DateTime', 'From', 'To', 'ContractAddress',
#             'Value_IN(ETH)', 'Value_OUT(ETH)', None, 'TxnFee(ETH)', 'TxnFee(USD)',
#             'Historical $Price/ETH', 'Status', 'ErrCode', 'Method'],
#            worksheet_name=WORKSHEET_NAME,
#            row_handler=parse_optimismscan)

# DataParser(DataParser.TYPE_EXPLORER,
#            "ArbiScan (Arbitrum Transactions)",
#            ['Txhash', 'Blockno', 'UnixTimestamp', 'DateTime', 'From', 'To', 'ContractAddress',
#             'Value_IN(ETH)', 'Value_OUT(ETH)', None, 'TxnFee(ETH)', 'TxnFee(USD)',
#             'Historical $Price/ETH', 'Status', 'ErrCode', 'Method', 'PrivateNote'],
#            worksheet_name=WORKSHEET_NAME,
#            row_handler=parse_optimismscan)

optimismscan_int = DataParser(
        DataParser.TYPE_EXPLORER,
        "OptimismScan (Optimism Internal Transactions)",
        ['Txhash', 'Blockno', 'UnixTimestamp', 'DateTime', 'ParentTxFrom', 'ParentTxTo',
         'ParentTxETH_Value', 'From', 'TxTo', 'ContractAddress', 'Value_IN(ETH)',
         'Value_OUT(ETH)', None, 'Historical $Price/ETH', 'Status', 'ErrCode', 'Type OP'],
        worksheet_name=WORKSHEET_NAME,
        row_handler=parse_optimismscan_internal)

# DataParser(DataParser.TYPE_EXPLORER,
#            "ArbiScan (Arbitrum Internal Transactions)",
#            ['Txhash', 'Blockno', 'UnixTimestamp', 'DateTime', 'ParentTxFrom', 'ParentTxTo',
#             'ParentTxETH_Value', 'From', 'TxTo', 'ContractAddress', 'Value_IN(ETH)',
#             'Value_OUT(ETH)', None, 'Historical $Price/ETH', 'Status', 'ErrCode', 'Type',
#             'PrivateNote'],
#            worksheet_name=WORKSHEET_NAME,
#            row_handler=parse_optimismscan_internal)

# Same header as Etherscan
#DataParser(DataParser.TYPE_EXPLORER,
#           "BscScan (BEP-20 Tokens)",
#           ['Txhash', 'UnixTimestamp', 'DateTime', 'From', 'To', 'Value', 'ContractAddress',
#            'TokenName', 'TokenSymbol'],
#           worksheet_name=WORKSHEET_NAME,
#           row_handler=parse_bscscan_tokens)

# Same header as Etherscan
#DataParser(DataParser.TYPE_EXPLORER,
#           "Etherscan (BEP-721 NFTs)",
#           ['Txhash', 'UnixTimestamp', 'DateTime', 'From', 'To', 'ContractAddress', 'TokenId',
#            'TokenName', 'TokenSymbol'],
#           worksheet_name=WORKSHEET_NAME,
#           row_handler=parse_bscscan_nfts)
