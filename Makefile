.PHONY: dkr-build drill sqlpad

dkr-build:
	docker build -t cppyy:latest .

drill:
	docker run --rm -it --name drill-1.15.0 -p 8047:8047 --volume $(shell PWD)/parquets:/parquets drill/apache-drill:1.15.0 /bin/bash

sqlpad:
	docker run --rm --name sqlpad --env-file sqlpad.env -p 3000:3000 sqlpad/sqlpad
