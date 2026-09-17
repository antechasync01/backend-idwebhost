import os
import sys

# Add parent directory to sys.path to allow imports from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.scheduler import generate_weekly_sales_analysis, generate_monthly_sales_analysis

def run():
    print("Triggering Weekly Sales Analysis (7-day)...")
    generate_weekly_sales_analysis()
    
    print("\nTriggering Monthly Sales Analysis (30-day)...")
    generate_monthly_sales_analysis()
    
    print("\nAnalysis generation complete!")

if __name__ == "__main__":
    run()
