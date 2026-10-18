"""Resumable downloads of the extra data the study needs."""

import datetime
import json
import pathlib
import sys

from jegadeesh_titman_india.data.nse_session import NseSession


class BhavcopyTopUp:
    """Downloads the share bhavcopies missing from the earlier files.

    Attributes:
        folder: Where the new raw zip files are stored.
        session: The HTTP session.
    """

    URL: str = (
        'https://nsearchives.nseindia.com/content/cm/'
        'BhavCopy_NSE_CM_0_0_0_{stamp}_F_0000.csv.zip'
    )
    OLD_URL: str = (
        'https://nsearchives.nseindia.com/content/historical/EQUITIES/'
        '{year}/{month}/cm{day}{month}{year}bhav.csv.zip'
    )
    LAST_OLD_DAY: datetime.date = datetime.date(2024, 7, 5)

    def url(self, day: datetime.date) -> str:
        """Gives the address of a day's file in the layout NSE used then.

        Args:
            day: The trading date.

        Returns:
            The old address up to 5 July 2024 and the UDiFF address after.

        Raises:
            None.
        """
        if day <= self.LAST_OLD_DAY:
            return self.OLD_URL.format(
                year=day.year,
                month=day.strftime('%b').upper(),
                day=day.strftime('%d'),
            )
        return self.URL.format(stamp=day.strftime('%Y%m%d'))

    def __init__(self, folder: pathlib.Path, session: NseSession) -> None:
        """Creates the downloader.

        Args:
            folder: The folder for the raw files.
            session: The HTTP session.

        Returns:
            None.

        Raises:
            None.
        """
        self.folder = folder
        self.session = session

    def run(self, first: datetime.date, last: datetime.date) -> None:
        """Downloads every weekday from first to last that is not on disk.

        Files go in one sub-folder per year, as the daily returns script
        reads them.

        Args:
            first: The first date to try.
            last: The last date to try.

        Returns:
            None.

        Raises:
            None.
        """
        self.folder.mkdir(parents=True, exist_ok=True)
        missing_file = self.folder / 'not_available.txt'
        known_missing = set()
        if missing_file.exists():
            known_missing = set(missing_file.read_text().split())
        day = first
        while day <= last:
            name = day.isoformat()
            year_folder = self.folder / str(day.year)
            year_folder.mkdir(exist_ok=True)
            target = year_folder / f'{name}.csv.zip'
            skip = day.weekday() >= 5 or target.exists()
            if name in known_missing:
                skip = True
            if not skip:
                response = self.session.get(self.url(day))
                if response.status_code == 200:
                    target.write_bytes(response.content)
                    print('saved', name, len(response.content), flush=True)
                else:
                    with missing_file.open('a') as handle:
                        handle.write(name + '\n')
                    print('missing', name, response.status_code, flush=True)
            day += datetime.timedelta(days=1)


class CorporateActionsRefresh:
    """Downloads one year of NSE corporate actions.

    Attributes:
        folder: Where the JSON files go.
        session: The HTTP session.
    """

    URL: str = 'https://www.nseindia.com/api/corporates-corporateActions'

    def __init__(self, folder: pathlib.Path, session: NseSession) -> None:
        """Creates the downloader.

        Args:
            folder: The folder for the JSON files.
            session: The HTTP session.

        Returns:
            None.

        Raises:
            None.
        """
        self.folder = folder
        self.session = session

    def run(self, year: int, last: datetime.date) -> None:
        """Downloads corporate actions for a year up to a date.

        Args:
            year: The calendar year.
            last: The last date to include.

        Returns:
            None.

        Raises:
            TypeError: When the answer is not a JSON list.
        """
        self.folder.mkdir(parents=True, exist_ok=True)
        params = {
            'index': 'equities',
            'from_date': f'01-01-{year}',
            'to_date': last.strftime('%d-%m-%Y'),
        }
        response = self.session.get(self.URL, params=params)
        rows = response.json()
        if not isinstance(rows, list):
            raise TypeError('Unexpected corporate actions answer')
        (self.folder / f'{year}.json').write_text(json.dumps(rows))
        print('corporate actions', year, len(rows), flush=True)


