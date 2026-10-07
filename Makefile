# Author: Emmanuel COLUSSI
.PHONY: check test

check:
	bash -n flasher.sh scripts/common.sh scripts/install-citool.sh
	python3 -m unittest discover -s tests -v

test: check
