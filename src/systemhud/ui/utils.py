import os

IS_TERMINAL = os.environ.get("TERM") not in {"linux", None}
