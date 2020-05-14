import pandas as pd
import mplfinance as mpf
import numpy as np
import matplotlib.pyplot as plt

def import_data(asset):
    """
    Imports data from csv file and returns a DataFrame.
    """
    data = pd.read_csv('data/' + asset + ".csv", header=0, index_col=0, parse_dates=True)
    data.index = pd.to_datetime(data.index, format="%Y%m%d")
    return data

def plot_candlestick(data, cant_mav = None, MA1 = None, MA2 = None, MA3 = None):
    """
    Plots candlestick chart. Must be passed the number of moving averages desired
    and the values of each. The max number of moving averages is 3.
    """
    style = dict(style_name    = 'aldo',
             base_mpl_style= 'dark_background', 
             marketcolors  = {'candle'  : {'up':'#00ff00', 'down':'#ff0000'},
                              'edge'    : {'up':'#00ff00', 'down':'#ff0000'},
                              'wick'    : {'up':'#ffffff', 'down':'#ffffff'},
                              'ohlc'    : {'up':'#ffffff', 'down':'#ffffff'},
                              'volume'  : {'up':'#00ff00', 'down':'#ff0000'},
                              'vcdopcod': False, # Volume Color Depends On Price Change On Day
                              'alpha'   : 1.0,
                             },
             mavcolors     = ['#fcba03','#cf03fc','#fcf120'],
             y_on_right    = True,
             gridcolor     = None,
             gridstyle     = None,
             facecolor     = None,
             rc            = [ ('axes.edgecolor'  , 'white'   ),
                               ('axes.linewidth'  ,  1.5      ),
                               ('axes.labelsize'  , 'large'   ),
                               ('axes.labelweight', 'semibold'),
                               ('axes.grid'       , True      ),
                               ('axes.grid.axis'  , 'both'    ),
                               ('axes.grid.which' , 'major'   ),
                               ('grid.alpha'      ,  0.9      ),
                               ('grid.color'      , '#b0b0b0' ),
                               ('grid.linestyle'  , '--'      ),
                               ('grid.linewidth'  ,  0.8      ),
                               ('figure.facecolor', '#0a0a0a' ),
                               ('patch.linewidth' ,  1.0      ),
                               ('lines.linewidth' ,  1.0      ),
                               ('font.weight'     , 'medium'  ),
                               ('font.size'       ,  10.0     ),
                             ],
             base_mpf_style= 'aldo'
            )


    if cant_mav is not None:
        if cant_mav == 1:
            mav = MA1
        elif cant_mav == 2:
            mav = (MA1, MA2)
        elif cant_mav == 3:
            mav = (MA1, MA2, MA3)
        else:
            print("Max cant of moving averages is 3")
            
        mpf.plot(data, type='candle', style=style,
            title='Asset',
            ylabel='Price ($)',
            ylabel_lower='Shares \nTraded',
            volume=True,
            mav = mav)
    else:
        mpf.plot(data, type='candle', style=style,
            title='Asset',
            ylabel='Price ($)',
            ylabel_lower='Shares \nTraded',
            volume=True)

    plt.show()
        
        
def mav_strategy(asset, short_window, long_window, exponential=False):

    # Initialize the `signals` DataFrame with the `signal` column
    signals = pd.DataFrame(index = asset.index)
    signals['signal'] = 0.0
    
    # Create simple or exponential moving average
    if exponential:
        signals['short_mavg'] = asset['Close'].ewm(span=short_window, adjust=False).mean()
        signals['long_mavg'] = asset['Close'].ewm(span=long_window, adjust=False).mean()
    else:
        signals['short_mavg'] = asset['Close'].rolling(window=short_window, min_periods = 1, center = False).mean()
        signals['long_mavg'] = asset['Close'].rolling(window=long_window, min_periods = 1, center=False).mean()

    # Create signals
    signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] 
                                            > signals['long_mavg'][short_window:], 1.0, 0.0)   

    # Generate trading orders
    signals['positions'] = signals['signal'].diff()
    
    return signals

def plot_strategy(asset, signals):
    # Initialize the plot figure
    fig = plt.figure(figsize = (12,6))

    # Add a subplot and label for y-axis
    ax1 = fig.add_subplot(111,  ylabel='Price in AR$')

    # Plot the closing price
    asset['Close'].plot(ax=ax1, color='b', lw=2.)

    # Plot the short and long moving averages
    signals[['short_mavg', 'long_mavg']].plot(ax=ax1, lw=2., color = ['y','k'])

    # Plot the buy signals
    ax1.plot(signals.loc[signals.positions == 1.0].index, 
         signals.short_mavg[signals.positions == 1.0],
         '^', markersize=10, color='g')
         
    # Plot the sell signals
    ax1.plot(signals.loc[signals.positions == -1.0].index, 
         signals.short_mavg[signals.positions == -1.0],
         'v', markersize=10, color='r')
    
    plt.grid()
    # Show the plot
    plt.show()

