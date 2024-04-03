import runpy
import sys

sys.argv = ["streamlit", "run", "homepage.py"]
runpy.run_module("streamlit", run_name="__main__")
