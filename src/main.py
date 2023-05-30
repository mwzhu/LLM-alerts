from langplot import LangPlot
from langplot import PlotterFactory
from coingecko_api import get_coin_ids_list
from webdrive_llm import web_drive_LLM


screenshot_url, webpage_url = web_drive_LLM("let's see the transaction history for vitalik.eth?")
print('succesfully downloaded img at path: ', screenshot_url, 'from source: ', webpage_url)

# get_coin_ids_list()
factory = PlotterFactory("Show me a pie chart of volume of eth and bitcoin over last 30 days")
plotter = factory.create_plotter()
# plotter.plot(theme='plotly_dark')


