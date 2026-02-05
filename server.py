"""
Production server using Waitress.
Run with: python server.py
"""
from waitress import serve
from app import app, db, init_sample_data

if __name__ == '__main__':
    # Initialize database and sample data
    with app.app_context():
        db.create_all()
        init_sample_data()
    
    # Get your IP by running 'ipconfig' in terminal
    HOST = '0.0.0.0'  # Binds to all network interfaces
    PORT = 8080
    
    print("=" * 50)
    print("🚀 Personal Dashboard (Waitress)")
    print("=" * 50)
    print(f"   Local:   http://localhost:{PORT}")
    print(f"   Network: http://YOUR_IP:{PORT}")
    print("")
    print("   Run 'ipconfig' to find your IP address")
    print("   Press Ctrl+C to stop the server")
    print("=" * 50)
    
    serve(app, host=HOST, port=PORT, threads=4)
