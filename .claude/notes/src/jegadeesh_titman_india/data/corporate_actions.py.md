# corporate_actions.py

The NSE subject text is free-form. Bonus a:b gives factor (a+b)/b; a split or consolidation takes the first two rupee amounts as old and new face value; dividends are either rupees or a percent of face value. "Sub-division" contains "div", so it is removed before looking for dividends (a bug caught by the first run, where every split also paid a dividend). Rights issues, buybacks, mergers and demergers are not adjusted; large unexplained moves are handled by the data-error rule in the daily builder.
