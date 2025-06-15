import sys
import pandas as pd
from sqlmodel import SQLModel, create_engine
from models import User, City, POI, UserFrequency
from pathlib import Path

def create_db():
    database_url = 'mysql://root:password@localhost:3306/travel'
    
    try:
        print("Creating database tables...")
        engine = create_engine(database_url, echo=False)
        SQLModel.metadata.create_all(engine)
        print("✓ All tables created successfully!")
        
        tables = ["users", "city", "poi", "user_freq"]
        print("\nCreated tables:")
        for table in tables:
            print(f"  - {table}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")

def display_file1():
    try:
        print("Reading yjmob100k-dataset1...")
        script_dir = Path(__file__).parent 
        csv_path = script_dir.parent / 'dataset' / 'yjmob100k-dataset1.csv'
        df = pd.read_csv(csv_path, nrows=5000)
        
        print(f"File shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"Columns: {', '.join(df.columns.tolist())}")
        print("\nFirst 5000 rows:")
        print(df.head(5000))
        
    except FileNotFoundError:
        print("❌ yjmob100k-dataset1.csv not found")
    except Exception as e:
        print(f"❌ Error reading yjmob100k-dataset1.csv: {str(e)}")

def display_file2():
    try:
        print("Reading yjmob100k-dataset2.csv...")
        script_dir = Path(__file__).parent 
        csv_path = script_dir.parent / 'dataset' / 'yjmob100k-dataset2.csv'
        df = pd.read_csv(csv_path, nrows=100)
        
        print(f"File shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"Columns: {', '.join(df.columns.tolist())}")
        print("\nFirst 100 rows:")
        print(df.head(100))
        
    except FileNotFoundError:
        print("❌ yjmob100k-dataset2.csv not found")
    except Exception as e:
        print(f"❌ Error reading yjmob100k-dataset2.csv: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python commands.py <function_name>")
        print("Available functions: create_db, display_file1, display_file2")
        sys.exit(1)
    
    function_name = sys.argv[1]
    
    if function_name == "create_db":
        create_db()
    elif function_name == "display_file1":
        display_file1()
    elif function_name == "display_file2":
        display_file2()
    else:
        print(f"Unknown function: {function_name}")
        print("Available functions: create_db, display_file1, display_file2")