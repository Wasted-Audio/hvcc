# intended for heavy.lang.json and heavy.ir.json, to list out all of the language blocks/commands
alias hlang_blocks="grep '\".*\": {' | sort | uniq | cut -d '\"' -f 2"

# invoke tox with alt config file, 2nd one include test coverage stats
alias toxx="tox -c ~/projects/hvcc/dgb-hvcc/tox.dev.ini"
alias toxc="tox -c ~/projects/hvcc/dgb-hvcc/tox.dev.ini -- --cov-config=tox.ini --cov=hvcc"
