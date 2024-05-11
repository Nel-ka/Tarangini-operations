import json
import datetime

# Function to calculate panel age
def calculate_panel_age(installation_date, plant_id):
    current_date = datetime.date.today()
    age = current_date.year - installation_date.year
    if age <0:
        print(f"Date error : check installation date of plant {plant_id}")
    return max(age, 0)

# Function to calculate panel deterioration
def calculate_deterioration(age_years, deterioration_rate):
    return (1 - (deterioration_rate / 100) * age_years)

# Function to calculate max production based on plant capacity and deterioration factor
def calculate_max_production(capacity, deterioration_factor):
    return round(capacity * 5 * deterioration_factor, 2)

# Function to determine threshold based on weather conditions
def determine_threshold(weather_condition, max_production):
    # Hardcoded thresholds for different weather conditions
    thresholds = {
        "sunny": 1,
        "mostly sunny": 0.95,
        "partly cloudy": 0.8,
        "mostly cloudy": 0.75,
        "cloudy": 0.7,
        "snow": 0.6,
        "rain": 0.0,
        "scattered showers": 0.0,
        "thunderstorm": 0.0,
        "fog": 0.5,
        "mist": 0.5,
        "clean": 0.9,
        "drizzle": 0.65
    }
    threshold = thresholds.get(weather_condition.lower(), 1)  # Default threshold is 1 if condition not found
    buffer_value = 0.8 # setting value as 80% to trigger alert, allowing 20% deviation from ideal condition
    return round(max_production * threshold*buffer_value, 2)

# Function to process plant data and trigger alerts
def process_plant_data(plant_data):
    alerts = []
    cluster_production = 0
    cluster_capacity = 0
    for plant_id, data in plant_data.items():
        net_production = data["net_production"]
        cluster_production += net_production
        installation_date = datetime.datetime.strptime(data["installation_date"], "%d/%m/%Y").date() # for cluster.json
        capacity = data["capacity"]
        deterioration_rate = data["deterioration_rate"]
        weather_condition = data["weather_condition"]

        panel_age_years = calculate_panel_age(installation_date, plant_id)
        deterioration_factor = calculate_deterioration(panel_age_years, deterioration_rate)
        max_production = calculate_max_production(capacity, deterioration_factor)
        cluster_capacity += max_production
        threshold = determine_threshold(weather_condition, max_production)

        if net_production < threshold:
            alerts.append(f"\033[91mPlant {plant_id}: Alert triggered, Performance {net_production}/{threshold} kWh max cap {max_production}\033[0m")
        else:
            alerts.append(f"\033[92mPlant {plant_id}: Performance {net_production}/{threshold} kWh max cap {max_production}\033[0m")


    return alerts, cluster_production, round(cluster_capacity, 2)

def load_cluster_data(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

def assess_cluster(cluster_name, cluster_production, cluster_capacity, cleaning_cost_per_plant, no_of_plants,revenue_per_unit_production):
    total_production = cluster_production
    total_capacity = cluster_capacity
    
    # Calculate loss in revenue due to production below threshold
    if total_production < total_capacity:
        revenue_loss = (total_capacity - total_production) * revenue_per_unit_production 
    else:
        revenue_loss = 0
    
    # Calculate total cost of cleaning all plants in the cluster
    total_cleaning_cost = no_of_plants * cleaning_cost_per_plant
    
    # Trigger alert if the revenue loss exceeds the total cleaning cost
    alert_val = revenue_loss > total_cleaning_cost
    if alert_val:
        print(f'\033[91mAlert triggered {cluster_name}.\033[0m')
        # Trigger alert or take necessary action
    else:
        print(f"\033[92m{cluster_name}\033[0m")
        
    return alert_val

def main():
    clusters_data = load_cluster_data("C:\\Users\\Nelka\\Desktop\\Study\\Startup\\Energy generation\\tarangini\\clusters.json")
    cleaning_cost_per_plant = 50  # Example cleaning cost per plant
    revenue_per_unit_production = 4.5 # Rs 4.5 per unit

    # Group clusters by location
    clusters_by_location = {}
    for cluster_name, cluster_data in clusters_data.items():
        location = cluster_data.get("location")
        if location not in clusters_by_location:
            clusters_by_location[location] = []
        clusters_by_location[location].append((cluster_name, cluster_data))
    
    # Iterate over clusters grouped by location
    for location, clusters in clusters_by_location.items():
        print(f"Location: {location}")
        for cluster_name, cluster_data in clusters:
            plant_data = cluster_data["plants"]
            no_of_plants = len(plant_data)
            alerts, cluster_production, cluster_capacity = process_plant_data(plant_data)
            
            alert_val = assess_cluster(cluster_name, cluster_production, cluster_capacity, no_of_plants, cleaning_cost_per_plant, revenue_per_unit_production)
            
            if alert_val:
                # print("  Cluster:", cluster_name)
                for alert in alerts:
                    print("    ", alert)
            else: #comment out this condition to get consolidated view for green clusters
                for alert in alerts:
                    print("    ", alert)
                
        print()
                    
if __name__ == "__main__":
    main()

