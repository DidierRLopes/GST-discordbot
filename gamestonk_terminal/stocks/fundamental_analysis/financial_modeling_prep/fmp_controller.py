""" Financial Modeling Prep Controller """
__docformat__ = "numpy"

import argparse
import difflib
from typing import List, Union
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.stocks.fundamental_analysis.financial_modeling_prep import (
    fmp_view,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    check_positive,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    try_except,
    system_clear,
)
from gamestonk_terminal.menu import session


class FinancialModelingPrepController:
    """Financial Modeling Prep Controller"""

    # Command choices
    CHOICES = [
        "cls",
        "home",
        "h",
        "?",
        "help",
        "q",
        "quit",
        "..",
        "exit",
        "r",
        "reset",
    ]

    CHOICES_COMMANDS = [
        "profile",
        "quote",
        "enterprise",
        "dcf",
        "income",
        "balance",
        "cash",
        "metrics",
        "ratios",
        "growth",
    ]
    CHOICES += CHOICES_COMMANDS

    def __init__(
        self,
        ticker: str,
        start: str,
        interval: str,
        queue: List[str] = None,
    ):
        """Constructor

        Parameters
        ----------
        ticker : str
            Fundamental analysis ticker symbol
        start : str
            Stat date of the stock data
        interval : str
            Stock data interval
        """

        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.fmp_parser = argparse.ArgumentParser(add_help=False, prog="fmp")
        self.fmp_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.completer: Union[None, NestedCompleter] = None
        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            self.completer = NestedCompleter.from_nested_dict(choices)

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help"""
        help_text = f"""
Financial Modeling Prep Menu:

