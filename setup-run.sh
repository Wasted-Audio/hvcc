# I don't know when it is necessary, but have seen cases where
# toxx was not running the latest code for hvcc. 

# to install hvcc
pip install -e .

# to force tox to rebuild (this seems to work, but is slower)
toxx -r PD_FILE



# to get your shell into a tox-like environment, just
.tox/py39/bin/activate


