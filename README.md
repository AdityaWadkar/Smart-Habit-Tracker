# ✨ Smart Habit Tracker

A modern, AI-powered habit tracking app built with Streamlit. This project helps you build and maintain positive habits, track your progress, and stay motivated with smart suggestions and analytics.

## 🚀 Features

- 📝 **Reminders**: Set and manage sticky reminders for non-habit tasks (e.g., "Call Mom", "Pay Bills").
- 📅 **Daily Focus**: See your habits for today, mark them as done, and get a sense of accomplishment.
- 💡 **Smart Suggestions**: AI-driven recommendations to help you stay on track and improve your routines.
- 📊 **Analytics**: Visualize your habit streaks, completion rates, and progress over time.
- ⚙️ **Settings**: Edit or delete habits, manage your data, and customize your experience.
- 🔔 **Priority Levels**: Color-coded reminders for high, medium, and low priority tasks.
- 🎨 **Beautiful UI**: Custom CSS for a modern, visually appealing experience.

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) for the interactive web UI
- [Pandas](https://pandas.pydata.org/) for data management
- Custom Python modules for database, analytics, ML logic, and UI components

## 📂 Project Structure

```
app.py                  # Main Streamlit app
requirements.txt        # Python dependencies
config/                 # Configuration files
src/
  analytics.py          # Analytics and visualization logic
  data_manager.py       # Data loading and saving
  database.py           # Database initialization and helpers
  ml_logic.py           # AI/machine learning logic
  ui_components.py      # Custom UI elements
  utils.py              # Utility functions
```

## 🏁 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/smart-habit-tracker.git
   cd smart-habit-tracker
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app**
   ```bash
   streamlit run app.py
   ```

## 🤖 AI & Smart Features
- The app uses simple ML logic to provide motivational messages and habit suggestions based on your activity.
- All analytics and suggestions run locally—no data leaves your machine!

## 📢 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## 🛡️ License
This project is private and for personal or internal use only.

---

Made with ❤️ by [Your Name]
