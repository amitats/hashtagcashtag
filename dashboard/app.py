from flask import Flask, render_template
import psycopg2
import plotly.graph_objs as go

app = Flask(__name__)

@app.route("/")
def home():
    conn = psycopg2.connect(...)  # Connect to DB
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock_sentiment WHERE symbol='AAPL'")
    rows = cursor.fetchall()
    
    # Build Plotly chart
    timestamps = [r[1] for r in rows]
    mentions = [r[2] for r in rows]
    positives = [r[3] for r in rows]

    chart = go.Figure()
    chart.add_trace(go.Scatter(x=timestamps, y=mentions, name="Mentions"))
    chart.add_trace(go.Scatter(x=timestamps, y=positives, name="Positives"))

    return chart.to_html()

if __name__ == "__main__":
    app.run(debug=True)
