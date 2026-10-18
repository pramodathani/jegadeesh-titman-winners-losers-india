# bhavcopy_reader.py

Two layouts: the old CSV (SYMBOL, SERIES, CLOSE, TOTTRDVAL, trailing comma, so read with index_col=False) and the UDiFF layout from 2024-07-08 (only FinInstrmTp STK rows are shares). The date comes from the file name, not the TIMESTAMP column. Series EQ, BE and BZ are kept, EQ preferred. Fund units (ETFs) trade in EQ, so is_fund marks ISINs starting INF; ISINs exist in the files only from about 2018, so earlier delisted funds are caught by name in the build script.
