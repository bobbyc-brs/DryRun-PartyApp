# 🍻 Vision Document: Party Drink Tracker
Copyright (C) 2025 Brighter Sight
This program is free software under GPL v3

## 1. **Project Overview**
The **Party Drink Tracker** is a lightweight, web-accessible application designed to monitor and visualize alcohol consumption at social gatherings. Guests can log their drinks in real time, while the host can view aggregated data and estimated blood alcohol levels (BAC) for each participant. The app aims to promote awareness, safety, and a touch of fun through intuitive design and visual feedback.

## 2. **Goals**
- ✅ Provide an easy-to-use interface for guests to register drinks
- 📊 Enable hosts to monitor consumption and view BAC graphs
- 🖼️ Use drink images for intuitive selection
- 🔐 Ensure data is isolated per guest and securely stored
- 🧪 Run in a Python 3 virtual environment for clean deployment

## 3. **Target Users**
- **Guests**: Individuals attending the party who want to log their drinks
- **Host**: The organizer who monitors overall consumption and BAC estimates

## 4. **Key Features**
### Guest Interface (`<ip-address>:4000`)
- Grid of guest names (from `~/guest-list`)
- Input field for guest weight (lbs)
- Clickable drink images (from `~/drinks`)
- Drink metadata (volume, ABV) sourced from `~/drinks/drink-list.csv`
- Real-time logging of drink selections

### Host Interface (`<ip-address>:4001`)
- Dashboard showing total drinks per guest
- Estimated BAC graph per guest (based on weight, drink history, and time)
- Option to toggle between individual and group views

## 5. **Data Sources**
| Source File                  | Purpose                                  |
|-----------------------------|------------------------------------------|
| `~/guest-list`              | List of guests displayed in UI           |
| `~/drinks/drink-list.csv`   | Drink metadata: name, volume, ABV        |
| `~/drinks/`                 | Drink images used for selection buttons  |

## 6. **Technical Stack**
- **Language**: Python 3
- **Environment**: Virtual environment (`venv`) for isolation
- **Framework**: Flask or FastAPI for web routing
- **Frontend**: HTML/CSS/JS (possibly with Bootstrap for layout)
- **Data Storage**: In-memory or lightweight DB (e.g., SQLite)
- **Graphing**: Matplotlib or Plotly for BAC visualization

## 7. **Success Criteria**
- Guests can register drinks with minimal friction
- Host can view accurate BAC approximations
- App runs reliably in a virtual environment
- Interfaces are responsive and intuitive

## 8. **Assumptions**
- Guests will honestly input their weight and drink selections
- BAC estimates are for entertainment and awareness, not medical accuracy
- The app will be hosted on a local network (not exposed to the internet)

## 9. **Out of Scope**
- Mobile app version
- Real-time syncing across multiple devices
- Integration with external health APIs
