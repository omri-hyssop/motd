#!/bin/bash
# Development server startup script

echo "🚀 Starting Meal of the Day Development Server"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Check if database exists
if [ ! -f "motd_dev.db" ]; then
    echo "🗄️  Setting up database..."
    
    # Initialize migrations
    if [ ! -d "migrations" ]; then
        flask db init
    fi
    
    # Create migration
    flask db migrate -m "Initial migration"
    
    # Apply migration
    flask db upgrade
    
    echo ""
    echo "👤 Create an admin user to get started"
    python manage.py create-admin
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting Flask development server..."
echo "   API will be available at: http://localhost:5000"
echo "   Press Ctrl+C to stop"
echo ""

# Run Flask development server
export FLASK_APP=wsgi.py
export FLASK_ENV=development
flask run
