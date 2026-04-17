import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from google.adk.cli.fast_api import get_fast_api_app

app = get_fast_api_app(
    agents_dir=os.path.join(os.path.dirname(__file__), "tanjai_project"),
    web=True,
)