Ticker: {self.ticker}

    profile       profile of the company
    quote         quote of the company
    enterprise    enterprise value of the company over time
    dcf           discounted cash flow of the company over time
    income        income statements of the company
    balance       balance sheet of the company
    cash          cash flow statement of the company
    metrics       key metrics of the company
    ratios        financial ratios of the company
    growth        financial statement growth of the company
        """
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input
        Parameters
        -------
        an_input : str
            string with input arguments
        Returns
        -------
        List[str]
            List of commands in the queue to execute
        """

        # Empty command
        if not an_input:
            print("")
            return self.queue

        # Navigation slash is being used
        if "/" in an_input:
            actions = an_input.split("/")

            # Absolute path is specified
            if not actions[0]:
                an_input = "home"
            # Relative path so execute first instruction
            else:
                an_input = actions[0]

            # Add all instructions to the queue
            for cmd in actions[1:][::-1]:
                if cmd:
                    self.queue.insert(0, cmd)

        (known_args, other_args) = self.fmp_parser.parse_known_args(an_input.split())

        # Redirect commands to their correct functions
        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

        getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

        return self.queue

    def call_cls(self, _):
        """Process cls command"""
        system_clear()

    def call_home(self, _):
        """Process home command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_help(self, _):
        """Process help command"""
        self.print_help()

    def call_quit(self, _):
        """Process quit menu command"""
        self.queue.insert(0, "quit")

    def call_exit(self, _):
        """Process exit terminal command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command"""
        self.queue.insert(0, "fmp")
        self.queue.insert(0, "fa")
        if self.ticker:
            self.queue.insert(0, f"load {self.ticker}")
        self.queue.insert(0, "stocks")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    @try_except
    def call_profile(self, other_args: List[str]):
        """Process profile command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="profile",
            description="""
                Prints information about, among other things, the industry, sector exchange and company
                description. The following fields are expected: Address, Beta, Ceo, Changes, Cik, City
                Company name, Country, Currency, Cusip, Dcf, Dcf diff, Default image, Description,
                Exchange, Exchange short name, Full time employees, Image, Industry, Ipo date, Isin,
                Last div, Mkt cap, Phone, Price, Range, Sector, State, Symbol, Vol avg, Website, Zip.
                [Source: Financial Modeling Prep]
            """,
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            fmp_view.display_profile(self.ticker)

    @try_except
    def call_quote(self, other_args: List[str]):
        """Process quote command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="quote",
            description="""
                Prints actual information about the company which is, among other things, the day high,
                market cap, open and close price and price-to-equity ratio. The following fields are
                expected: Avg volume, Change, Changes percentage, Day high, Day low, Earnings
                announcement, Eps, Exchange, Market cap, Name, Open, Pe, Previous close, Price, Price
                avg200, Price avg50, Shares outstanding, Symbol, Timestamp, Volume, Year high, and Year
                low. [Source: Financial Modeling Prep]
            """,
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            fmp_view.display_quote(self.ticker)

    @try_except
    def call_enterprise(self, other_args: List[str]):
        """Process income command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="enterprise",
            description="""
                Prints stock price, number of shares, market capitalization and
                enterprise value over time. The following fields are expected: Add total debt,
                Enterprise value, Market capitalization, Minus cash and cash equivalents, Number
                of shares, Stock price, and Symbol. [Source: Financial Modeling Prep]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=1,
            help="Limit of latest years/quarters.",
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter fundamental data flag.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.display_enterprise(
                ticker=self.ticker,
                number=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )

    @try_except
    def call_dcf(self, other_args: List[str]):
        """Process dcf command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dcf",
            description="""
                Prints the discounted cash flow of a company over time including the DCF of today. The
                following fields are expected: DCF, Stock price, and Date. [Source: Financial Modeling
                Prep]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=1,
            help="Limit of latest years/quarters.",
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter fundamental data flag.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.display_discounted_cash_flow(
                ticker=self.ticker,
                number=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )

    @try_except
    def call_income(self, other_args: List[str]):
        """Process income command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="inc",
            description="""
                Prints a complete income statement over time. This can be either quarterly or annually.
                The following fields are expected: Accepted date, Cost and expenses, Cost of
                revenue, Depreciation and amortization, Ebitda, Ebitdaratio, Eps, Epsdiluted, Filling
                date, Final link, General and administrative expenses, Gross profit, Gross profit
                ratio, Income before tax, Income before tax ratio, Income tax expense, Interest
                expense, Link, Net income, Net income ratio, Operating expenses, Operating income,
                Operating income ratio, Other expenses, Period, Research and development expenses,
                Revenue, Selling and marketing expenses, Total other income expenses net, Weighted
                average shs out, Weighted average shs out dil [Source: Financial Modeling Prep]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=1,
            help="Limit of latest years/quarters.",
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter fundamental data flag.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.display_income_statement(
                ticker=self.ticker,
                number=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )

    @try_except
    def call_balance(self, other_args: List[str]):
        """Process balance command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="bal",
            description="""
                Prints a complete balance sheet statement over time. This can be
                either quarterly or annually. The following fields are expected: Accepted date,
                Account payables, Accumulated other comprehensive income loss, Cash and cash
                equivalents, Cash and short term investments, Common stock, Deferred revenue,
                Deferred revenue non current, Deferred tax liabilities non current, Filling date,
                Final link, Goodwill, Goodwill and intangible assets, Intangible assets, Inventory,
                Link, Long term debt, Long term investments, Net debt, Net receivables, Other assets,
                Other current assets, Other current liabilities, Other liabilities, Other non current
                assets, Other non current liabilities, Othertotal stockholders equity, Period, Property
                plant equipment net, Retained earnings, Short term debt, Short term investments, Tax
                assets, Tax payables, Total assets, Total current assets, Total current liabilities,
                Total debt, Total investments, Total liabilities, Total liabilities and stockholders
                equity, Total non current assets, Total non current liabilities, and Total stockholders
                equity. [Source: Financial Modeling Prep]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=1,
            help="Limit of latest years/quarters.",
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter fundamental data flag.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.display_balance_sheet(
                ticker=self.ticker,
                number=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )

    @try_except
    def call_cash(self, other_args: List[str]):
        """Process cash command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cash",
            description="""
                Prints a complete cash flow statement over time. This can be either
                quarterly or annually. The following fields are expected: Accepted date, Accounts
                payables, Accounts receivables, Acquisitions net, Capital expenditure, Cash at
                beginning of period, Cash at end of period, Change in working capital, Common stock
                issued, Common stock repurchased, Debt repayment, Deferred income tax, Depreciation and
                amortization, Dividends paid, Effect of forex changes on cash, Filling date, Final
                link, Free cash flow, Inventory, Investments in property plant and equipment, Link, Net
                cash provided by operating activities, Net cash used for investing activities, Net cash
                used provided by financing activities, Net change in cash, Net income, Operating cash
                flow, Other financing activities, Other investing activities, Other non cash items,
                Other working capital, Period, Purchases of investments, Sales maturities of
                investments, Stock based compensation. [Source: Financial Modeling Prep]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=1,
            help="Limit of latest years/quarters.",
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter fundamental data flag.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.display_cash_flow(
                ticker=self.ticker,
                number=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )

    @try_except
    def call_metrics(self, other_args: List[str]):
        """Process metrics command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="metrics",
            description="""
                Prints a list of the key metrics of a company over time. This can be either
                quarterly or annually. This includes, among other things, Return on Equity (ROE),
                Working Capital, Current Ratio and Debt to Assets. The following fields are expected:
                Average inventory, Average payables, Average receivables, Book value per share, Capex
                per share, Capex to depreciation, Capex to operating cash flow, Capex to revenue, Cash
                per share, Current ratio, Days of inventory on hand, Days payables outstanding, Days
                sales outstanding, Debt to assets, Debt to equity, Dividend yield, Earnings yield,
                Enterprise value, Enterprise value over EBITDA, Ev to free cash flow, Ev to operating
                cash flow, Ev to sales, Free cash flow per share, Free cash flow yield, Graham net net,
                Graham number, Income quality, Intangibles to total assets, Interest debt per share,
                Inventory turnover, Market cap, Net current asset value, Net debt to EBITDA, Net income
                per share, Operating cash flow per share, Payables turnover, Payout ratio, Pb ratio, Pe
                ratio, Pfcf ratio, Pocfratio, Price to sales ratio, Ptb ratio, Receivables turnover,
                Research and development to revenue, Return on tangible assets, Revenue per share,
                Roe, Roic, Sales general and administrative to revenue, Shareholders equity per
                share, Stock based compensation to revenue, Tangible book value per share, and Working
                capital. [Source: Financial Modeling Prep]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=1,
            help="Limit of latest years/quarters.",
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter fundamental data flag.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.display_key_metrics(
                ticker=self.ticker,
                number=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )

    @try_except
    def call_ratios(self, other_args: List[str]):
        """Process cash command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ratios",
            description="""
                Prints in-depth ratios of a company over time. This can be either quarterly or
                annually. This contains, among other things, Price-to-Book Ratio, Payout Ratio and
                Operating Cycle. The following fields are expected: Asset turnover, Capital expenditure
                coverage ratio, Cash conversion cycle, Cash flow coverage ratios, Cash flow to debt
                ratio, Cash per share, Cash ratio, Company equity multiplier, Current ratio, Days of
                inventory outstanding, Days of payables outstanding, Days of sales outstanding, Debt
                equity ratio, Debt ratio, Dividend paid and capex coverage ratio, Dividend payout ratio,
                Dividend yield, Ebit per revenue, Ebt per ebit, Effective tax rate, Enterprise value
                multiple, Fixed asset turnover, Free cash flow operating cash flow ratio, Free cash
                flow per share, Gross profit margin, Inventory turnover, Long term debt to
                capitalization, Net income per EBT, Net profit margin, Operating cash flow per share,
                Operating cash flow sales ratio, Operating cycle, Operating profit margin, Payables
                turnover, Payout ratio, Pretax profit margin, Price book value ratio, Price cash flow
                ratio, Price earnings ratio, Price earnings to growth ratio, Price fair value,
                Price sales ratio, Price to book ratio, Price to free cash flows ratio, Price to
                operating cash flows ratio, Price to sales ratio, Quick ratio, Receivables turnover,
                Return on assets, Return on capital employed, Return on equity, Short term coverage
                ratios, and Total debt to capitalization. [Source: Financial Modeling Prep]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=1,
            help="Limit of latest years/quarters.",
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter fundamental data flag.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.display_financial_ratios(
                ticker=self.ticker,
                number=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )

    @try_except
    def call_growth(self, other_args: List[str]):
        """Process cash command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="growth",
            description=""" Prints the growth of several financial statement items and ratios over
            time. This can be either annually and quarterly. These are, among other things, Revenue
            Growth (3, 5 and 10 years), inventory growth and operating cash flow growth (3, 5 and 10
            years). The following fields are expected: Asset growth, Book valueper share growth, Debt
            growth, Dividendsper share growth, Ebitgrowth, Epsdiluted growth, Epsgrowth, Five y
            dividendper share growth per share, Five y net income growth per share, Five y operating c
            f growth per share, Five y revenue growth per share, Five y shareholders equity growth per
            share, Free cash flow growth, Gross profit growth, Inventory growth, Net income growth,
            Operating cash flow growth, Operating income growth, Rdexpense growth, Receivables growth,
            Revenue growth, Sgaexpenses growth, Ten y dividendper share growth per share, Ten y net
            income growth per share, Ten y operating c f growth per share, Ten y revenue growth per
            share, Ten y shareholders equity growth per share, Three y dividendper share growth per
            share, Three y net income growth per share, Three y operating c f growth per share, Three y
            revenue growth per share, Three y shareholders equity growth per share, Weighted average
            shares diluted growth, and Weighted average shares growth [Source: Financial Modeling Prep]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=1,
            help="Limit of latest years/quarters.",
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter fundamental data flag.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.display_financial_statement_growth(
                ticker=self.ticker,
                number=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )


def menu(
    ticker: str,
    start: str,
    interval: str,
    queue: List[str] = None,
):
    """Financial Modeling Prep menu

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    start : str
        Start date of the stock data
    interval : str
        Stock data interval
    """

    fmp_controller = FinancialModelingPrepController(ticker, start, interval, queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if fmp_controller.queue and len(fmp_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if fmp_controller.queue[0] in ("q", "..", "quit"):
                if len(fmp_controller.queue) > 1:
                    return fmp_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = fmp_controller.queue[0]
            fmp_controller.queue = fmp_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in fmp_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /stocks/fa/fmp/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                fmp_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and fmp_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /stocks/fa/fmp/ $ ",
                    completer=fmp_controller.completer,
                    search_ignore_case=True,
                )
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /stocks/fa/fmp/ $ ")

        try:
            # Process the input command
            fmp_controller.queue = fmp_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /stocks/options menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                fmp_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                if " " in an_input:
                    candidate_input = (
                        f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                    )
                else:
                    candidate_input = similar_cmd[0]

                if candidate_input == an_input:
                    an_input = ""
                    fmp_controller.queue = []
                    print("\n")
                    continue

                print(f" Replacing by '{an_input}'.")
                fmp_controller.queue.insert(0, an_input)
            else:
                print("\n")
                an_input = ""
                fmp_controller.queue = []
