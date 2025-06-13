from flask import Flask, redirect, render_template_string
import subprocess
import os
import sys

app = Flask(__name__)

@app.route('/')
def index():
    return redirect('/streamlit/')

@app.route('/streamlit/')
def streamlit():
    # Start Streamlit in the background if not already running
    streamlit_process = subprocess.Popen(
        ["streamlit", "run", "../app.py", "--server.port=8506", "--server.address=0.0.0.0"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Simple HTML to redirect to the Streamlit app
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Redirecting to xT-GK Streamlit App</title>
        <meta http-equiv="refresh" content="0;url=http://{{ host }}:8506">
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
            }
        </style>
    </head>
    <body>
        <h1>Redirecting to xT-GK Streamlit App...</h1>
        <p>If you are not redirected automatically, <a href="http://{{ host }}:8506">click here</a>.</p>
    </body>
    </html>
    """, host=request.host.split(':')[0])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
