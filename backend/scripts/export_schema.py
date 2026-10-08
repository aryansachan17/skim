import sys
from pathlib import Path

from app.graphql_schema import schema

Path(sys.argv[1]).write_text(schema.as_str() + "\n")
