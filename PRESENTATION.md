# ExpenseIQ — Smart Expense Tracker
## Project Presentation

---

## 📝 1. Abstract

**ExpenseIQ** is a full-stack personal finance management web application that empowers users to track their income and expenses in real-time, visualize their financial data through interactive charts, and receive AI-powered financial advice. Built using a modern client-server architecture with **Python Flask** on the backend, **MySQL** for persistent storage, and a responsive **HTML/CSS/JavaScript** frontend, the application offers a secure, user-friendly platform for personal budgeting. A standout feature is the integration of **Google Gemini AI**, which acts as a personalized financial advisor — analyzing the user's real financial data to provide actionable spending insights, savings tips, and purchase recommendations.

---

## 📖 2. Introduction

Managing personal finances is a fundamental life skill, yet many individuals struggle with tracking where their money goes. Traditional methods like spreadsheets or pen-and-paper budgets are tedious, error-prone, and lack real-time insights.

**ExpenseIQ** addresses this gap by providing a modern, web-based expense tracking solution that is:
- **Simple to Use** — Intuitive UI with forms for income and expense entry
- **Visually Rich** — Pie charts and line graphs for financial data visualization
- **Secure** — User authentication with bcrypt-hashed passwords
- **AI-Enhanced** — Google Gemini-powered financial advisor that understands the user's spending patterns
- **Responsive** — Works seamlessly across desktops, tablets, and mobile devices

The application follows a **client-server architecture** where the Flask backend serves RESTful APIs consumed by the vanilla JavaScript frontend, with MySQL handling all data persistence.

---

## ❓ 3. Problem Statement

In today's fast-paced world, individuals face several challenges in managing their personal finances:

1. **Lack of Awareness** — Most people do not have a clear picture of their income vs. expenditure ratio, leading to overspending.
2. **No Centralized Tracking** — Income from multiple sources and expenses across various categories are scattered, making it hard to get a consolidated view.
3. **Manual Effort** — Existing solutions like Excel require significant manual effort and are not accessible on-the-go.
4. **No Intelligent Insights** — Traditional trackers only record data but do not provide actionable financial advice based on spending patterns.
5. **Security Concerns** — Storing financial data without proper authentication and encryption exposes sensitive information to risks.
6. **Absence of Visual Analytics** — Without charts and graphs, raw financial data is difficult to interpret at a glance.

### Objective
To design and develop a **secure, intelligent, and visually appealing web application** that allows users to:
- Track income and expenses with categorization
- Visualize financial data through interactive charts
- Receive AI-driven personalized financial advice
- Access the application securely with user authentication

---

## 🎯 4. Solution Domain

ExpenseIQ provides a comprehensive solution through the following modules:

### 4.1 User Authentication Module
- Secure registration & login using email and password
- Passwords hashed using **bcrypt** (industry-standard)
- Session-based authentication with Flask sessions
- Protected API routes using a `login_required` decorator

### 4.2 Income Management Module
- Add income entries with **source**, **amount**, **date**, and **description**
- View complete income history in a tabular format
- Delete income records as needed
- Data stored in MySQL with foreign key relationship to the user

### 4.3 Expense Management Module
- Add expense entries with **category** (Food, Transport, Shopping, Bills, Entertainment, Health, Education, Rent, Other), **amount**, **date**, and **description**
- Pre-defined category selection with emoji icons for easy identification
- View complete expense history and delete entries
- Data stored in MySQL with cascading deletes

### 4.4 Dashboard & Analytics Module
- **Summary Cards** — Total Income, Total Expenses, Current Balance
- **Pie Chart** — Income breakdown by source (using Chart.js)
- **Line Chart** — Expenses trend over time (month-by-month)
- **Recent Transactions** — Last 10 combined income/expense entries

### 4.5 AI Financial Advisor Module
- Chat-based interface powered by **Google Gemini 2.5 Flash**
- AI has access to the user's real financial data (income, expenses, balance)
- Provides personalized advice on:
  - Spending analysis
  - Savings tips
  - Budget planning
  - Purchase affordability assessment
- Quick suggestion chips for common queries

---

## 📐 5. UML Diagrams

### 5.1 Use Case Diagram

