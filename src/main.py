from langplot import LangPlot
from langplot import PlotterFactory
from coingecko_api import get_coin_ids_list

get_coin_ids_list()
factory = PlotterFactory("Show me a pie chart of volume of eth and bitcoin over last 30 days")
plotter = factory.create_plotter()
# plotter.plot(theme='plotly_dark')
