import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import yfinance as yf
import locale


class strategy():
    '''The strategy class contains many stock stragies which have an input
of the stock ticker desired to be analysed and output of a number between
0 and 1, 0 indicating a strong sell and 1 indicating a strong buy'''

    def __init__(self, stock_ticker):
        self.ticker = stock_ticker
        self.signals = {}

    # Implement signal for the rsi strategy
    def rsi(self, start, end, hi, lo, mva_days):
        startdate = datetime(*start)  ##Tuple --> datetime object
        enddate = datetime(*end)  # Tuple --> datetime object
        # Import and treat data
        data = yf.download(self.ticker, start=startdate, end=enddate)  # Import stock data
        delta = data["Adj Close"].diff(
            1)  # Make pd dataframe of differences between successive trading period closing prices
        delta.dropna(inplace=True)  # Remove NaN values
        positive = delta.copy()  # Initialise variable for gains
        negative = delta.copy()  # Initialise variable for losses
        positive[positive < 0] = 0  # Set losses equal to 0
        negative[negative > 0] = 0  # Set gains equal to 0
        average_gain = positive.rolling(window=mva_days).mean()  # Create pandas series obeject of 14 day mean of gains
        average_loss = abs(
            negative.rolling(window=mva_days).mean())  # Create pandas series object of 14 day mean of gains

        # Calculate RSI

        relative_strength = average_gain / average_loss  # Create pandas series for relatie strenght for specific times
        rsi = 100.0 - (100.0 / (1.0 + relative_strength))  # Convert relative strenght into rsi
        combined = pd.DataFrame()  # Initialise final df

        combined["Open"] = data["Open"]
        combined["High"] = data["High"]
        combined["Low"] = data["Low"]

        combined["Adj Close"] = data["Adj Close"]  # Add column of closing prices
        combined["rsi"] = rsi  # Add column for rsi value

        # Determine signals
        prev_rsi = combined.loc[datetime(*start).strftime("%Y-%m-%d %H:%M:%S"), 'rsi']
        for index, row in combined.iloc[1:].iterrows():
            try:
                if row["rsi"] < hi and prev_rsi > hi:
                    self.signals[combined.index[combined.index.get_loc(index) + 1]] = 'SELL'
                elif row["rsi"] > lo and prev_rsi < lo:
                    self.signals[combined.index[combined.index.get_loc(index) + 1]] = 'BUY'
                else:
                    self.signals[combined.index[combined.index.get_loc(index) + 1]] = 'HOLD'
            except IndexError:
                print("---")
            prev_rsi = row['rsi']
        return combined

    def plot_signals(self,data, transactions, *args):
        plt.figure(figsize=(12, 8))
        plt.subplot(211)
        plt.plot(data.index, data["Adj Close"], color="lightgray")
        plt.title("Adjusted Close Price")
        plt.grid(True, color="#555555")
        plt.gca().set_axisbelow(True)
        plt.gca().set_facecolor("black")
        plt.gcf().set_facecolor("#121212")
        plt.gca().tick_params(axis="x", colors="white")
        plt.gca().tick_params(axis="y", colors="white")
        for index in transactions:
            if transactions[index] == "SELL":
                plt.scatter(index, data.loc[index, "Open"], color = "red")
            elif transactions[index] == "BUY":
                plt.scatter(index, data.loc[index, "Open"], color = "green")
        plt.subplot(212)
        plt.plot(data.index, data["rsi"], color="lightgray")
        plt.axhline(0, linestyle="--", alpha=0.5, color="#ff0000")
        plt.axhline(10, linestyle="--", alpha=0.5, color="#ffaa00")
        plt.axhline(20, linestyle="--", alpha=0.5, color="#00ff00")
        plt.axhline(30, linestyle="--", alpha=0.5, color="#cccccc")
        plt.axhline(70, linestyle="--", alpha=0.5, color="#cccccc")
        plt.axhline(80, linestyle="--", alpha=0.5, color="#00ff00")
        plt.axhline(90, linestyle="--", alpha=0.5, color="#ffaa00")
        plt.axhline(100, linestyle="--", alpha=0.5, color="#ff0000")
        plt.title("RSI Value")
        plt.grid(False)
        plt.gca().set_axisbelow(True)
        plt.gca().set_facecolor("black")
        plt.gca().tick_params(axis="x", colors="white")
        plt.gca().tick_params(axis="y", colors="white")
        for index in transactions:
            if transactions[index] == "SELL":
                plt.scatter(index, data.loc[index, "rsi"], color="red")
            elif transactions[index] == "BUY":
                plt.scatter(index, data.loc[index, "rsi"], color="green")

        plt.show()

    def get_signals(self, when):
        when_date = datetime(*when)
        if when_date in self.signals:
            return f"At {when_date}, you should {self.signals[when_date]}"
        else:
            return f"No signal available for {when_date}. Market closed that day."

    def backtest(self, capital, data,start):
        locale.setlocale(locale.LC_ALL, '')
        stocks = 0
        money_left = capital
        transactions = {}
        for index in self.signals:
            new = 0
            price = data.loc[index, "Open"]
            if self.signals[index] == "BUY":
                if money_left >= price:
                    transactions[index] = "BUY"
                    new = (money_left // price)
                    stocks += new
                    money_left -= money_left // price * price
                    print(
                        f"bought on {index} {round(new)} stock(s), for {locale.currency(price, grouping=True)}. I now have {round(stocks)} stocks and {locale.currency(money_left, grouping=True)} left")
                else:
                    continue
            elif self.signals[index] == "SELL":
                if stocks != 0:
                    transactions[index] = "SELL"
                    money_left += stocks * price
                    print(
                        f"sold on {index} {round(stocks)} stocks, for {locale.currency(price, grouping=True)}. I now have {round(new)} stocks and {locale.currency(money_left, grouping=True)} left")
                    stocks = 0
                else:
                    continue
            else:
                continue
        print(
            f"{locale.currency(money_left + (stocks * price), grouping=True)} - you made a profit/loss of {locale.currency(money_left + (stocks * price) - capital, grouping=True)} since {start}")
        return transactions


# Example usage
test = strategy("AMZN")
test.plot_signals(
    test.rsi((2023, 1, 4), (2024, 1, 31), 80, 20, 14),
    (test.backtest(1000000, test.rsi((2023, 1, 4), (2024, 1, 31), 80, 20, 14),(2023, 1, 4)))
    )