```
                    ┌─────────────────────────────────────────────┐
                    │              ExpenseIQ System               │
                    │                                             │
                    │  ┌──────────────────┐                       │
                    │  │    Register       │                       │
           ┌───┐   │  └────────┬─────────┘                       │
           │   │───┼──►┌───────┴──────────┐                       │
           │ U │   │   │     Login        │                       │
           │ s │   │   └────────┬─────────┘                       │
           │ e │   │  ┌────────┴─────────┐                       │
           │ r │───┼──►│  View Dashboard  │                       │
           │   │   │   └────────┬─────────┘                       │
           │   │   │  ┌────────┴─────────┐                       │
           │   │───┼──►│  Manage Income   │                       │
           │   │   │   │  (Add / Delete)  │                       │
           │   │   │   └────────┬─────────┘                       │
           │   │   │  ┌────────┴─────────┐                       │
           │   │───┼──►│ Manage Expenses  │                       │
           │   │   │   │  (Add / Delete)  │                       │
           │   │   │   └────────┬─────────┘                       │
           │   │   │  ┌────────┴─────────┐   ┌────────────────┐  │
           │   │───┼──►│ Chat with AI     │──►│  Gemini API    │  │
           │   │   │   │ Advisor          │   │  (External)    │  │
           └───┘   │   └────────┬─────────┘   └────────────────┘  │
                    │  ┌────────┴─────────┐                       │
                    │  │    Logout        │                       │
                    │  └──────────────────┘                       │
                    └─────────────────────────────────────────────┘
```

### 5.2 Class Diagram (Database Entity Model)
```
┌──────────────────────────────────┐
│            users                 │
├──────────────────────────────────┤
│ + id: INT (PK, AUTO_INCREMENT)  │
│ + username: VARCHAR(50) UNIQUE  │
│ + email: VARCHAR(100) UNIQUE    │
│ + password_hash: VARCHAR(255)   │
│ + created_at: TIMESTAMP         │
├──────────────────────────────────┤
│ + register()                    │
│ + login()                       │
│ + logout()                      │
│ + getProfile()                  │
└──────────┬───────────────────────┘
           │ 1
           │
     ┌─────┴─────┐
     │            │
     │ *          │ *
┌────┴───────────────────────┐    ┌─────────────────────────────────┐
│          income            │    │           expenses              │
├────────────────────────────┤    ├─────────────────────────────────┤
│ + id: INT (PK)             │    │ + id: INT (PK)                  │
│ + user_id: INT (FK)        │    │ + user_id: INT (FK)             │
│ + source: VARCHAR(100)     │    │ + category: VARCHAR(100)        │
│ + amount: DECIMAL(12,2)    │    │ + amount: DECIMAL(12,2)         │
│ + date: DATE               │    │ + date: DATE                    │
│ + description: TEXT        │    │ + description: TEXT              │
│ + created_at: TIMESTAMP    │    │ + created_at: TIMESTAMP         │
├────────────────────────────┤    ├─────────────────────────────────┤
│ + addIncome()              │    │ + addExpense()                  │
│ + getAll()                 │    │ + getAll()                      │
│ + deleteIncome()           │    │ + deleteExpense()               │
└────────────────────────────┘    └─────────────────────────────────┘
```

### 5.3 Sequence Diagram — Add Expense Flow

```
  User (Browser)          Flask Server           MySQL Database         
       │                       │                       │                
       │── POST /api/expenses──►                       │                
       │   {category, amount,  │                       │                
       │    date, description} │                       │                
       │                       │──Check session────────►                
       │                       │◄─user_id found────────│                
       │                       │                       │                
       │                       │──Validate input──     │                
       │                       │                       │                
       │                       │──INSERT INTO ─────────►                
       │                       │  expenses             │                
       │                       │◄─lastrowid────────────│                
       │                       │                       │                
       │◄─ 201 {message, id}──│                       │                
       │                       │                       │                
```

### 5.4 Sequence Diagram — AI Chat Flow

```
  User (Browser)       Flask Server        MySQL Database      Gemini API
       │                    │                    │                  │
       │─ POST /api/chat ──►│                    │                  │
       │  {message}         │                    │                  │
       │                    │─ Fetch income ────►│                  │
       │                    │◄─ income data ────│                  │
       │                    │─ Fetch expenses ──►│                  │
       │                    │◄─ expense data ───│                  │
       │                    │─ Fetch recent ────►│                  │
       │                    │◄─ transactions ───│                  │
       │                    │                    │                  │
       │                    │──Build context + ─────────────────────►
       │                    │  system prompt     │                  │
       │                    │◄─ AI response ───────────────────────│
       │                    │                    │                  │
       │◄─ {reply} ────────│                    │                  │
       │                    │                    │                  │
```

