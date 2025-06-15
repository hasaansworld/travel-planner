import sys
import pandas as pd
from sqlmodel import SQLModel, create_engine
from models import User, City, POICount, UserVist, Category
from database import db_session
from pathlib import Path
from sqlmodel import Session, select
from database import db_engine

def create_db():
    database_url = 'mysql+pymysql://user:password@localhost:3306/travel_planner'
    
    try:
        print("Creating database tables...")
        engine = create_engine(database_url, echo=False)
        SQLModel.metadata.create_all(engine)
        print("✓ All tables created successfully!")
        
        tables = ["users", "city", "poi", "user_freq", "categories"]
        print("\nCreated tables:")
        for table in tables:
            print(f"  - {table}")

        # Create initial data
        print("\nCreating initial data...")
        
        with Session(engine) as session:
            # Create one city
            print("Creating city...")
            city = City(city_name="Somewhere in Japan")
            session.add(city)
            session.commit()
            session.refresh(city)  # Get the generated city_id
            print("✓ City created successfully!")
            
            # Create 125,000 empty users
            print("Creating 125,000 users...")
            batch_size = 1000  # Insert in batches for better performance
            
            for i in range(0, 125000, batch_size):
                users_batch = []
                batch_end = min(i + batch_size, 125000)
                
                for j in range(i, batch_end):
                    user = User()  # Empty user with default values
                    users_batch.append(user)
                
                session.add_all(users_batch)
                session.commit()
                
                # Progress indicator
                if (i + batch_size) % 10000 == 0 or batch_end == 125000:
                    print(f"  Created {batch_end} users...")
            
            print("✓ All 125,000 users created successfully!")
            
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")

def insert_categories():
    """Insert categories into the database if table is empty"""
    
    try:
        with Session(db_engine) as session:
            # Check if categories table is empty
            existing_count = session.exec(select(Category)).first()
            if existing_count:
                print("Categories table is not empty. Skipping insertion.")
                return
            
            # Read category names from file
            script_dir = Path(__file__).parent 
            csv_path = script_dir.parent / 'dataset' / 'POI_datacategories.csv'
            with open(csv_path, 'r', encoding='utf-8') as file:
                category_names = [line.strip() for line in file if line.strip()]
            
            # Insert all categories
            for category_name in category_names:
                new_category = Category(category_name=category_name)
                session.add(new_category)
                print(f"Added: {category_name}")
            
            # Commit all changes
            session.commit()
            
            print(f"\nInserted {len(category_names)} categories successfully!")
            
    except FileNotFoundError:
        print(f"Error: File dataset/POI_datacategories.csv not found")
    except Exception as e:
        print(f"Error: {e}")

def insert_poi_count():
    """
    Reads cell_POIcat.csv and inserts data into poi_count table
    """
    script_dir = Path(__file__).parent 
    csv_path = script_dir.parent / 'dataset' / 'cell_POIcat.csv'
    
    try:
        print("Reading CSV file...")
        df = pd.read_csv(csv_path)
        print(f"✓ Read {len(df)} records from CSV")
        
        print("Inserting data into database...")
        
        with Session(db_engine) as session:
            batch_size = 1000
            total_records = len(df)
            inserted_count = 0
            
            for i in range(0, total_records, batch_size):
                batch_df = df.iloc[i:i + batch_size]
                poi_records = []
                
                for _, row in batch_df.iterrows():
                    poi_record = POICount(
                        x=int(row['x']),
                        y=int(row['y']),
                        poi_category_id=int(row['POIcategory']),
                        poi_count=int(row['POI_count']),
                        city_id=1
                    )
                    poi_records.append(poi_record)
                
                session.add_all(poi_records)
                session.commit()
                
                inserted_count += len(poi_records)
                
                if inserted_count % 10000 == 0 or inserted_count == total_records:
                    progress = (inserted_count / total_records) * 100
                    print(f"  Progress: {inserted_count}/{total_records} records ({progress:.1f}%)")
        
        print(f"✓ Successfully inserted {inserted_count} POI count records!")
        
    except Exception as e:
        print(f"❌ Error inserting POI count data: {str(e)}")
        raise


def last_n_rows(file, n=10):
    with open(file) as f:
        total = sum(1 for _ in f) - 1
    return pd.read_csv(file, skiprows=range(1, max(0, total-n)+1))

def display_file1():
    try:
        print("Reading yjmob100k-dataset1...")
        script_dir = Path(__file__).parent 
        csv_path = script_dir.parent / 'dataset' / 'yjmob100k-dataset1.csv'
        df = last_n_rows(csv_path, 10)
        
        print(f"File shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"Columns: {', '.join(df.columns.tolist())}")
        print("\nLast 10 rows:")
        print(df.head(10))
        
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
    
    if function_name == "setup":
        create_db()
        insert_categories()
    elif function_name == "create_db":
        create_db()
    elif function_name == "display_file1":
        display_file1()
    elif function_name == "display_file2":
        display_file2()
    elif function_name == "insert_categories":
        insert_categories()
    elif function_name == "insert_poi_count":
        insert_poi_count()
    else:
        print(f"Unknown function: {function_name}")
        print("Available functions: create_db, display_file1, display_file2")