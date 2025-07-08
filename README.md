# ⛽ Fuel Per Kilometer Analysis

A data science project that analyzes and visualizes fuel efficiency of vehicles based on real-world data. It helps identify cars that offer the **best mileage per kilometer**, using machine learning techniques like **linear regression** and **data filtering**.

---

## 📊 Overview

This project:
- Loads a dataset of over **1000 car entries**
- Explores relationships between **mileage**, **fuel tank capacity**, and **distance covered**
- Applies **regression models** to predict fuel efficiency
- Provides **visual insights** on the most fuel-efficient vehicles

---

## 🛠️ Tech Stack

| Language | Libraries             | Tools                       |
|----------|-----------------------|-----------------------------|
| Python   | pandas, numpy         | Jupyter Notebook ('.ipynb') |
|          | matplotlib, seaborn   | scikit-learn (for regression) |

---

## 📁 Folder Structure

Fuel-Per-Kilometer-Analysis/
├── data/
│   └── car_fuel_data.csv        # Dataset used
├── notebooks/
│   └── FuelAnalysis.ipynb       # Jupyter notebook with EDA + ML
├── screenshots/
│   └── correlation_plot.png
│   └── regression_result.png
├── README.md

🚀 How to Run
1. Clone the Repository
bash
Copy
Edit
git clone https://github.com/RitzwiK/Fuel-Per-Kilometer-Analysis.git
cd Fuel-Per-Kilometer-Analysis
2. Create a Virtual Environment (Recommended)
bash
Copy
Edit
python -m venv venv
Then activate it:

On Windows:

bash
Copy
Edit
venv\Scripts\activate
On macOS/Linux:

bash
Copy
Edit
source venv/bin/activate
3. Install Required Packages
If you have a requirements.txt:

bash
Copy
Edit
pip install -r requirements.txt
If not yet created, install manually:

bash
Copy
Edit
pip install pandas numpy matplotlib seaborn scikit-learn
4. Launch Jupyter Notebook
bash
Copy
Edit
jupyter notebook
Then open:

Copy
Edit
notebooks/FuelAnalysis.ipynb

## 📷 Screenshots
<p align="center"> <img src="screenshots/correlation_plot.png" alt="Correlation Plot" width="500"/> <br> <img src="screenshots/regression_result.png" alt="Regression Line" width="500"/> </p>
## 📌 Features
🔍 Exploratory Data Analysis (EDA)

📈 Linear regression to predict fuel efficiency

📊 Mileage vs. Fuel Usage scatter plots

📌 Highlights top fuel-efficient vehicles

📂 Clean modular structure for data + code separation

## 🧠 Future Enhancements
Use real-time API-based fuel data

Build a web dashboard with Streamlit

Add multiple ML models for better prediction

Vehicle clustering using KMeans
