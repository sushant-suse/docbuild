#
try:
    get_ipython().run_line_magic("load_ext", "autoreload")
    get_ipython().run_line_magic("autoreload", "-p", "1")
    print(" Automatically enabled autoreload")
except Exception:
    pass  # Not running inside IPython
