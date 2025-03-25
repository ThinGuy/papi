#!/bin/bash
docker build -t repo-size-estimator .
docker run -p 5000:5000 repo-size-estimator
