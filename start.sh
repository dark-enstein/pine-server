#! /bin/env bash

SILENT="2>/dev/null"

start_app(){
 python -m uvicorn main:app --port 80 --reload
}


install_deps(){
sudo apt update $SILENT
sudo apt install python3.11-venv git -y $SILENT
python3 -m venv venv $SILENT
. venv/bin/activate
pip install -r requirements.txt $SILENT
pip install "fastapi[all]"
pip install git+https://github.com/BiomedSciAI/biomed-multi-alignment.git $SILENT
}

#install_deps
start_app
