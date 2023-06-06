# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2020

from decimal import Decimal
from ..dataparser import DataParser
from ..exceptions import UnexpectedTypeError
from ..out_record import TransactionOutRecord

WALLET = "KuCoin"


def parse_kucoin_trades_v4(data_row, parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict["createdDate"], tz="Asia/Hong_Kong")

    if row_dict["direction"].lower() == "buy":
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_TRADE,
            data_row.timestamp,
            buy_quantity=row_dict["amount"],
            buy_asset=row_dict["symbol"].split("-")[0],
            sell_quantity=row_dict["dealValue"],
            sell_asset=row_dict["symbol"].split("-")[1],
            fee_quantity=row_dict["fee"],
            fee_asset=row_dict["symbol"].split("-")[1],
            wallet=WALLET,
        )
    elif row_dict["direction"].lower() == "sell":
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_TRADE,
            data_row.timestamp,
            buy_quantity=row_dict["dealValue"],
            buy_asset=row_dict["symbol"].split("-")[1],
            sell_quantity=row_dict["amount"],
            sell_asset=row_dict["symbol"].split("-")[0],
            fee_quantity=row_dict["fee"],
            fee_asset=row_dict["symbol"].split("-")[1],
            wallet=WALLET,
        )
    else:
        raise UnexpectedTypeError(
            parser.in_header.index("direction"), "direction", row_dict["direction"]
        )


def parse_kucoin_trades_v3(data_row, parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict["tradeCreatedAt"], tz="Asia/Hong_Kong")

    if row_dict["side"] == "buy":
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_TRADE,
            data_row.timestamp,
            buy_quantity=row_dict["size"],
            buy_asset=row_dict["symbol"].split("-")[0],
            sell_quantity=row_dict["funds"],
            sell_asset=row_dict["symbol"].split("-")[1],
            fee_quantity=row_dict["fee"],
            fee_asset=row_dict["feeCurrency"],
            wallet=WALLET,
        )
    elif row_dict["side"] == "sell":
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_TRADE,
            data_row.timestamp,
            buy_quantity=row_dict["funds"],
            buy_asset=row_dict["symbol"].split("-")[1],
            sell_quantity=row_dict["size"],
            sell_asset=row_dict["symbol"].split("-")[0],
            fee_quantity=row_dict["fee"],
            fee_asset=row_dict["feeCurrency"],
            wallet=WALLET,
        )
    else:
        raise UnexpectedTypeError(parser.in_header.index("side"), "side", row_dict["side"])


def parse_kucoin_trades_v2(data_row, parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict["created_at"], tz="Asia/Hong_Kong")

    if row_dict["direction"].lower() == "buy":
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_TRADE,
            data_row.timestamp,
            buy_quantity=row_dict["amount_coin"],
            buy_asset=row_dict["symbol"].split("-")[0],
            sell_quantity=row_dict["funds"],
            sell_asset=row_dict["symbol"].split("-")[1],
            fee_quantity=row_dict["fee"],
            fee_asset=row_dict["symbol"].split("-")[1],
            wallet=WALLET,
        )
    elif row_dict["direction"].lower() == "sell":
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_TRADE,
            data_row.timestamp,
            buy_quantity=row_dict["funds"],
            buy_asset=row_dict["symbol"].split("-")[1],
            sell_quantity=row_dict["amount_coin"],
            sell_asset=row_dict["symbol"].split("-")[0],
            fee_quantity=row_dict["fee"],
            fee_asset=row_dict["symbol"].split("-")[1],
            wallet=WALLET,
        )
    else:
        raise UnexpectedTypeError(
            parser.in_header.index("direction"), "direction", row_dict["direction"]
        )


def parse_kucoin_trades_v1(data_row, parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict["created_at"], tz="Asia/Hong_Kong")

    if row_dict["direction"].lower() == "buy":
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_TRADE,
            data_row.timestamp,
            buy_quantity=row_dict["amount"],
            buy_asset=row_dict["symbol"].split("-")[0],
            sell_quantity=row_dict["deal_value"],
            sell_asset=row_dict["symbol"].split("-")[1],
            wallet=WALLET,
        )
    elif row_dict["direction"].lower() == "sell":
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_TRADE,
            data_row.timestamp,
            buy_quantity=row_dict["deal_value"],
            buy_asset=row_dict["symbol"].split("-")[1],
            sell_quantity=row_dict["amount"],
            sell_asset=row_dict["symbol"].split("-")[0],
            wallet=WALLET,
        )
    else:
        raise UnexpectedTypeError(
            parser.in_header.index("direction"), "direction", row_dict["direction"]
        )


