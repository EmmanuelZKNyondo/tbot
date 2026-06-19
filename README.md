# TBot v2.0

### Dependencies (Windows)
- Python Install Manager
- Python 3.12
- MetaTrader 5 Desktop Application

### SETUP (on Windows Environment)
1. Clone project from `git.github.`
2. Use python 3.12 
3. create python environment with python version 3.12.* `py -3.12 -m venv venv`
4. activate python use `.venv\Scripts\Activate`
    - Just to confirm that you have the environment set with Python 3.12*, run `python --version` while in the active virtual environment
5. Upgrade pip by running `python -m pip install --upgrade pip`    
6. Install requirements/dependencies with `pip install -r requirements.txt`
    - MT5
    - numpy
    - pandas
    - python_dotenv
    - pytz
    - tzdata
    - and others 

7. update `config/settings.json` and `.env ` to meet your account, broker details as well as trading parameters 


### Developer Understanding
Flow of the application 

    main_test.py
      ↓
    MarketLoop (scheduler)
      ↓
    TradeOrchestrator (brain pipeline)
      ↓
    ExecutionRouter (MT5 or dry-run)


    execution mode: test | mt5_direct | mt5_bridge