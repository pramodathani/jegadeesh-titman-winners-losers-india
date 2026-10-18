# ranking.py

Past return needs all J monthly returns. Deciles use floor((rank-1) x 10 / n) + 1, which gives groups differing by at most one share; the first version used ceil(rank x 10 / n), which put the lowest share of nine into decile 2 (caught by a test). A month with fewer than 100 ranked shares forms no cohort.
