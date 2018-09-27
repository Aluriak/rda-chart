
c: cli
cli:
	python cli.py 1 16 -i default -t "Timeline complète de Reflet d'Acide"
	$(MAKE) show
cli-simple:
	python cli.py 1 12 -r énoriel zarakai zehirmann trichelieu wrandrall narrateur roger dragonne kyo -t "Timeline simplifiée de Reflet d'Acide"
	$(MAKE) show

b: build
build:
	python build_sankey.py
	$(MAKE) show

extract:
	python extract_data.py

poc:
	python poc_sankey.py


show:
	xdg-open temp-plot.html


t: test
test:
	python -m pytest *.py --ignore=venv --doctest-module -vv


.PHONY: c cli b build extract poc t test show