def parse_kucoin_deposits_withdrawals(data_row, parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict["created_at"], tz="Asia/Hong_Kong")

    if row_dict["type"] == "DEPOSIT":
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_DEPOSIT,
            data_row.timestamp,
            buy_quantity=row_dict["vol"],
            buy_asset=row_dict["coin_type"],
            wallet=WALLET,
        )
    elif row_dict["type"] == "WITHDRAW":
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=row_dict["vol"],
            sell_asset=row_dict["coin_type"],
            wallet=WALLET,
        )
    else:
        raise UnexpectedTypeError(parser.in_header.index("type"), "type", row_dict["type"])


def parse_kucoin_bundle_deposits_withdrawals(data_row, parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict["Time(UTC+08:00)"], tz="Asia/Singapore")

    if "Withdrawal Address/Account" in row_dict:
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=row_dict["Amount"],
            sell_asset=row_dict["Coin"],
            fee_value=row_dict["Fee"],
            wallet=row_dict["Withdrawal Address/Account"],
        )
    else:
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_DEPOSIT,
            data_row.timestamp,
            buy_quantity=row_dict["Amount"],
            buy_asset=row_dict["Coin"],
            fee_value=row_dict["Fee"],
            wallet=WALLET,
        )


def parse_kucoin_bundle_earn_orders_profit(data_row, parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict["Time(UTC+08:00)"], tz="Asia/Singapore")

    data_row.t_record = TransactionOutRecord(
        TransactionOutRecord.TYPE_GIFT_RECEIVED,
        data_row.timestamp,
        buy_quantity=row_dict["Amount"],
        buy_asset=row_dict["Earnings Coin"],
        fee_value=row_dict["Fee"],
        wallet=row_dict["Withdrawal Address/Account"],
    )


def parse_kucoin_bundle_earn_orders_stacking(data_row, parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict["Staked Time(UTC+08:00)"], tz="Asia/Singapore")

    data_row.t_record = TransactionOutRecord(
        TransactionOutRecord.TYPE_STAKING,
        data_row.timestamp,
        buy_quantity=row_dict["Amount"],
        buy_asset=row_dict["Staked Coin"],
        wallet=row_dict["Withdrawal Address/Account"],
    )


def parse_kucoin_bundle_futures_pnl(data_row, parser, **_kwargs):
    row_dict = data_row.row_dict
    position_closing_time = DataParser.parse_timestamp(row_dict["Position Closing Time(UTC+08:00)"], tz="Asia/Singapore")
    position_opening_time = DataParser.parse_timestamp(row_dict["Position Opening Time(UTC+08:00)"], tz="Asia/Singapore")
    data_row.timestamp = position_closing_time

    if data_row.timestamp:
        pnl = Decimal(row_dict["Total Realized PNL"])
        was_profitable = pnl >= 0
        pnl = abs(pnl)
        data_row.t_record = TransactionOutRecord(
            TransactionOutRecord.TYPE_TRADE,
            timestamp=position_closing_time,
            buy_quantity=pnl if was_profitable else 0,
            buy_asset="USDT",
            sell_quantity=0 if was_profitable else pnl,
            sell_asset="USDT",
            fee_value=Decimal(row_dict["Total Funding Fees"]) + Decimal(row_dict["Total Trading Fees"]),
            wallet=f"{WALLET} Futures",
            note=position_closing_time,
        )


def parse_kucoin_deposits(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict["Time"], tz="Asia/Singapore")

    data_row.t_record = TransactionOutRecord(
        TransactionOutRecord.TYPE_DEPOSIT,
        data_row.timestamp,
        buy_quantity=row_dict["Amount"],
        buy_asset=row_dict["Coin"],
        wallet=WALLET,
    )


def parse_kucoin_withdrawals(data_row, _parser, **_kwargs):
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(row_dict["Time"], tz="Asia/Singapore")

    data_row.t_record = TransactionOutRecord(
        TransactionOutRecord.TYPE_WITHDRAWAL,
        data_row.timestamp,
        sell_quantity=row_dict["Amount"],
        sell_asset=row_dict["Coin"],
        wallet=WALLET,
    )


DataParser(
    DataParser.TYPE_EXCHANGE,
    "KuCoin Trades",
    [
        "oid",
        "symbol",
        "dealPrice",
        "dealValue",
        "amount",
        "fee",
        "direction",
        "createdDate",
        "",
    ],
    worksheet_name="KuCoin T",
    row_handler=parse_kucoin_trades_v4,
)