def backtest(asset, signals, initial_capital = float(100000.0)):

    # Create a DataFrame `positions`
    positions = pd.DataFrame(index=signals.index).fillna(0.0)

    # Buy a 100 shares
    positions['Asset'] = 100*signals['signal']   
  
    # Initialize the portfolio with value owned   
    portfolio = positions.multiply(asset['Adj Close'], axis=0)

    # Store the difference in shares owned 
    pos_diff = positions.diff()

    # Add `holdings` to portfolio
    portfolio['holdings'] = (positions.multiply(asset['Adj Close'], axis=0)).sum(axis=1)

    # Add `cash` to portfolio
    portfolio['cash'] = initial_capital - (pos_diff.multiply(asset['Adj Close'], axis=0)).sum(axis=1).cumsum()   

    # Add `total` to portfolio
    portfolio['total'] = portfolio['cash'] + portfolio['holdings']

    # Add `returns` to portfolio
    portfolio['returns'] = portfolio['total'].pct_change()
    
    return portfolio

def plot_backtesting(portfolio, signals):
    # Create a figure
    fig = plt.figure(figsize = (12,6))

    ax1 = fig.add_subplot(111, ylabel='Portfolio value in $')

    # Plot the equity curve in dollars
    portfolio['total'].plot(ax=ax1, lw=2.)

    ax1.plot(portfolio.loc[signals.positions == 1.0].index, 
         portfolio.total[signals.positions == 1.0],
         '^', markersize=10, color='g')
    ax1.plot(portfolio.loc[signals.positions == -1.0].index, 
         portfolio.total[signals.positions == -1.0],
         'v', markersize=10, color='r')
    plt.grid()

    plt.show()

def STOK(close, low, high, n, slow = 0): 
    STOK = ((close - low.rolling(window=n, min_periods=1, center=False).min())/(high.rolling(window=n, min_periods=1, center=False).max() - low.rolling(window=n, min_periods=1, center=False).min()))*100
    if slow != 0:
        STOK = STOK.rolling(window=slow, min_periods=1, center=False).mean()
    return STOK

def STOD(STOK):
    STOD = STOK.rolling(window = 3, min_periods=1, center=False).mean()
    return STOD

def get_intday(symbol, desde, hasta, interval):
    '''
    desde: YYYY-MM-DD
    hasta: YYYY-MM-DD
    interval: '1m', '3m', '5m', '15m', '30m', '1h', '4h'
    '''
    
    period1 = str(int(datetime.datetime.timestamp(datetime.datetime(int(desde[0:4]), int(desde[5:7]), int(desde[8:]), 11, 0, 0))))
    period2 = str(int(datetime.datetime.timestamp(datetime.datetime(int(hasta[0:4]), int(hasta[5:7]), int(hasta[8:]), 16, 55, 0))))
    
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/'+symbol+'?symbol='+symbol+'&period1='+period1+'&period2='+period2+'&interval='+interval+'&includePrePost=true&events=div%7Csplit%7Cearn&lang=en-US&region=US&crumb=%2FsTZCR4Ghpz&corsDomain=finance.yahoo.com'
    
    r = requests.get(url=url)
    return json.loads(r.text)

def get_timestamp(r):
    return r['chart']['result'][0]['timestamp']

def get_close(r):
    return r['chart']['result'][0]['indicators']['quote'][0]['close']

def get_ohlc_dataframe(r):

    date = r['chart']['result'][0]['timestamp']
    index = []
    for d in date:
        index.append(datetime.datetime.fromtimestamp(d))
        #index.append(datetime.datetime.utcfromtimestamp(d).strftime('%d-%m-%Y %H:%M:%S'))
    
    low = r['chart']['result'][0]['indicators']['quote'][0]['low']
    high = r['chart']['result'][0]['indicators']['quote'][0]['high']
    open = r['chart']['result'][0]['indicators']['quote'][0]['open']
    close = r['chart']['result'][0]['indicators']['quote'][0]['close']
    volume = r['chart']['result'][0]['indicators']['quote'][0]['volume']
                 
    values = {'Open': open,
              'High': high,
              'Low': low,
              'Close': close,
              'Volume': volume}

    data = pd.DataFrame(values, index = index)
    data.index = pd.to_datetime(data.index, format='%d-%m-%Y %H:%M:%S')
    return data