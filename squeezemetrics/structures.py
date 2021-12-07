from recordclass import recordclass

StockId = recordclass("StockId", "ticker gsheet last_seen ibkr_timeout no_shares")