DataParser(
    DataParser.TYPE_EXCHANGE,
    "KuCoin Trades",
    [
        "tradeCreatedAt",
        "orderId",
        "symbol",
        "side",
        "price",
        "size",
        "funds",
        "fee",
        "liquidity",
        "feeCurrency",
        "orderType",
        "",
    ],
    worksheet_name="KuCoin T",
    row_handler=parse_kucoin_trades_v3,
)

DataParser(
    DataParser.TYPE_EXCHANGE,
    "KuCoin Trades",
    [
        "tradeCreatedAt",
        "orderId",
        "symbol",
        "side",
        "price",
        "size",
        "funds",
        "fee",
        "liquidity",
        "feeCurrency",
        "orderType",
    ],
    worksheet_name="KuCoin T",
    row_handler=parse_kucoin_trades_v3,
)

DataParser(
    DataParser.TYPE_EXCHANGE,
    "KuCoin Trades",
    [
        "uid",
        "symbol",
        "order_type",
        "price",
        "amount_coin",
        "direction",
        "funds",
        "fee",
        "created_at",
    ],
    worksheet_name="KuCoin T",
    row_handler=parse_kucoin_trades_v2,
)

DataParser(
    DataParser.TYPE_EXCHANGE,
    "KuCoin Trades",
    ["uid", "symbol", "direction", "deal_price", "amount", "deal_value", "created_at"],
    worksheet_name="KuCoin T",
    row_handler=parse_kucoin_trades_v1,
)

DataParser(
    DataParser.TYPE_EXCHANGE,
    "KuCoin Deposits",
    ["Time", "Coin", "Amount", "Type", "Remark"],
    worksheet_name="KuCoin D",
    row_handler=parse_kucoin_deposits,
)

DataParser(
    DataParser.TYPE_EXCHANGE,
    "KuCoin Withdrawals",
    ["Time", "Coin", "Amount", "Type", "Wallet Address", "Remark"],
    worksheet_name="KuCoin W",
    row_handler=parse_kucoin_withdrawals,
)

DataParser(
    DataParser.TYPE_EXCHANGE,
    "KuCoin Deposits/Withdrawals",
    ["coin_type", "type", "add", "hash", "vol", "created_at"],
    worksheet_name="Kucoin D,W",
    row_handler=parse_kucoin_deposits_withdrawals,
)

DataParser(
    DataParser.TYPE_EXCHANGE,
    "KuCoin Bundle Deposits History",
    ["UID","Account Type","Time(UTC+08:00)","Remarks","Status","Fee","Amount","Coin","Transfer Network"],
    worksheet_name="Kucoin B D",
    row_handler=parse_kucoin_bundle_deposits_withdrawals,
)

DataParser(
    DataParser.TYPE_EXCHANGE,
    "KuCoin Bundle Withdrawals History",

    ["UID","Account Type","Time(UTC+08:00)","Remarks","Status","Fee","Amount","Coin","Transfer Network","Withdrawal Address/Account"],
    worksheet_name="Kucoin B W",
    row_handler=parse_kucoin_bundle_deposits_withdrawals,
)

DataParser(
    DataParser.TYPE_EXCHANGE,
    "KuCoin Bundle Earn Orders Profit History",

    ["UID","Account Type","Order ID","Time(UTC+08:00)","Staked Coin","Product Type","Product Name","Earnings Coin","Earnings Type","Remarks","Amount","Amount（USDT）","Fee"],
    worksheet_name="Kucoin B EOP",
    row_handler=parse_kucoin_bundle_earn_orders_profit,
)

DataParser(
    DataParser.TYPE_EXCHANGE,
    "KuCoin Bundle Earn Orders Stacking History",

    ["UID","Account Type","Staked Time(UTC+08:00)","Staked Coin","Product Type","Product Name","Maturity Date(UTC+08:00)","Amount","Redemption Time(UTC+08:00)","Status"],
    worksheet_name="Kucoin B EOS",
    row_handler=parse_kucoin_bundle_earn_orders_stacking,
)

DataParser(
    DataParser.TYPE_EXCHANGE,
    "KuCoin Bundle Futures Orders Realized PNL",
    ["UID","Account Type","Symbol","Close Type","Realized PNL","Total Realized PNL","Total Funding Fees","Total Trading Fees","Position Opening Time(UTC+08:00)","Position Closing Time(UTC+08:00)"],
    worksheet_name="Kucoin B F PNL",
    row_handler=parse_kucoin_bundle_futures_pnl,
)