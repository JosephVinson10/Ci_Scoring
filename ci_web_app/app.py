import os
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

# Upload folder for storing files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to calculate CI score
def calculate_ci(emissions, output):
    if output == 0:
        return 0
    return emissions / output

# Route for the homepage with the form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission
@app.route('/calculate', methods=['POST'])
def calculate():
    if 'file' not in request.files:
        return "No file part in the request."

    file = request.files['file']

    # Save the file to the uploads folder
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Retrieve latitude and longitude input from the form
    lat = request.form.get('latitude')
    long = request.form.get('longitude')

    try:
        # Process CSV file
        df = pd.read_csv(file_path)

        # Ensure required columns are present
        required_columns = ['Product', 'CO2 Emissions (kg CO2)', 'Output (kg)', 'Energy Use (kWh)', 'Transport Distance (km)']
        if not all(column in df.columns for column in required_columns):
            raise ValueError("CSV file is missing required headers.")
        
        # Calculate CI scores and add to DataFrame
        df['CI Score (kg CO2/unit)'] = df.apply(lambda row: calculate_ci(row['CO2 Emissions (kg CO2)'], row['Output (kg)']), axis=1)

        # Create graph of CI scores
        plot_ci_graph(df)

        # Save results to a new CSV file
        results_file = os.path.join(app.config['UPLOAD_FOLDER'], 'ci_scoring_results.csv')
        df.to_csv(results_file, index=False)

        # Pass the DataFrame directly to the template
        return render_template('results.html', df=df, lat=lat, long=long)
    except Exception as e:
        return str(e)


# Function to plot the CI graph
def plot_ci_graph(df):
    try:
        # Create a bar chart
        plt.figure(figsize=(10, 6))
        plt.bar(df['Product'], df['CI Score (kg CO2/unit)'], color='skyblue')

        # Adding title and labels
        plt.title('CI Scores for Different Products', fontsize=14)
        plt.xlabel('Product', fontsize=12)
        plt.ylabel('CI Score (kg CO2/unit)', fontsize=12)

        # Save the graph as an image in the static folder
        graph_file = os.path.join('static', 'ci_scoring_graph.png')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(graph_file)
        plt.close()

    except Exception as e:
        print(f"Error generating graph: {e}")

if __name__ == '__main__':
    app.run(debug=True)
