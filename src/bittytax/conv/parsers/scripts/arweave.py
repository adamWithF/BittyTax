# -*- coding: utf-8 -*-
# (c)

# Support for Arweave via viewblock.io

from ..out_record import TransactionOutRecord
from ..dataparser import DataParser

WALLET = "Arweave"
WORKSHEET_NAME = "Arweave"

def parse_arweave(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict['time'])

    if row_dict['success'] != 'yes':
        # Failed txns should not have a Value_OUT
        return

    if get_wallet_address(_kwargs['filename']) == row_dict['to']:
        data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_DEPOSIT,
                                                 data_row.timestamp,
                                                 buy_quantity=abs(float(row_dict['value'].split(' ')[0].replace(',', ''))),
                                                 buy_asset=row_dict['value'].split(' ')[1],
                                                 fee_quantity=row_dict['fee'].split(' ')[0],
                                                 fee_asset=row_dict['fee'].split(' ')[1],
                                                 wallet=get_wallet(row_dict['to']))

    else:
        data_row.t_record = TransactionOutRecord(TransactionOutRecord.TYPE_WITHDRAWAL,
                                                 data_row.timestamp,
                                                 sell_quantity=abs(float(row_dict['value'].split(' ')[0].replace(',', ''))),
                                                 sell_asset=row_dict['value'].split(' ')[1],
                                                 fee_quantity=row_dict['fee'].split(' ')[0],
                                                 fee_asset=row_dict['fee'].split(' ')[1],
                                                 wallet=get_wallet(row_dict['from']))


def get_wallet(address):
    return "%s-%s" % (WALLET, address.lower()[0:TransactionOutRecord.WALLET_ADDR_LEN])

def get_wallet_address(filename):
    return filename.split('-')[0]


arweave_txns = DataParser(
    DataParser.TYPE_EXPLORER,
    "Near",
    ['hash','timestamp','time','height','from','direction','to','value','token','fee','method','success','error'],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_arweave)
