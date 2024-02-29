ECHO OFF
ECHO Activating virtual environment
mma_nlp\Scripts\activate.bat
ECHO Scraping Script
python processing\scraper.py
ECHO Parsing Script
python processing\parser.py
ECHO Performing Sentiment Analysis
python sentiment_analysis\sentiment_analysis.py
exit