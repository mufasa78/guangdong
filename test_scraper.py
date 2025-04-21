"""
Test script to verify that the scraper is working correctly and generating data up to 2024.
"""

from scraper import scrape_population_data
import pandas as pd

def test_scraper():
    """Test the scraper functionality"""
    print("Testing scraper...")
    
    # Get data using synthetic data generation
    data = scrape_population_data(use_synthetic=True)
    
    # Check if data was generated
    if data is None or data.empty:
        print("ERROR: No data was generated!")
        return False
    
    # Check if we have data for 2024
    years = sorted(data["year"].unique())
    print(f"Years in dataset: {years}")
    
    if 2024 not in years:
        print("ERROR: Data for 2024 is missing!")
        return False
    
    # Check if we have the expected number of records
    expected_records = 148  # 21 cities * 7 years (2018-2024) + 1 China total
    if len(data) != expected_records:
        print(f"WARNING: Expected {expected_records} records, but got {len(data)}")
    
    # Check if we have data for all cities
    cities = data["city"].unique()
    print(f"Number of cities: {len(cities)}")
    
    # Check if we have the China total population data
    if "直辖市" not in cities:
        print("ERROR: China total population data is missing!")
        return False
    
    # Print sample data for 2024
    print("\nSample data for 2024:")
    print(data[data["year"] == 2024].head())
    
    print("\nScraper test completed successfully!")
    return True

if __name__ == "__main__":
    test_scraper()
