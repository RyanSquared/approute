.PHONY: build clean install

build:
	poetry build

clean:
	poetry clean

install: build
	find dist -name '*whl' -exec pip3 install --user {} \;
