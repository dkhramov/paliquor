BOT_NAME = 'paliquor'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['paliquor.spiders']
NEWSPIDER_MODULE = 'paliquor.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

ITEM_PIPELINES = [
    'paliquor.pipelines.PaliquorPipeline',
]

CONCURRENT_REQUESTS_PER_DOMAIN = 1
CONCURRENT_SPIDERS = 1
