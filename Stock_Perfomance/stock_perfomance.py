import os
import yaml
import pandas as pd
import mysql.connector
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# Database Connection
DB_URL = "mysql+mysqlconnector://root:root@localhost/stock_db"  # Replace with your database credentials
engine = create_engine(DB_URL)

def extract_yaml_to_csv(yaml_folder):
    """ Extract data from YAML files and save to CSV """
    all_data = []
    yaml_folder = yaml_folder.replace("\\", "/")  # Fix path formatting
    if not os.path.exists(yaml_folder):
        print(f"Error: The folder '{yaml_folder}' does not exist. Provide the correct directory path.")
        return pd.DataFrame()
    
    for month_folder in os.listdir(yaml_folder):
        month_path = os.path.join(yaml_folder, month_folder).replace("\\", "/")
        if os.path.isdir(month_path):
            for file in os.listdir(month_path):
                if file.endswith(".yaml"):
                    with open(os.path.join(month_path, file).replace("\\", "/"), 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data:
                            all_data.append(data)
    df = pd.DataFrame(all_data)
    df.to_csv("stock_data.csv", index=False, encoding='utf-8')  # Replace with your preferred save location
    return df

def load_data_to_db(csv_file):
    """ Load CSV data into MySQL database """
    csv_file = csv_file.replace("\\", "/")  # Fix path formatting
    if not os.path.exists(csv_file):
        print(f"Error: The file '{csv_file}' does not exist. Provide the correct file path.")
        return
    df = pd.read_csv(csv_file, encoding='utf-8')
    df.to_sql('stocks', con=engine, if_exists='replace', index=False)

def analyze_stock_data():
    """ Analyze and visualize stock data """
    df = pd.read_sql('SELECT * FROM stocks', con=engine)
    if df.empty:
        print("Error: No data found in the database. Ensure the correct database is used.")
        return
    df['daily_return'] = df['Close'].pct_change()
    
    top_gainers = df.groupby('Symbol')[['daily_return']].sum().nlargest(10, 'daily_return')
    top_losers = df.groupby('Symbol')[['daily_return']].sum().nsmallest(10, 'daily_return')
    
    plt.figure(figsize=(10,5))
    sns.barplot(x=top_gainers.index, y=top_gainers['daily_return'], color='green')
    plt.title("Top 10 Gainers")
    plt.xticks(rotation=45)
    plt.show()
    
    plt.figure(figsize=(10,5))
    sns.barplot(x=top_losers.index, y=top_losers['daily_return'], color='red')
    plt.title("Top 10 Losers")
    plt.xticks(rotation=45)
    plt.show()

def stock_dashboard():
    """ Streamlit Dashboard """
    st.title("Stock Analysis Dashboard")
    df = pd.read_sql('SELECT * FROM stocks', con=engine)
    if df.empty:
        st.error("No data available in the database. Check if the correct database is connected.")
        return
    st.dataframe(df)
    
    st.subheader("Top Gainers & Losers")
    col1, col2 = st.columns(2)
    with col1:
        gainers = df.nlargest(10, 'daily_return')
        st.bar_chart(gainers.set_index('Symbol')['daily_return'])
    with col2:
        losers = df.nsmallest(10, 'daily_return')
        st.bar_chart(losers.set_index('Symbol')['daily_return'])

if __name__ == "__main__":
    yaml_folder = r"D:/Guvi/My-Projects-Work/My-Projects-Work/data/2023-10"  # Replace with actual YAML directory
    csv_file = r"D:/Guvi/My-Projects-Work/My-Projects-Work/processed_data/stock_data.csv"  # Replace with actual CSV path
    df = extract_yaml_to_csv(yaml_folder)
    if not df.empty:
        load_data_to_db(csv_file)
        analyze_stock_data()
        stock_dashboard()
