from shorthand.utils.config import CONFIG_FILE_LOCATION
from shorthand.web.app import create_app


default_app = create_app(CONFIG_FILE_LOCATION)
