#!/usr/bin/env bash

USR=$(id -u)
GRP=$(id -g)

docker run --rm -it --volume $PWD/.:/parmesan --user ${USR}:${GRP} cppyy bash