class IndexTotalReturnDownload:
    """Downloads the NIFTY 500 total return index in one request.

    Attributes:
        target: The JSON file to write.
        session: The HTTP session.
    """

    URL: str = 'https://www.niftyindices.com/BackPage/getTotalReturnIndexString'

    def __init__(self, target: pathlib.Path, session: NseSession) -> None:
        """Creates the downloader.

        Args:
            target: The JSON file to write.
            session: The HTTP session.

        Returns:
            None.

        Raises:
            None.
        """
        self.target = target
        self.session = session

    def run(self, last: datetime.date) -> None:
        """Downloads the whole history up to a date.

        Args:
            last: The last date to ask for.

        Returns:
            None.

        Raises:
            RuntimeError: When no rows come back.
        """
        cinfo = (
            "{'name':'NIFTY 500','startDate':'01-Jan-1995',"
            f"'endDate':'{last.strftime('%d-%b-%Y')}',"
            "'indexName':'NIFTY 500'}"
        )
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.niftyindices.com',
            'Referer': 'https://www.niftyindices.com/reports/historical-data',
        }
        response = self.session.post_json(self.URL, {'cinfo': cinfo}, headers)
        rows = response.json()
        if not isinstance(rows, list) or not rows:
            raise RuntimeError('No total return rows')
        self.target.parent.mkdir(parents=True, exist_ok=True)
        self.target.write_text(json.dumps(rows))
        print('total return rows', len(rows), flush=True)


class IimaFactorsDownload:
    """Downloads the IIMA monthly four-factor file.

    Attributes:
        folder: The folder for the CSV.
        session: The HTTP session.
    """

    NAME: str = (
        '2025-12_FourFactors_and_Market_Returns_Monthly_'
        'SurvivorshipBiasAdjusted.csv'
    )
    URL: str = (
        'https://faculty.iima.ac.in/iffm/Indian-Fama-French-Momentum/DATA/'
    )

    def __init__(self, folder: pathlib.Path, session: NseSession) -> None:
        """Creates the downloader.

        Args:
            folder: The folder for the CSV.
            session: The HTTP session.

        Returns:
            None.

        Raises:
            None.
        """
        self.folder = folder
        self.session = session

    def run(self) -> None:
        """Downloads the file.

        Args:
            None.

        Returns:
            None.

        Raises:
            RuntimeError: When the download fails.
        """
        self.folder.mkdir(parents=True, exist_ok=True)
        response = self.session.get(self.URL + self.NAME)
        if response.status_code != 200:
            raise RuntimeError(f'IIMA download {response.status_code}')
        (self.folder / self.NAME).write_bytes(response.content)
        print('iima bytes', len(response.content), flush=True)


class MarketCapDownload:
    """Downloads NSE market cap files from the PR bhavcopy zips.

    Attributes:
        folder: Where the zips go.
        session: The HTTP session.
    """

    URL: str = (
        'https://nsearchives.nseindia.com/archives/equities/bhavcopy/pr/'
        'PR{stamp}.zip'
    )

    def __init__(self, folder: pathlib.Path, session: NseSession) -> None:
        """Creates the downloader.

        Args:
            folder: The folder for the zips.
            session: The HTTP session.

        Returns:
            None.

        Raises:
            None.
        """
        self.folder = folder
        self.session = session

    def run(self, first: datetime.date, last: datetime.date) -> None:
        """Downloads the last trading day's zip of every month.

        Args:
            first: A date in the first month.
            last: A date in the last month.

        Returns:
            None.

        Raises:
            None.
        """
        self.folder.mkdir(parents=True, exist_ok=True)
        year = first.year
        month = first.month
        while (year, month) <= (last.year, last.month):
            if month == 12:
                next_first = datetime.date(year + 1, 1, 1)
            else:
                next_first = datetime.date(year, month + 1, 1)
            day = min(next_first - datetime.timedelta(days=1), last)
            self.fetch_month_end(day)
            year = next_first.year
            month = next_first.month

    def fetch_month_end(self, day: datetime.date) -> None:
        """Walks back from a date until a zip is found, or gives up.

        Args:
            day: The date to start from.

        Returns:
            None.

        Raises:
            None.
        """
        for step in range(8):
            candidate = day - datetime.timedelta(days=step)
            if candidate.weekday() >= 5:
                continue
            target = self.folder / f'PR{candidate.strftime("%d%m%y")}.zip'
            if target.exists():
                return
            url = self.URL.format(stamp=candidate.strftime('%d%m%y'))
            response = self.session.get(url)
            if response.status_code == 200:
                target.write_bytes(response.content)
                print('saved', target.name, flush=True)
                return
        print('no market cap zip near', day, flush=True)


