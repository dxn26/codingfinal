import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import yfinance as yf
class strategy():
    '''The strategy class contains many stock stragies which have an input
of the stock ticker desired to be analysed and output of a number between
0 and 1, 0 indicating a strong sell and 1 indicating a strong buy'''
    def __init__(self,stock_ticker):
        self.ticker = stock_ticker
        self.signals = {}
    
    #Implement signal for the rsi strategy    
    def rsi(self,start, end, hi,lo,mva_days):
        startdate = datetime(*start) ##Tuple --> datetime object
        enddate = datetime(*end)     #Tuple --> datetime object
        #Import and treat data
        data = yf.download(self.ticker, start=startdate, end=enddate) #Import stock data
        delta = data["Adj Close"].diff(1) #Make pd dataframe of differences between successive trading period closing prices
        delta.dropna(inplace=True) #Remove NaN values
        positive = delta.copy()    #Initialise variable for gains
        negative = delta.copy()    #Initialise variable for losses
        positive[positive < 0] = 0  #Set losses equal to 0
        negative[negative > 0] = 0  #Set gains equal to 0
        average_gain = positive.rolling(window=mva_days).mean() #Create pandas series obeject of 14 day mean of gains
        average_loss = abs(negative.rolling(window=mva_days).mean()) #Create pandas series object of 14 day mean of gains

        #Calculate RSI
        
        relative_strength = average_gain / average_loss #Create pandas series for relatie strenght for specific times
        rsi = 100.0 - (100.0 / (1.0 + relative_strength)) #Convert relative strenght into rsi
        combined = pd.DataFrame() #Initialise final df
        combined["Adj Close"] = data["Adj Close"] #Add column of closing prices
        combined["rsi"] = rsi #Add column for rsi value

        #Give signal
        # Determine signals
        for index, row in combined.iterrows():
            if row["rsi"] > hi:
                self.signals[index] = 'SELL'
            elif row["rsi"] < lo:
                self.signals[index] = 'BUY'
            else:
                self.signals[index] = 'HOLD'
        for key in self.signals:
            print("At {}, you should {}".format(key,self.signals[key]))
        return combined

    def plot_signals(data):
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

        plt.show()

    def get_signals(self, when):
        when_date = datetime(*when)
        if when_date in self.signals:
            return f"At {when_date}, you should {self.signals[when_date]}"
        else:
            return f"No signal available for {when_date}. Market closed that day."


# Example usage
test = strategy('AAPL')
test.rsi((2022, 1, 1), (2024, 1, 31), 70, 30,14)
print(test.get_signals((2023, 11, 22)))
test.plot_signals(test.rsi((2022, 1, 1), (2024, 1, 31), 70, 30,14))




    

