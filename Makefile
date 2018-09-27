
c: cli
cli:
	python cli.py 1 16 -i default -t "Timeline complète de Reflets d'Acide" -m -io
	$(MAKE) show
cli-main:
	python cli.py 1 16 -r default -t "Timeline des personnages principaux de Reflets d'Acide" -m -io
	$(MAKE) show
cli-short:
	python cli.py 1 12 -r énoriel zarakai zehirmann trichelieu wrandrall roger alia -t "Timeline simplifiée de Reflets d'Acide" -m -io
	$(MAKE) show
cli-test:
	python cli.py 1 4 -r default -m -io
	$(MAKE) show

b: build
build:
	python build_sankey.py
	$(MAKE) show

extract:
	python extract_data.py

poc:
	python poc_sankey.py

retrieve-rda-data:
	git clone https://github.com/Neamar/sagas-mp3.git


show:
	xdg-open temp-plot.html


t: test
test:
	python -m pytest *.py --ignore=venv --doctest-module -vv


.PHONY: c cli b build extract poc t test show
