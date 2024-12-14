from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
from EDAtoJSON import EDAtoJSON  
import io
from forcast import ForecastingModel  

import csv

app = Flask(__name__)


client = MongoClient("mongodb+srv://bybenseghieryasser:tqnYztMrMUG7j2f0@cluster0.xntsfip.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["test"]
csv_collection = db["csvfiles"]

@app.route('/histogram_sales', methods=['GET'])
def histogram_sales():
    file_id = request.args.get('_id')

    if not file_id:
        return jsonify({"error": "CSV file ID is required"}), 400

    try:
        csv_file = csv_collection.find_one({"_id": ObjectId(file_id)})
        if not csv_file:
            return jsonify({"error": "CSV file not found"}), 404

        csv_content = csv_file.get("data")
        if not csv_content:
            return jsonify({"error": "CSV content is empty"}), 400

        csv_string = io.StringIO(csv_content.decode('utf-8'))
        df = pd.read_csv(csv_string)

        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        # Perform EDA
        eda = EDAtoJSON(df)
        eda.generate_histogram_sales_by_category(categorical_cols, sales_col='sales')

        return jsonify(eda.results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sales_over_time', methods=['GET'])
def sales_over_time():
    file_id = request.args.get('_id')

    if not file_id:
        return jsonify({"error": "CSV file ID is required"}), 400

    try:
        csv_file = csv_collection.find_one({"_id": ObjectId(file_id)})
        if not csv_file:
            return jsonify({"error": "CSV file not found"}), 404

        csv_content = csv_file.get("data")
        if not csv_content:
            return jsonify({"error": "CSV content is empty"}), 400

        # Read CSV content into a DataFrame
        csv_string = io.StringIO(csv_content.decode('utf-8'))
        df = pd.read_csv(csv_string)

        # Ensure the time column exists
        time_col = 'time'  # Replace with the actual column name for time
        if time_col not in df.columns:
            return jsonify({"error": f"Time column '{time_col}' not found in dataset"}), 400

        # Perform EDA
        eda = EDAtoJSON(df)
        eda.generate_line_graph_sales_over_time(time_col, sales_col='sales')

        return jsonify(eda.results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/forecast/next_week', methods=['GET'])
def forecast_next_week():
    file_id = request.args.get('_id')

    if not file_id:
        return jsonify({"error": "CSV file ID is required"}), 400

    try:
        csv_file = csv_collection.find_one({"_id": ObjectId(file_id)})
        if not csv_file:
            return jsonify({"error": "CSV file not found"}), 404

        csv_content = csv_file.get("data")
        if not csv_content:
            return jsonify({"error": "CSV content is empty"}), 400

        # Read CSV content into a DataFrame
        csv_string = io.StringIO(csv_content.decode('utf-8'))
        df = pd.read_csv(csv_string)

        # Initialize ForecastingModel
        forecasting_model = ForecastingModel(df, date_col='date', sales_col='sales')
        forecasting_model.preprocess_data()

        # Forecast next week
        forecast = forecasting_model.forecast_next_week()
        return jsonify(forecast.to_dict(orient='records'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/forecast/next_month', methods=['GET'])
def forecast_next_month():
    file_id = request.args.get('_id')

    if not file_id:
        return jsonify({"error": "CSV file ID is required"}), 400

    try:
        csv_file = csv_collection.find_one({"_id": ObjectId(file_id)})
        if not csv_file:
            return jsonify({"error": "CSV file not found"}), 404

        csv_content = csv_file.get("data")
        if not csv_content:
            return jsonify({"error": "CSV content is empty"}), 400

        csv_string = io.StringIO(csv_content.decode('utf-8'))
        df = pd.read_csv(csv_string)

        # Initialize ForecastingModel
        forecasting_model = ForecastingModel(df, date_col='date', sales_col='sales')
        forecasting_model.preprocess_data()

        forecast = forecasting_model.forecast_next_month()
        return jsonify(forecast.to_dict(orient='records'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/forecast/next_year', methods=['GET'])
def forecast_next_year():
    file_id = request.args.get('_id')

    if not file_id:
        return jsonify({"error": "CSV file ID is required"}), 400

    try:
        csv_file = csv_collection.find_one({"_id": ObjectId(file_id)})
        if not csv_file:
            return jsonify({"error": "CSV file not found"}), 404

        csv_content = csv_file.get("data")
        if not csv_content:
            return jsonify({"error": "CSV content is empty"}), 400

        # Read CSV content into a DataFrame
        csv_string = io.StringIO(csv_content.decode('utf-8'))
        df = pd.read_csv(csv_string)

        # Initialize ForecastingModel
        forecasting_model = ForecastingModel(df, date_col='date', sales_col='sales')
        forecasting_model.preprocess_data()

        # Forecast next year
        forecast = forecasting_model.forecast_next_year()
        return jsonify(forecast.to_dict(orient='records'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=4000)