### 5.5 Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                      CLIENT (Browser)                            │
│                                                                  │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐  │
│  │ index.html │ │dashboard   │ │income.html │ │expenses.html │  │
│  │ (Landing)  │ │.html       │ │            │ │              │  │
│  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └──────┬───────┘  │
│        │              │              │               │           │
│  ┌─────┴──────┐ ┌─────┴──────┐ ┌────┴───────┐ ┌─────┴───────┐  │
│  │ auth.js    │ │dashboard.js│ │ income.js  │ │expenses.js  │  │
│  └────────────┘ └────────────┘ └────────────┘ └─────────────┘  │
│                                                                  │
│  ┌────────────┐                 ┌──────────────┐                 │
│  │advisor.html│─────────────────│ advisor.js   │                 │
│  └────────────┘                 └──────────────┘                 │
│                                                                  │
│  ┌──────────────────────────────────────────────┐                │
│  │              styles.css (1278 lines)          │                │
│  │  Dark theme, Glassmorphism, Responsive        │                │
│  └──────────────────────────────────────────────┘                │
│                         │                                        │
│                    Chart.js CDN                                   │
└─────────────────────────┼────────────────────────────────────────┘
                          │  RESTful API (JSON)
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                    SERVER (Flask / Python)                        │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────────┐│
│  │ Auth API    │  │ Income API   │  │ Expenses API             ││
│  │ /api/auth/* │  │ /api/income  │  │ /api/expenses            ││
│  └─────────────┘  └──────────────┘  └──────────────────────────┘│
│                                                                  │
│  ┌─────────────────┐  ┌──────────────────────────────────────┐  │
│  │ Dashboard API   │  │ AI Chat API (/api/chat)              │  │
│  │ /api/dashboard  │  │ → Google Gemini 2.5 Flash            │  │
│  └─────────────────┘  └──────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Middleware: login_required decorator, Session Mgmt       │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────┬────────────────────────────────────────┘
                          │  mysql.connector
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                   DATABASE (MySQL)                                │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                    │
│  │  users   │───►│  income   │    │ expenses │                    │
│  │          │───►│          │    │          │                    │
│  └──────────┘    └──────────┘    └──────────┘                    │
│                                                                  │
│  Database: expense_tracker                                       │
│  Engine: InnoDB (with FK constraints & cascading deletes)        │
└──────────────────────────────────────────────────────────────────┘
```

### 5.6 Data Flow Diagram (Level 0)

```
                ┌──────────┐
                │   User   │
                └────┬─────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
  ┌──────────┐ ┌──────────┐ ┌──────────┐
  │ Login /  │ │ Income & │ │   AI     │
  │ Register │ │ Expense  │ │ Advisor  │
  │          │ │ Data     │ │ Query    │
  └────┬─────┘ └────┬─────┘ └────┬─────┘
       │            │            │
       ▼            ▼            ▼
  ┌─────────────────────────────────────┐
  │         ExpenseIQ System            │
  │  (Authentication, CRUD, Analytics,  │
  │   AI Processing)                    │
  └────────────────┬────────────────────┘
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
  ┌─────────┐ ┌─────────┐ ┌─────────┐
  │Dashboard│ │  Data   │ │   AI    │
  │ Charts  │ │ Tables  │ │ Advice  │
  └─────────┘ └─────────┘ └─────────┘
```

---

## 🔧 6. Methodology

The project follows an **Agile Incremental Development** methodology:

### Phase 1: Requirement Analysis & Planning
- Identified core features: authentication, income/expense tracking, visualization, AI chat
- Selected technology stack based on simplicity, scalability, and availability
- Designed the database schema with three normalized tables

### Phase 2: Database Design
- Created the `expense_tracker` database with three tables:
  - `users` — stores user credentials with bcrypt-hashed passwords
  - `income` — stores income entries linked to users via foreign key
  - `expenses` — stores expense entries with category classification
- Implemented **ON DELETE CASCADE** to maintain referential integrity

### Phase 3: Backend Development
- Developed the Flask server (`app.py` — 483 lines) with modular API sections:
  - **Auth API**: `/api/auth/register`, `/api/auth/login`, `/api/auth/logout`, `/api/auth/me`
  - **Income API**: `GET/POST /api/income`, `DELETE /api/income/<id>`
  - **Expenses API**: `GET/POST /api/expenses`, `DELETE /api/expenses/<id>`
  - **Dashboard API**: `/api/dashboard/summary` (aggregated financial data)
  - **AI Chat API**: `/api/chat` (Gemini-powered financial advisor)
- Implemented authentication middleware using Python decorators
- Created utility functions for database operations and JSON serialization

### Phase 4: Frontend Development
- Built 5 HTML pages with a consistent dark-themed design:
  - **Landing Page** (`index.html`) — Hero section with login/register forms
  - **Dashboard** (`dashboard.html`) — Stats cards, pie chart, line chart, recent transactions
  - **Income Page** (`income.html`) — Add income form + income history table
  - **Expenses Page** (`expenses.html`) — Add expense form with category dropdown + expense history table
  - **AI Advisor** (`advisor.html`) — Chat interface with suggestion chips
- Developed 5 JavaScript files for client-side logic and API integration
- Created a comprehensive CSS design system (1278 lines) with:
  - Dark theme with glassmorphism effects
  - CSS custom properties for consistent theming
  - Responsive design with media queries
  - Smooth transitions and animations

### Phase 5: AI Integration
- Integrated Google Gemini 2.5 Flash model via the `google-generativeai` Python SDK
- Built a context-aware system prompt that includes the user's real financial data
- Implemented error handling for API quota limits and failures

### Phase 6: Testing & Deployment
- Tested all CRUD operations for income and expenses
- Verified authentication flow (register → login → session → logout)
- Validated chart rendering with dynamic data
- Tested AI advisor with various financial queries

---

## 🛠️ 7. Tools and Technologies Used

### Backend
| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.x | Server-side programming language |
| **Flask** | 3.1.0 | Lightweight web framework for REST APIs |
| **MySQL** | 8.x | Relational database for data persistence |
| **mysql-connector-python** | 9.2.0 | Python connector for MySQL database |
| **bcrypt** | 4.3.0 | Password hashing and verification |
| **python-dotenv** | 1.1.0 | Environment variable management |
| **google-generativeai** | 0.8.5 | Google Gemini AI SDK for financial advisor |

### Frontend
| Technology | Purpose |
|---|---|
| **HTML5** | Page structure and semantic markup |
| **CSS3** | Styling with dark theme, glassmorphism, animations |
| **Vanilla JavaScript** | Client-side logic, API calls (Fetch API), DOM manipulation |
| **Chart.js** | 4.4.7 | Interactive pie and line chart rendering |

### Development Tools
| Tool | Purpose |
|---|---|
| **VS Code** | Code editor / IDE |
| **Git** | Version control |
| **Postman / Browser DevTools** | API testing and debugging |
| **MySQL Workbench / CLI** | Database management |

### Architecture & Design Patterns
| Pattern | Usage |
|---|---|
| **Client-Server Architecture** | Frontend communicates with backend via REST APIs |
| **MVC Pattern** | Model (MySQL), View (HTML/CSS), Controller (Flask routes) |
| **RESTful API Design** | Standard HTTP methods (GET, POST, DELETE) with JSON payloads |
| **Decorator Pattern** | `@login_required` middleware for route protection |
| **Environment-based Configuration** | Sensitive credentials stored in `.env` file |

---

## 📊 8. Results

The ExpenseIQ application successfully achieves the following outcomes:

### 8.1 User Authentication
- ✅ Users can **register** with username, email, and password
- ✅ Passwords are securely **hashed using bcrypt** before storage
- ✅ Users can **login** with email and password
- ✅ Session-based authentication protects all dashboard routes
- ✅ Unauthorized API access returns **401 Unauthorized** response

### 8.2 Income & Expense Management
- ✅ Users can **add income** entries with source, amount, date, and description
- ✅ Users can **add expense** entries with category selection (9 categories), amount, date, and description
- ✅ Both income and expense tables display **complete history** sorted by date
- ✅ Users can **delete** individual entries with instant UI updates
- ✅ Form validation prevents submission of incomplete data

### 8.3 Dashboard & Visualization
- ✅ **Summary cards** display Total Income, Total Expenses, and Balance in real-time
- ✅ **Pie chart** (Chart.js) visualizes income distribution by source
- ✅ **Line chart** (Chart.js) shows monthly expense trends over time
- ✅ **Recent transactions** table lists the last 10 combined entries

### 8.4 AI Financial Advisor
- ✅ Chat interface allows **natural language** financial queries
- ✅ AI has **context** of user's actual income, expenses, and balance
- ✅ Provides **personalized** savings tips, budget plans, and purchase advice
- ✅ Quick **suggestion chips** for common queries
- ✅ Graceful **error handling** for API quota limits

### 8.5 UI/UX Design
- ✅ **Dark glassmorphism** theme with gradient accents
- ✅ Fully **responsive** design for all screen sizes
- ✅ **Smooth animations** and hover effects (0.3s cubic-bezier transitions)
- ✅ **Toast notifications** for user feedback on actions
- ✅ **Empty states** with helpful messages when no data exists

---

## 📌 9. Conclusion

**ExpenseIQ** is a successfully developed full-stack personal finance management application that combines traditional expense tracking with modern AI capabilities. The project demonstrates:

1. **Full-Stack Proficiency** — Seamless integration of a Python Flask backend with a vanilla HTML/CSS/JavaScript frontend, communicating through well-designed RESTful APIs.

2. **Database Design** — Properly normalized MySQL schema with foreign key relationships and cascading deletes ensuring data integrity.

3. **Security Best Practices** — Implementation of bcrypt password hashing, session-based authentication, and route-level authorization using decorators.

4. **Data Visualization** — Integration of Chart.js for interactive, dynamic pie and line charts that update with real user data.

5. **AI Integration** — Novel use of Google Gemini AI to create a context-aware financial advisor that understands the user's actual financial situation, not just generic advice.

6. **Modern UI/UX** — A polished dark-themed interface with glassmorphism, animations, and responsive design that provides a premium user experience.

### Future Enhancements
- **Export Reports** — PDF/CSV export of income and expense data
- **Budget Goals** — Set monthly/category-wise budget limits with alerts
- **Recurring Transactions** — Auto-add recurring income/expenses
- **Multi-Currency Support** — Support for international currencies
- **Mobile App** — React Native or Flutter mobile application
- **Advanced Analytics** — Year-over-year comparison, spending predictions
- **Email Notifications** — Alerts when nearing budget limits

---

## 🌍 10. Applications of the Project

### 10.1 Personal Finance Management
- Individuals can track daily income and expenses to build better financial habits
- Students can monitor their monthly budgets and identify overspending areas
- Freelancers can track income from multiple clients/sources

### 10.2 Educational Purpose
- Serves as a **Mini Project / Major Project** for B.Tech, BCA, MCA students
- Demonstrates full-stack development with Python Flask and MySQL
- Showcases AI integration with Google Gemini API
- Illustrates RESTful API design, authentication, and data visualization

### 10.3 Small Business Use
- Small business owners can use it to track business income and operational expenses
- Helps in maintaining a simplified profit/loss overview
- AI advisor can help with cost-cutting recommendations

### 10.4 Family Budgeting
- Families can track household expenses across categories (Food, Bills, Rent, etc.)
- The dashboard provides a quick snapshot of the family's financial health
- AI advisor can suggest savings strategies based on spending patterns

### 10.5 Financial Literacy & Awareness
- The visualization features (pie charts, line graphs) help users **understand** their money flow
- The AI advisor educates users on budgeting, saving, and smart spending
- Promotes financial discipline through regular tracking

### 10.6 Prototype for Fintech Applications
- Can serve as a **proof of concept** for fintech startups
- The AI-powered advisor demonstrates the value of intelligent financial tools
- The architecture can be extended to support bank API integrations, UPI tracking, etc.

---

## 📁 Project Structure

```
expense-tracker/
├── app.py                    # Flask backend (483 lines) — all API routes
├── db.sql                    # MySQL database schema
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (DB config, API keys)
└── public/                   # Frontend static files
    ├── index.html            # Landing page with login/register
    ├── dashboard.html        # Dashboard with charts and stats
    ├── income.html           # Income management page
    ├── expenses.html         # Expense management page
    ├── advisor.html          # AI financial advisor chat
    ├── css/
    │   └── styles.css        # Complete design system (1278 lines)
    └── js/
        ├── auth.js           # Authentication logic
        ├── dashboard.js      # Dashboard data loading & chart rendering
        ├── income.js         # Income CRUD operations
        ├── expenses.js       # Expense CRUD operations
        └── advisor.js        # AI chat interface logic
```

---

## 📚 References

1. Flask Documentation — https://flask.palletsprojects.com/
2. MySQL 8.0 Reference Manual — https://dev.mysql.com/doc/refman/8.0/en/
3. Chart.js Documentation — https://www.chartjs.org/docs/
4. Google Gemini AI Documentation — https://ai.google.dev/docs
5. bcrypt Password Hashing — https://pypi.org/project/bcrypt/
6. MDN Web Docs (HTML/CSS/JS) — https://developer.mozilla.org/

---

> **Project Name**: ExpenseIQ — Smart Expense Tracker  
> **Technology**: Python Flask + MySQL + Chart.js + Google Gemini AI  
> **Type**: Full-Stack Web Application  
> **Category**: Personal Finance Management  
