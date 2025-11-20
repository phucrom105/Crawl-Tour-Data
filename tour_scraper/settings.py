BOT_NAME = "tour_scraper"

SPIDER_MODULES = ["tour_scraper.spiders"]
NEWSPIDER_MODULE = "tour_scraper.spiders"

# Crawl responsibly
ROBOTSTXT_OBEY = False
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 2

# Enable pipelines
ITEM_PIPELINES = {
    "tour_scraper.pipelines.TourScraperPipeline": 300,
}

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Log settings
LOG_LEVEL = 'INFO'

FEEDS = {
    'tours_miennam.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'indent': 4,
    },
}
