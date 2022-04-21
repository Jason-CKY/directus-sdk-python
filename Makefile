
lint:
	docker run --rm -v $(PWD):/src:Z \
	--workdir=/src odinuge/yapf:latest yapf \
	--style '{based_on_style: pep8, dedent_closing_brackets: true, coalesce_brackets: true}' \
	--no-local-style --verbose --recursive --diff --parallel directus

format:
	docker run --rm -v $(PWD):/src:Z \
	--workdir=/src odinuge/yapf:latest yapf \
	--style '{based_on_style: pep8, dedent_closing_brackets: true, coalesce_brackets: true}' \
	--no-local-style --verbose --recursive --in-place --parallel directus

pyflakes:
	docker run --rm -v $(PWD):/src:Z \
	--workdir=/src python:3.8 \
	/bin/bash -c "pip install --upgrade pyflakes && python -m pyflakes /src && echo 'pyflakes passed!'"