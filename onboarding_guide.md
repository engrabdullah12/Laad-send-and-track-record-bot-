# How to Setup and Run the Bot (Onboarding Guide for Other Users)

If you are a new developer or running this bot on a new system, follow this guide to set up and run the bot successfully.

---

## 1. Prerequisites
Before setting up the project, make sure you have the following installed on your machine:
*   [Python 3.12](https://www.python.org/downloads/) (Make sure to check **"Add Python to PATH"** during installation).
*   [Google Chrome Browser](https://www.google.com/chrome/).
*   [Git](https://git-scm.com/).
*   [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) (Only required if you want to generate PDF reports locally).

---

## 2. Step-by-Step Installation

### Step A: Clone the Repository
Clone the code from GitHub to your local folder:
```bash
git clone https://github.com/engrabdullah12/Laad-send-and-track-record-bot-.git
cd Laad-send-and-track-record-bot-
```

### Step B: Create a Virtual Environment
Initialize a fresh virtual environment inside the project folder:
```bash
python -m venv venv
```

### Step C: Activate the Environment & Install Packages
*   **On Windows (PowerShell)**:
    ```powershell
    .\venv\Scripts\Activate.ps1
    ```
*   **On Windows (Command Prompt)**:
    ```cmd
    .\venv\Scripts\activate.bat
    ```
*   **On Mac/Linux**:
    ```bash
    source venv/bin/activate
    ```

Once activated, install the required packages:
```bash
pip install -r requirements.txt
```

---

## 3. Configuration Check (`config.ini`)
Open the `config.ini` file in the root directory to verify scheduler or proxy settings:
```ini
[proxy]
enabled = false  # Set to true if you are using proxy
host = us.res.geonix.com
port = 10315
username = YOUR_USERNAME
password = YOUR_PASSWORD
scheme = http

[scheduler]
interval_minutes = 60
max_jitter_minutes = 0
run_once = false
```

---

## 4. Run the Tests
To run the automated tests on your machine, always run them through the Python execution module in the activated environment to avoid path policy errors:

```bash
.\venv\Scripts\python.exe -m pytest -v
```

---

## 5. Troubleshooting (Windows AppLocker / Driver Errors)
If you are running on a secure corporate computer where execution of external binaries is blocked by policies:
1. Open driver.py (line 22) and driver_factory.py (line 125).
2. Change the `executable_path` username in the path string (e.g. change `ic` to your Windows account username):
   ```python
   service = Service(executable_path=r"C:\Users\YOUR_USERNAME\AppData\Local\Programs\Python\Python312\Scripts\chromedriver.exe")
   ```
3. If you do not have any security blocks, you can simply remove the `service=service` argument from `webdriver.Chrome(...)` and let Selenium launch Chrome normally.
