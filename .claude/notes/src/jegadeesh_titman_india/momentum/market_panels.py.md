# market_panels.py

Standard months are calendar months. The Panel B ("skip a week") holding months run between boundaries that sit skip_sessions sessions after each month end; a cohort ranked at month end m is held from session m+5. The ranking itself always uses calendar months. The daily table is not cut at the last complete month so that the last shifted month has its closing boundary.
