# MGU Scraper: Automate Your Exam Result Analysis

This document details MGU Scraper, a tool designed to simplify the process of extracting and analyzing student exam results from Mahatma Gandhi University (MGU).

### What It Does:
- Fetches exam results from the MGU portal asynchronously.
- Presents results in a user-friendly table format.
- Provides sorting options to organize data.
- Features charts for visualizing data.
- Allows downloading results as a CSV file for further analysis.

### Important Note
- This tool is intended for educational purposes only.
- The data scraped belongs to MGU and should not be used without their permission. Respecting data ownership and ethical standards is crucial.

The objective of this tool is to help teachers assess their students' exam results easily.

## Getting Started:
1. **Clone the Repository:**
   ```bash
    git clone https://github.com/shonebinu/MGUScraper.git && cd MGUScraper
   ```
2. **Install Required Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    This command installs the necessary Python libraries the program relies on.
3. **Run the App:**
    ```bash
    streamlit run src/app.py
    ```
    This launches the MGU Scraper interface in your default web browser.

### Using MGU Scraper:
1. Select the desired exam from the available options.
2. Enter the starting and ending register numbers of the students you want results for.
3. Click "Run Scraping" to initiate the process. The tool retrieves and displays the results.

### Production Deployment
This section outlines optional steps for deploying the app in a production environment (server):
1. **Run with Authentication:**
    ```bash
    streamlit run src/authenticate.py
    ```
    This option involves user authentication for secure access.
2. **Configure Users:**
    - Copy `config.yml.example` to `config.yml` and define user accounts following the provided format in the file. 
      - Hash user passwords using the provided program:
        ```bash
        python src/utils/hash_password.py "password1" "password2"
        ```
3. **Docker Deployment:**
    - Run `docker-compose up` to deploy the app using Docker containers.
    - The app will be accessible on port 80 by default. Modify `docker-compose.yml` to change the port if needed.
  
## License:
MGU Scraper is licensed under the [GNU General Public License v3 (GPL-3)](LICENSE).

