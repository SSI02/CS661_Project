# 🌍 Climate Change Dashboard

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)  
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)  
[![Dash](https://img.shields.io/badge/dash-2.x-orange.svg)](https://dash.plotly.com/)  

An interactive, data-driven dashboard built with **Plotly Dash**, visualizing key climate indicators:
- **Global Temperature Trends**
- **CO₂ Emissions by Country**
- **Sea Level Rise**
- **Correlation Analysis** between temperature, emissions, and sea level

---

## 🚀 Features

- **Modular Pages**
  - `/temperature` – animated choropleth & bar charts
  - `/emissions` – top-10 emitters by year
  - `/sea_level` – historical trends, seasonal patterns, projections
  - `/correlation` – time series, correlation matrix, scatter, dashboard view

- **Interactive Controls**
  - Year slider with play/pause animation
  - Tabs & dropdowns for choosing chart types and regions
  - Range sliders for filtering date spans

- **Insights Panels**
  Automated text summaries highlighting key statistics (e.g., hottest country, rate of change).

- **Responsive Design**
  Styled with Bootstrap and Poppins font, mobile-friendly layout, custom color themes.

---

## 📦 Tech Stack

- **Python 3.8+**
- **Dash & Plotly** for interactive visualizations
- **Dash Bootstrap Components** for UI
- **Pandas**, **NumPy**, **SciPy** for data processing
- **Gunicorn** web server (for production)

---

## 📁 Project Structure

```
├── index.py              # App entrypoint & router
├── pages/
│   ├── homepage.py
│   ├── temperature.py
│   ├── emissions.py
│   ├── sea_level.py
│   └── correlation.py
├── assets/style.css
├── requirements.txt
└── README.md
```

---

## 🔧 Installation & Local Run

1. **Clone the repo**  
   ```bash
   git clone https://github.com/SSI02/CS661_Project.git
   cd CS661_Project
   ```

2. **Create a virtual environment** (optional but recommended)  
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Linux/macOS
   venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**  
   ```bash
   python index.py
   ```
   Then open `http://127.0.0.1:8050` in your browser.

---

## 🌐 Live Demo

Access the deployed dashboard here:  
https://climate-dashboard-ybix.onrender.com/

---

## 👩‍💻 Contributing

1. Fork the repo  
2. Create a feature branch: `git checkout -b feature/foo`  
3. Commit changes: `git commit -m 'Add foo feature'`  
4. Push to branch: `git push origin feature/foo`  
5. Open a Pull Request

Please follow the existing code style, add tests if applicable, and keep assets under 100 MB per file.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).


Project Link: https://github.com/SSI02/CS661_Project  

