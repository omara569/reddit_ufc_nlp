ECHO OFF
ECHO Scraping Script
python processing\scraper.py
ECHO Parsing Script
python processing\parser.py
ECHO Performing Sentiment Analysis
python sentiment_analysis\sentiment_analysis.py