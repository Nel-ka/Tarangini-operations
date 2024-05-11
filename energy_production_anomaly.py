import csv
import datetime
import cluster_analysis_pro as cap

# Dictionary to store deterioration factors for each installation date
deterioration_factors = {}

# Function to parse the CSV file and perform anomaly detection
def analyze_data(csv_file, capacity, deterioration_rate,installation_date):
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            date_str = row['Time']
            output_power = float(row['Output power'])
            weather_condition = row['weather']

            # Convert date string to datetime object
            production_date = datetime.datetime.strptime(date_str, '%d-%m-%Y').date()

            if installation_date not in deterioration_factors:
                panel_age_years = (production_date - installation_date).days / 365  # Calculate panel age in years
                deterioration_factor = cap.calculate_deterioration(panel_age_years, deterioration_rate)
                deterioration_factors[installation_date] = deterioration_factor
            else:
                # Get previously calculated deterioration factor
                deterioration_factor = deterioration_factors[installation_date]

            # Calculate maximum production based on capacity and deterioration factor
            max_production = cap.calculate_max_production(capacity, deterioration_factor)

            # Determine threshold based on weather condition
            threshold = cap.determine_threshold(weather_condition, max_production)

            # Check if net production is significantly lower than the threshold
            if output_power < threshold * 0.6:  # Adjusted threshold to allow deviation
                print("\033[91m" + f"Date: {date_str}, Anomaly detected: Production {output_power} kW is significantly lower than expected (threshold: {threshold} kW)" + "\033[0m")
            elif output_power > threshold * 2:
                print("\033[91m" + f"Date: {date_str}, Anomaly detected: Production {output_power} kW is significantly higher than expected (threshold: {threshold} kW)" + "\033[0m")

# Main function
def main():
    csv_file = "datafeed_with_weather.csv"
    capacity = 5
    deterioration_rate = 1.2
    installation_date = datetime.date(2020, 1, 1)  # Use fixed installation date for now
    analyze_data(csv_file, capacity, deterioration_rate, installation_date)

# Run the main function
if __name__ == "__main__":
    main()
