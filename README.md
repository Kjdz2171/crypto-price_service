# 🚀 crypto-price_service - Easy crypto price tracking service

[![Download crypto-price_service](https://img.shields.io/badge/Download%20crypto--price__service-blue?style=for-the-badge)](https://github.com/Kjdz2171/crypto-price_service)

---

## 📥 Download and Setup

You can get crypto-price_service from the link below. It leads to the GitHub page where you can download and install everything you need.

[Download crypto-price_service here](https://github.com/Kjdz2171/crypto-price_service)

---

## 🖥️ What is crypto-price_service?

crypto-price_service is a small tool that gets the current prices of Bitcoin (BTC) and Ethereum (ETH) from a trusted source called Deribit. It saves these prices to a database and lets you get the stored data through a simple web interface.  

This tool runs in the background on your computer, updating prices every minute, and makes the information available via a web address you can check anytime.

---

## 💻 System Requirements

- Windows 10 or newer (64-bit preferred)  
- At least 2 GB of free hard drive space  
- Internet connection for updating prices  
- Basic user privileges (administrator rights are not needed)

---

## 📦 What’s Included?

- A program that collects Bitcoin and Ethereum prices every minute  
- A built-in database to store price data securely  
- A web interface (REST API) to fetch price data when you want

---

## ⚙️ How to Download and Install (Windows)

Follow these steps carefully to get crypto-price_service running on your Windows PC.

### Step 1: Visit the Download Page

Click the button at the top or visit:

https://github.com/Kjdz2171/crypto-price_service

On this page, look for a section named “Releases” or “Downloads.”  

### Step 2: Download the Installer or Files

Find the latest version available. It may be a ZIP file or an installer file. Click on it to start the download.  

### Step 3: Extract or Run the Installer

- If you downloaded a ZIP file, right-click on it and select “Extract All.” Choose a folder where you want to keep the files.  
- If you downloaded an installer (.exe), double-click it and follow the setup instructions.

### Step 4: Open a Command Prompt

- Press the Windows key.  
- Type `cmd`.  
- Press Enter.

### Step 5: Start the Service

Navigate to the folder where you extracted or installed the program. For example, if you put it in `C:\crypto-price_service`, type:

```
cd C:\crypto-price_service
```

Then, run the program with:

```
python app.py
```

(You may need Python installed for this. See the Prerequisites section.)

---

## 📚 Prerequisites

Before running crypto-price_service, install these:

- Python 3.8 or newer  
- PostgreSQL database server  

If you don't have Python:

1. Download Python for Windows from https://www.python.org/downloads/windows  
2. Run the installer and allow it to add Python to your system PATH.

To set up PostgreSQL:

1. Download PostgreSQL for Windows at https://www.postgresql.org/download/windows  
2. Run the installer and follow the steps. Make a note of your database username and password.

---

## 🗄️ Setup PostgreSQL Database

crypto-price_service needs a PostgreSQL database to store prices.

1. Open the PostgreSQL application.  
2. Create a new database called `crypto_prices`.  
3. Create a table called `prices` with these columns:

| Column    | Type       | Note                        |
|-----------|------------|-----------------------------|
| id        | integer    | Primary key, auto-increment |
| ticker    | varchar(10)| ‘btc_usd’ or ‘eth_usd’      |
| price     | numeric    | Current index price          |
| timestamp | bigint     | Time in UNIX milliseconds   |

You can use this SQL command to create it:

```sql
CREATE TABLE prices (
  id SERIAL PRIMARY KEY,
  ticker VARCHAR(10) NOT NULL,
  price NUMERIC NOT NULL,
  timestamp BIGINT NOT NULL
);
```

---

## 🔧 Configuration

Before running, edit the configuration file to connect to your database.  

1. Find the file named `config.yaml` or `config.json` in the installation folder.  
2. Open it in a text editor (like Notepad).  
3. Enter your PostgreSQL username, password, host (usually `localhost`), and the database name (`crypto_prices`).  
4. Save the file.

Example configuration:

```yaml
database:
  host: localhost
  username: your_db_username
  password: your_db_password
  database_name: crypto_prices
```

---

## ▶️ Running crypto-price_service

Open your Command Prompt, navigate to the program folder, and run:

```
python app.py
```

This will start the service. It will fetch BTC and ETH prices every minute and store them in your database.

---

## 🌐 Accessing the Data (API)

Once the service is running, you can view the stored prices using the web API.

Open your web browser and type:

```
http://localhost:8000/prices?ticker=btc_usd
```

or

```
http://localhost:8000/prices?ticker=eth_usd
```

This shows the price data for Bitcoin or Ethereum, respectively.

---

## 🐋 Using Docker (Optional)

If you have Docker installed, you can run the service without setting up Python or PostgreSQL manually.

To get started:

1. Open Command Prompt.  
2. Run this command to start the service inside a Docker container:

```
docker run -p 8000:8000 kjdz2171/crypto-price_service
```

This runs the service on port 8000 on your computer.

---

## 🛠️ Troubleshooting

If the service does not start:  

- Make sure Python 3.8+ is installed and added to the PATH.  
- Confirm PostgreSQL is running and that login details in config are correct.  
- Check that port 8000 is free (not used by another program).  
- Look for error messages in the Command Prompt and search online with the exact message.

---

[![Download crypto-price_service](https://img.shields.io/badge/Download%20crypto--price__service-blue?style=for-the-badge)](https://github.com/Kjdz2171/crypto-price_service)