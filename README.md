# MIS2001 Flask Project

A minimal Flask web application template for MIS2001 coursework.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Setup

1. **Activate the virtual environment:**
   ```powershell
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   
   # Or use the Python directly:
   .\.venv\Scripts\python.exe -m flask run
   ```

2. **Install dependencies (already done):**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   flask run
   ```

4. **Open your browser:**
   Navigate to `http://127.0.0.1:5000`

## 📁 Project Structure

```
flask_project/
├── .venv/              # Virtual environment
├── static/             # CSS, JavaScript, images
│   └── style.css
├── templates/          # Jinja2 HTML templates
│   └── index.html
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (don't commit!)
└── README.md           # This file
```

## 🛠️ Available Commands

| Command | Description |
|---------|-------------|
| `flask run` | Start the development server |
| `flask shell` | Open interactive Python shell with app context |
| `pip freeze > requirements.txt` | Update requirements file |

## 📚 Key Features

- **Flask** - Lightweight web framework
- **Flask-SQLAlchemy** - Database ORM integration
- **Jinja2** - Templating engine
- **python-dotenv** - Environment variable management
- **requests** - HTTP library for API calls

## 🔧 Configuration

Edit the `.env` file to customize:
- `SECRET_KEY` - Application secret key
- `DATABASE_URL` - Database connection string
- `FLASK_DEBUG` - Enable/disable debug mode

## 📖 Next Steps

1. Add more routes in `app.py`
2. Create additional templates in `templates/`
3. Add static files (CSS, JS) in `static/`
4. Define database models in `app.py` or separate `models.py`
5. Implement forms using Flask-WTF (install separately)

## 📝 License

This project is for educational purposes (MIS2001).
