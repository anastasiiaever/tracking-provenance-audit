"""Put the released packages on the import path for pytest."""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in ("src", "scripts", os.path.join("other-work", "src"),
           os.path.join("other-work", "scripts"),
           os.path.join("other-work", "tests")):
    sys.path.insert(0, os.path.join(_HERE, _p))
