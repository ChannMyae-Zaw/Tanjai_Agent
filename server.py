import os
import sys

# Make sure tanjai_project is findable
sys.path.insert(0, os.path.dirname(__file__))

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/etc/secrets/credentials.json"

from google.adk.cli.fast_api import get_fast_api_app

app = get_fast_api_app(
    agents_dir=os.path.join(os.path.dirname(__file__)),
    web=True,
)