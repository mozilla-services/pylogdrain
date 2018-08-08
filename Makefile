all: local_build

check_venv:
ifeq ($(VIRTUAL_ENV),)
	$(error "Run from a virtualenv (try 'make install && source venv/bin/activate')")
endif

black: check_venv
	black --check $(shell git ls-files | grep \.py$$)

build:
	(cd ${VIRTUAL_ENV}/lib/python3.6/site-packages && zip -r9 ${VIRTUAL_ENV}/../pylogdrain.zip .)
	zip -g pylogdrain.zip *.py

docker_build: install build
local_build: clean install check_venv build

clean:
	rm -f pylogdrain.zip

dev_install: install
	( . venv/bin/activate && pip install -r dev-requirements.txt )

install: venv
	( . venv/bin/activate && pip install -U pip && pip install -r requirements.txt )

# Package lambda function in zip file
package:
	docker run -i --rm -v `pwd`:/pylogdrain -e VIRTUAL_ENV='/pylogdrain/venv' \
		python:3.6 \
		/bin/bash -c 'apt-get update && apt-get install -y zip && cd /pylogdrain && make docker_build'

test: check_venv
	pytest tests/test_*.py

venv:
	python3 -m venv venv

.PHONY:
	all \
	black \
	check_venv \
	clean \
	dev_install \
	install \
	test \
	venv
