# Trust The ChatBot

## Install
Clone the repository and the necessary submodules
```
git clone https://github.com/Tupryk/TrustTheChatBot
cd TrustTheChatBot
git submodule init
git submodule update
```
Install the necessary dependencies
```
pip install -r requirements.txt
```

## Test Run
If you have a GPU you can test inference directly on an LLM by running
```
python3 main.py
```
Otherwise you can directly run a BBO test script on a pre-existing LLM output
```
python3 tests/bbo_test.py
```
