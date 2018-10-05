# General variables
OUTPUT_FILE=out.html

# CLI options
OUTPUT_FILE_ARG=-o $(OUTPUT_FILE)
IOCHAPTERS=-io
MERGE=-m
OPTIONS=$(MERGE) $(IOCHAPTERS) $(OUTPUT_FILE_ARG)


# CLI recipees
c: cli
cli:
	python cli.py 1 16 -i default -t "Timeline complète de Reflets d'Acide" $(OPTIONS)
	$(MAKE) show
cli-with-narrateur:
	python cli.py 1 16 -i default ^narrateur -t "Timeline complète de Reflets d'Acide (avec le Narrateur)" $(OPTIONS)
	$(MAKE) show
cli-main:
	python cli.py 1 16 -r default -t "Timeline des personnages principaux de Reflets d'Acide" $(OPTIONS)
	$(MAKE) show
cli-short:
	python cli.py 1 12 -r énoriel zarakai zehirmann trichelieu wrandrall roger alia -t "Timeline simplifiée de Reflets d'Acide" $(OPTIONS)
	$(MAKE) show
cli-png:
	python cli.py 1 6 -i none $(OPTIONS) -t "Timeline des 6 premiers épisodes de Reflets d'Acide" -p -w 4000
	$(MAKE) show
cli-test:
	python cli.py 1 6 -i none $(OPTIONS) -t "Timeline des 6 premiers épisodes de Reflets d'Acide"
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
	xdg-open $(OUTPUT_FILE)


t: test
test:
	python -m pytest *.py --ignore=venv --doctest-module -vv


.PHONY: c cli b build extract poc t test show
