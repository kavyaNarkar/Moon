import webview
import threading
from .server import app

def start_desktop_app():
    """
    Launches the Flask server in a separate thread and opens a native window using pywebview.
    """
    # Run Flask in a background thread with multi-threading enabled
    server_thread = threading.Thread(target=lambda: app.run(port=5000, debug=False, use_reloader=False, threaded=True))
    server_thread.daemon = True
    server_thread.start()

    # Create and start the webview window
    print("Launching Moon Desktop App...")
    webview.create_window('Moon AI Assistant', 'http://127.0.0.1:5000', 
                          width=1000, height=800, 
                          background_color='#050505')
    webview.start()

if __name__ == '__main__':
    start_desktop_app()
