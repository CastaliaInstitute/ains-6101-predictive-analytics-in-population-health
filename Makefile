html:
	jupyter-book build .

site: html
	bash scripts/stage-github-pages.sh

pdf:
	jupyter-book build . --builder pdflatex

epub:
	jupyter-book build . --builder epub

all: html pdf epub
