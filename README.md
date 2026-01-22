# Recipe Pipeline Verifier

A full-stack web application for searching, extracting, parsing, and analyzing recipes from [russianfood.com](https://www.russianfood.com). The application features an intuitive React frontend with analytics dashboards and a FastAPI backend that uses web scraping (Selenium + BeautifulSoup) to extract recipes and LLM-based parsing to structure recipe data.

Original design available at: [Figma Design](https://www.figma.com/design/ziZbu7gCm81rgp7PoU5LqE/Recipe-Search-Tool)

## Features

- 🔍 **Recipe Search**: Search for recipes on russianfood.com using natural language queries
- 🤖 **LLM-Powered Parsing**: Automatically parse and structure recipes using multiple LLM providers (Together AI, Vercel AI, Mistral AI, DeepSeek AI)
- 📊 **Analytics Dashboard**: View comprehensive analytics on recipe processing, success rates, and error types
- 📝 **Recipe History**: Track and manage your recipe search and processing history
- 🎨 **Modern UI**: Built with Radix UI components and Tailwind CSS for a beautiful, responsive interface
- 🔄 **Structured Recipe View**: View recipes in a structured, easy-to-read format with ingredients, instructions, and metadata
- 📈 **Error Analysis**: Automatic error analysis for failed recipe parsing with LLM-powered diagnostics
- 🔧 **Patches System**: Apply patches to improve recipe parsing based on error analysis
- ⚙️ **Settings Panel**: Customize LLM providers, models, and other processing settings
- 🔄 **Re-parse Recipes**: Re-run parsing on recipes with updated configurations or patches

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
- **Selenium** + **BeautifulSoup** for web scraping russianfood.com
- **LLM Integration** supporting multiple providers:
  - Together AI (GPT-OSS, Llama models)
  - Vercel AI Gateway (GPT-4, Claude models)
  - Mistral AI (Mistral models)
  - DeepSeek AI (DeepSeek models)
- **Uvicorn** as ASGI server
- **Python-dotenv** for environment configuration
- **Structured logging** with request ID tracking and file rotation

## Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.8 or higher)
- **npm** or **yarn**
- **Chrome/Chromium** browser (for Selenium web scraping)
- **LLM API Key** (at least one of the following):
  - Together AI API Key ([Get one here](https://together.ai))
  - Vercel AI Gateway API Key ([Get one here](https://vercel.com))
  - Mistral AI API Key ([Get one here](https://mistral.ai))
  - DeepSeek AI API Key ([Get one here](https://deepseek.com))

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

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:3002` (configured in `vite.config.ts`).

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
# Note: Create a requirements.txt with dependencies or install manually:
# pip install fastapi uvicorn selenium beautifulsoup4 python-dotenv pydantic

# The database will be initialized automatically on first run
# Database file will be created at: data/recipes.db

# Start the backend server
python -m backend.main
# Or using uvicorn directly:
# uvicorn backend.main:app --reload --host 0.0.0.0 --port 8003
```

The backend API will be available at `http://localhost:8003` (configured in `backend/config.py`).

API documentation (Swagger UI) will be available at `http://localhost:8003/docs`.

## Configuration

Create a `.env` file in the root directory with the following variables:

```env
# LLM Provider API Keys (at least one required)
# Together AI
TOGETHER_AI_API_KEY=your_together_ai_api_key_here

# Vercel AI Gateway
AI_GATEWAY_API_KEY=your_vercel_ai_gateway_key_here

# Mistral AI
MISTRAL_API_KEY=your_mistral_api_key_here

# DeepSeek AI
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# API Server Configuration (Optional)
API_HOST=0.0.0.0
API_PORT=8003
API_RELOAD=true

# Logging Configuration (Optional)
LOG_LEVEL=INFO
LOG_TO_FILE=true
```

### Getting LLM API Keys

**Together AI:**
1. Visit [together.ai](https://together.ai)
2. Sign up for an account
3. Navigate to your API keys section
4. Copy your API key and add it to the `.env` file

**Vercel AI Gateway:**
1. Visit [vercel.com](https://vercel.com)
2. Sign up and navigate to AI Gateway settings
3. Create an API key
4. Add it to the `.env` file as `AI_GATEWAY_API_KEY`

**Mistral AI:**
1. Visit [mistral.ai](https://mistral.ai)
2. Sign up for an account
3. Get your API key from the dashboard
4. Add it to the `.env` file as `MISTRAL_API_KEY`

**DeepSeek AI:**
1. Visit [deepseek.com](https://deepseek.com)
2. Sign up for an account
3. Get your API key
4. Add it to the `.env` file as `DEEPSEEK_API_KEY`

The default LLM provider can be configured in `config_section.py` (default: `mistral_ai`).

## Running the Application

### Development Mode

1. **Start the backend** (in one terminal):
   ```bash
   cd backend
   python -m backend.main
   # Or: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8003
   ```

2. **Start the frontend** (in another terminal):
   ```bash
   npm run dev
   ```

3. Open your browser and navigate to `http://localhost:3002`

The frontend is configured to proxy API requests to `http://localhost:8003` automatically.

### Production Build

**Frontend:**
```bash
npm run build
```

The built files will be in the `dist` directory.

**Backend:**
```bash
cd backend
uvicorn backend.main:app --host 0.0.0.0 --port 8003
```

## Project Structure

```
recipe_bot_eval/
├── backend/                 # FastAPI backend
│   ├── __init__.py
│   ├── main.py             # FastAPI application entry point
│   ├── config.py           # Configuration loader (imports from config_section.py)
│   ├── logging_config.py   # Logging configuration with request ID tracking
│   ├── api/                # API routes and dependencies
│   │   ├── dependencies.py # Request ID and logger dependencies
│   │   └── routes/
│   │       └── recipes.py  # All /api/recipes/* endpoints
│   ├── database/           # Database operations
│   │   ├── __init__.py
│   │   └── db.py          # SQLite database operations
│   ├── models/            # Pydantic schemas
│   │   ├── __init__.py
│   │   └── schemas.py     # Request/response models
│   └── services/          # Business logic services
│       ├── scraper_service.py   # Selenium + BeautifulSoup web scraping
│       ├── parser_service.py    # LLM-based recipe parsing
│       └── analysis_service.py  # Error analysis with LLM
├── src/                    # React frontend source
│   ├── components/         # React components
│   │   ├── ui/            # Reusable UI components (Radix UI)
│   │   ├── AnalyticsDashboard.tsx
│   │   ├── RecipeDetailPage.tsx
│   │   ├── RecipeHistory.tsx
│   │   ├── HomePage.tsx
│   │   ├── SettingsPanel.tsx
│   │   └── ...
│   ├── lib/               # Utility libraries
│   │   ├── api.ts        # API client
│   │   ├── logger.ts     # Frontend logging
│   │   ├── storage.ts    # LocalStorage utilities
│   │   └── recipeTransform.ts  # Data transformation utilities
│   ├── types/            # TypeScript type definitions
│   │   └── recipe.ts     # Recipe type definitions
│   ├── App.tsx           # Main application component
│   └── main.tsx          # React entry point
├── patches/              # Recipe parsing patches
│   ├── cleanup_rules.json
│   ├── system_prompt_append.txt
│   └── unit_mapping.json
├── data/                 # Database storage directory (SQLite file)
├── log/                  # Application logs (if file logging enabled)
├── config_section.py     # Centralized configuration
├── recipe_models.py      # Recipe data models
├── patches.py            # Patch application logic
├── response_cleanup.py   # Response cleaning utilities
├── package.json          # Frontend dependencies
├── vite.config.ts        # Vite configuration (port 3002, proxy to 8003)
├── tsconfig.json         # TypeScript configuration
├── system_prompt.txt     # LLM system prompt for parsing
├── error_analysis_prompt.txt  # LLM prompt for error analysis
└── README.md            # This file
```

## API Endpoints

The backend provides the following main endpoints:

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check endpoint

### Recipe Endpoints
- `GET /api/recipes` - Get all recipes (optional `?status_filter=new|success|failure`)
- `GET /api/recipes/stats` - Get recipe statistics (optional `?date_from=` and `?date_to=` filters)
- `GET /api/recipes/{recipe_id}` - Get full recipe details
- `GET /api/recipes/{recipe_id}/raw` - Get raw scraped recipe data
- `GET /api/recipes/{recipe_id}/parsed` - Get parsed recipe schema
- `POST /api/recipes/search` - Search for a recipe on russianfood.com and save it
- `POST /api/recipes/{recipe_id}/parse` - Parse a recipe using LLM (optional `model` parameter)
- `POST /api/recipes/{recipe_id}/analyze` - Analyze errors for a failed recipe (optional `apply_patches`, `reparse` parameters)
- `GET /api/recipes/{recipe_id}/analyses` - Get all error analyses for a recipe
- `DELETE /api/recipes/{recipe_id}` - Delete a recipe

For complete API documentation with request/response schemas, visit `http://localhost:8003/docs` when the backend is running.

## Features in Detail

### Recipe Search & Extraction
- Natural language recipe queries on russianfood.com
- Automatic web scraping using Selenium + BeautifulSoup
- Recipe content extraction (title, text, URL)
- Automatic saving to database with status tracking

### LLM-Powered Parsing
- Multi-provider LLM support (Together AI, Vercel AI, Mistral AI, DeepSeek AI)
- Structured recipe parsing (ingredients, instructions, metadata)
- Configurable models per provider
- Automatic parsing on recipe selection (if not already parsed)
- Manual re-parsing with different models/providers

### Error Analysis & Patches
- Automatic error analysis for failed recipe parsing
- LLM-powered error diagnosis and suggestions
- Patches system for improving parsing rules
- Apply patches and re-parse recipes automatically
- Track error types and patterns

### Analytics Dashboard
- Total recipe counts
- Statistics by status (new, success, failure)
- Error type breakdown
- Date-filtered statistics
- Visual charts and metrics

### Recipe Management
- View recipe history with status indicators
- Detailed recipe views (raw and parsed)
- Recipe deletion
- Batch re-parsing operations
- Settings for LLM provider and model selection

## Development

### Code Style
- Frontend: TypeScript with ESLint
- Backend: Python with PEP 8 style guide

### Logging
The application uses structured logging with request ID tracking:
- **Request ID Middleware**: Each request gets a unique ID (from `X-Request-ID` header or auto-generated)
- **Console Logging**: Always enabled with structured format
- **File Logging**: Rotating file handler writes to `log/backend.log` (if `LOG_TO_FILE=true`)
- **Log Levels**: Configurable via `LOG_LEVEL` environment variable (default: INFO)

### Database
The application uses SQLite for data persistence:
- **Database Location**: `data/recipes.db` (auto-created on first run)
- **Schema**: Stores recipes with status (new/success/failure), raw content, parsed data, and error analyses
- **Initialization**: Database and tables are created automatically when the backend starts

### Web Scraping
- **Selenium WebDriver**: Uses Chrome/Chromium in headless mode (configurable)
- **BeautifulSoup**: HTML parsing and content extraction
- **Wait Strategies**: Configurable timeouts for page loads and element visibility
- **Content Extraction**: Extracts recipe title, text content, and URL from russianfood.com

### LLM Configuration
- **Provider Selection**: Configured in `config_section.py` (default: `mistral_ai`)
- **Model Selection**: Choose from available models per provider
- **System Prompts**: Customizable prompts in `system_prompt.txt` and `error_analysis_prompt.txt`
- **Patches**: System prompt can be enhanced with patches from error analysis

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on the [GitHub repository](https://github.com/MaxeeTig/recipe_bot_eval).
