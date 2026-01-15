# Recipe Search Tool

A full-stack web application for searching, analyzing, and managing recipes. The application features an intuitive React frontend with analytics dashboards and a FastAPI backend that integrates with Tavily search API to find recipes from across the web.

Original design available at: [Figma Design](https://www.figma.com/design/ziZbu7gCm81rgp7PoU5LqE/Recipe-Search-Tool)

## Features

- 🔍 **Recipe Search**: Search for recipes using natural language queries powered by Tavily API
- 📊 **Analytics Dashboard**: View comprehensive analytics on recipe searches and usage
- 📝 **Recipe History**: Track and manage your recipe search history
- 🎨 **Modern UI**: Built with Radix UI components and Tailwind CSS for a beautiful, responsive interface
- 🔄 **Structured Recipe View**: View recipes in a structured, easy-to-read format
- 📈 **Error Analysis**: Monitor and analyze errors in recipe processing
- 💬 **Feedback System**: Collect and manage user feedback
- ⚙️ **Settings Panel**: Customize your experience with various settings

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for build tooling
- **Radix UI** for accessible component primitives
- **Tailwind CSS** for styling
- **Recharts** for data visualization
- **Axios** for API communication
- **React Hook Form** for form management

### Backend
- **FastAPI** for the REST API
- **SQLite** for data persistence
- **Tavily Python SDK** for recipe search
- **Uvicorn** as ASGI server
- **Python-dotenv** for environment configuration
- **Structured logging** with request ID tracking

## Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.8 or higher)
- **npm** or **yarn**
- **Tavily API Key** ([Get one here](https://tavily.com))

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/MaxeeTig/recipe_bot_eval.git
cd recipe_bot_eval
```

### 2. Frontend Setup

```bash
# Install dependencies
npm install

# The development server will start automatically
npm run dev
```

The frontend will be available at `http://localhost:5173` (default Vite port).

### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python init_db.py

# Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`.

API documentation (Swagger UI) will be available at `http://localhost:8000/docs`.

## Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Tavily API Configuration (Required)
TAVILY_API_KEY=your_tavily_api_key_here

# AI Gateway Configuration (Optional, for future use)
AI_GATEWAY_API_KEY=your_ai_gateway_key_here

# Logging Configuration (Optional)
LOG_LEVEL=INFO
ENABLE_FILE_LOGGING=true
```

### Getting a Tavily API Key

1. Visit [Tavily.com](https://tavily.com)
2. Sign up for an account
3. Navigate to your API keys section
4. Copy your API key and add it to the `.env` file

## Running the Application

### Development Mode

1. **Start the backend** (in one terminal):
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. **Start the frontend** (in another terminal):
   ```bash
   npm run dev
   ```

3. Open your browser and navigate to `http://localhost:5173`

### Production Build

**Frontend:**
```bash
npm run build
```

The built files will be in the `dist` directory.

**Backend:**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Project Structure

```
recipe_bot_eval/
├── backend/                 # FastAPI backend
│   ├── __init__.py
│   ├── main.py             # FastAPI application entry point
│   ├── config.py           # Configuration and environment variables
│   ├── database.py         # Database operations
│   ├── init_db.py          # Database initialization script
│   ├── logger.py           # Logging configuration
│   ├── tavily_service.py   # Tavily API integration
│   └── requirements.txt    # Python dependencies
├── src/                    # React frontend source
│   ├── components/         # React components
│   │   ├── ui/            # Reusable UI components (Radix UI)
│   │   ├── AnalyticsDashboard.tsx
│   │   ├── RecipeDetailPage.tsx
│   │   ├── RecipeHistory.tsx
│   │   └── ...
│   ├── lib/               # Utility libraries
│   │   ├── api.ts        # API client
│   │   └── logger.ts     # Frontend logging
│   ├── types/            # TypeScript type definitions
│   └── App.tsx           # Main application component
├── data/                 # Database storage directory
├── logs/                 # Application logs (if file logging enabled)
├── package.json          # Frontend dependencies
├── vite.config.ts        # Vite configuration
├── tsconfig.json         # TypeScript configuration
└── README.md            # This file
```

## API Endpoints

The backend provides the following main endpoints:

- `GET /api/recipes` - Get all recipes
- `GET /api/recipes/{recipe_id}` - Get a specific recipe
- `POST /api/recipes/search` - Search for recipes
- `DELETE /api/recipes/{recipe_id}` - Delete a recipe
- `GET /api/analytics` - Get analytics data

For complete API documentation, visit `http://localhost:8000/docs` when the backend is running.

## Features in Detail

### Recipe Search
- Natural language recipe queries
- Automatic recipe extraction and structuring
- Multiple search result ranking
- Recipe metadata extraction

### Analytics Dashboard
- Search statistics and trends
- Recipe popularity metrics
- Error rate monitoring
- User engagement metrics

### Recipe Management
- Save favorite recipes
- Recipe history tracking
- Recipe deletion
- Recipe detail views

## Development

### Code Style
- Frontend: TypeScript with ESLint
- Backend: Python with PEP 8 style guide

### Logging
The application uses structured logging with request ID tracking. Logs are written to:
- Console (always)
- Log files in `logs/` directory (if enabled)

### Database
The application uses SQLite for data persistence. The database file is stored in the `data/` directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on the [GitHub repository](https://github.com/MaxeeTig/recipe_bot_eval).
