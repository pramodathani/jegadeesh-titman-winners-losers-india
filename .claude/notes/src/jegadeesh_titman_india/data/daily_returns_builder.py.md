# daily_returns_builder.py

Return on a day is (close x factor + dividend) / previous close of the same share - 1, where the previous close is the share's own last trade, so gaps do not matter. An action with an ex-date that is not a trading day applies on the first trading day after. Returns below -50% or above +100% are set to zero and logged, as in the approved plan; 864 of 10.4 million rows were hit, most before 2007.
