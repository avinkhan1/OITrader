#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
nohup python src/schedulers/scheduler_btc_funding_monitor.py &