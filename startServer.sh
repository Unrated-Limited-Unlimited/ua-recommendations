#!/bin/bash
#docker stop ua-recommendations
#docker remove ua-recommendations
#docker build -t ua-recommendations .
#docker run --restart=always --network ua-network --name ua-recommendations -e DB_PASSWORD=$1 -p 5000:5000 -d ua-recommendations:latest
source .venv/bin/activate
python pip install -r requirements.txt
cd src
nohup python main.py
