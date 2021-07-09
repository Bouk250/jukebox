import logging
from colorlog import ColoredFormatter, StreamHandler, getLogger, basicConfig

formatter = ColoredFormatter(
	"%(log_color)s[%(asctime)s - %(levelname)-6s]%(reset)s - %(message)s",
	datefmt='%Y/%m/%d %H:%M:%S',
	log_colors={
		'DEBUG':    'cyan',
		'INFO':     'green',
		'WARNING':  'yellow',
		'ERROR':    'red',
		'CRITICAL': 'red,bg_white',
	},
	secondary_log_colors={},
	style='%'
)

handler = StreamHandler()
handler.setFormatter(formatter)

logger = getLogger('JukeBoxLogger')
logger.addHandler(handler)
logger.setLevel(logging.INFO)