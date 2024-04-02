LinkedIn Paraphrase  Post

Project Workflow:

![Image Description](https://drive.google.com/uc?id=1derJb-568KMp-DzC-8L35Y3BsLNuVdwD)


VideoLink:

[Watch the full video here](https://drive.google.com/uc?id=1UgoUs_0I0e_2uJ8gwSa40aXkMH36Kvtd)


Files:

* app.py - FastAPI
* main.py streamlit app

How to use it:

* Create environment with python==3.10
Install Dependencies:
pip install -r requirements.txt 

If pyperclip error occured, install package as:
sudo apt-get install xclip

To run the files:

1. uvicorn app:app --reload   (FastAPI), It accepts the content in json format {'url':'link'}
2. streamlit run main.py

