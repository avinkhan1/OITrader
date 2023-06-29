#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
nohup python src/schedulers/scheduler_under_200m_OI_monitor.py &