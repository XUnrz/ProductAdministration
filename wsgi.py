from waitress import serve
from app import app
import config

# ipv4和ipv6同时支持
serve(app,port=config.PORT,ipv6=True,ipv4=True)