from waitress import serve
from app import app
import config

# ipv6支持
serve(app, host='::', port=config.PORT)