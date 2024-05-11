import json
import cluster_analysis_pro as ca

def load_cluster_data(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

def assess_cluster(cluster_name, cluster_production, cluster_capacity, cleaning_cost_per_plant, no_of_plants, revenue_per_unit_production, location_cost):
    total_production = cluster_production
    total_capacity = cluster_capacity
    net_benefit_clean_cluster = 0
    
    if total_production < total_capacity:
        revenue_loss = (total_capacity - total_production) * revenue_per_unit_production 
    else:
        revenue_loss = 0
    
    total_cleaning_cost = no_of_plants * cleaning_cost_per_plant
    
    alert_val = revenue_loss > total_cleaning_cost
    
    if alert_val:
        print(f'\033[91mAlert triggered {cluster_name}.\033[0m')
        net_benefit_clean_cluster = revenue_loss - total_cleaning_cost - location_cost
    else:
        print(f"\033[92m{cluster_name}\033[0m")
        
    return alert_val, round(net_benefit_clean_cluster + location_cost, 2)

def main():
    clusters_data = load_cluster_data("C:\\Users\\Nelka\\Desktop\\Study\\Startup\\Energy generation\\tarangini\\clusters.json")
    cleaning_cost_per_plant = 50
    revenue_per_unit_production = 4.5
    #Dummy cost of reaching the location
    location_costs = {
        "sangareddy": 100,
        "kandi": 150,
        "patancheruvu" : 200,
        "miyapur" : 200
    }
    # Group clusters by location
    clusters_by_location = {}
    for cluster_name, cluster_data in clusters_data.items():
        location = cluster_data.get("location")
        if location not in clusters_by_location:
            clusters_by_location[location] = {"clusters": [], "total_benefit": 0}
        clusters_by_location[location]["clusters"].append((cluster_name, cluster_data))
    
    
    for location, location_data in clusters_by_location.items():
        print(f"Location: {location}")
        alert_clusters = []
        total_benefit = 0
        all_clusters = [cluster[0] for cluster in location_data["clusters"]]
        total_production_all = 0
        total_capacity_all = 0
        
        for cluster_name, cluster_data in location_data["clusters"]:
            plant_data = cluster_data["plants"]
            no_of_plants = len(plant_data)
            alerts, cluster_production, cluster_capacity = ca.process_plant_data(plant_data)
            
            alert_val, net_benefit_single = assess_cluster(cluster_name, cluster_production, cluster_capacity, cleaning_cost_per_plant, no_of_plants, revenue_per_unit_production, location_costs[location])
            
            if alert_val:
                alert_clusters.append(cluster_name)
                total_benefit += net_benefit_single
            
            total_production_all += cluster_production
            total_capacity_all += cluster_capacity
        
        if not alert_clusters:
            print("No cluster triggers an alert.")
        else:
            if len(alert_clusters) == len(all_clusters):
                print("Alert issued for the entire locality.")
            else:
                revenue_loss_all = max(0, (total_capacity_all - total_production_all) * revenue_per_unit_production)
                total_cleaning_cost_all = sum(len(cluster_data["plants"]) * cleaning_cost_per_plant for _, cluster_data in location_data["clusters"]) - location_costs[location]
                
                if revenue_loss_all > total_cleaning_cost_all:
                    print("Cleaning all clusters in the locality:", all_clusters)
                elif revenue_loss_all < total_cleaning_cost_all:
                    print("Cleaning only the alerted clusters:", alert_clusters)
                else:
                    print("Waiting for more clusters to trigger alerts.")
        print()

if __name__ == "__main__":
    main()