class ResultsDatesDownload:
    """Downloads NSE quarterly results filings, one year per request.

    Attributes:
        folder: The folder for the JSON files.
        session: The HTTP session.
    """

    URL: str = 'https://www.nseindia.com/api/corporates-financial-results'

    def __init__(self, folder: pathlib.Path, session: NseSession) -> None:
        """Creates the downloader.

        Args:
            folder: The folder for the JSON files.
            session: The HTTP session.

        Returns:
            None.

        Raises:
            None.
        """
        self.folder = folder
        self.session = session

    def run(self, first_year: int, last: datetime.date) -> None:
        """Downloads each year not already on disk.

        Args:
            first_year: The first calendar year.
            last: The last date to include.

        Returns:
            None.

        Raises:
            None.
        """
        self.folder.mkdir(parents=True, exist_ok=True)
        for year in range(first_year, last.year + 1):
            target = self.folder / f'{year}.json'
            end = datetime.date(year, 12, 31)
            if year == last.year:
                end = last
            if target.exists() and year != last.year:
                continue
            params = {
                'index': 'equities',
                'period': 'Quarterly',
                'from_date': f'01-01-{year}',
                'to_date': end.strftime('%d-%m-%Y'),
            }
            response = self.session.get(self.URL, params=params)
            rows = response.json()
            if isinstance(rows, list):
                target.write_text(json.dumps(rows))
                print('results', year, len(rows), flush=True)
            else:
                print('results failed', year, str(rows)[:100], flush=True)


class DataDownloadApplication:
    """Runs every extra download for the study.

    Attributes:
        root: The study's data folder.
        last: The last date to fetch up to.
    """

    def __init__(
        self,
        root: pathlib.Path,
        last: datetime.date,
        full_history: bool = False,
    ) -> None:
        """Creates the application.

        Args:
            root: The study's data folder.
            last: The last date to fetch up to.
            full_history: Whether to fetch every bhavcopy since 1995 and
                every year of corporate actions, instead of only what the
                earlier study's files lack.

        Returns:
            None.

        Raises:
            None.
        """
        self.root = root
        self.last = last
        self.full_history = full_history

    def run(self) -> None:
        """Runs all downloads in turn.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        session = NseSession()
        session.warm_up()
        nse = self.root / 'nse'
        IndexTotalReturnDownload(nse / 'nifty500_tri.json', session).run(
            self.last
        )
        IimaFactorsDownload(nse / 'iima', session).run()
        first_year = self.last.year
        first_day = datetime.date(2026, 10, 7)
        if self.full_history:
            first_year = 1995
            first_day = datetime.date(1995, 1, 2)
        actions = CorporateActionsRefresh(nse / 'corporate_actions', session)
        for year in range(first_year, self.last.year + 1):
            actions.run(year, min(self.last, datetime.date(year, 12, 31)))
        BhavcopyTopUp(nse / 'bhavcopy_raw', session).run(first_day, self.last)
        MarketCapDownload(nse / 'market_cap', session).run(
            datetime.date(2024, 2, 1), self.last
        )
        ResultsDatesDownload(nse / 'results', session).run(2007, self.last)


if __name__ == '__main__':
    DataDownloadApplication(
        pathlib.Path(sys.argv[1]),
        datetime.date.fromisoformat(sys.argv[2]),
        full_history=len(sys.argv) > 3 and sys.argv[3] == 'full',
    ).run()
