# import numpy as np
# import pandas as pd 
# import matplotlib.pyplot as plt
# import seaborn as sns 
# import streamlit as st 
# import tensorflow as tf

# import pandas as pd



# df = pd.read_csv(r"E:\Final Project\makeup.csv")
# df.head()

# print("Null values before cleaning :\n", df.isnull().sum())
# #----------Handel Missing Values--------
# df['brand'] = df['brand'].fillna("Unknown")
# df['description'] = df['description'].fillna("No description")
# df['category'] = df['category'].fillna("Other")
# df['price'] = df['price'].fillna(df['price'].median())
# df['currency'] = df['currency'].fillna("USD")

# #---------- Check after handeling missing values-----------
# print("Missing values after handling:")
# print(df.isnull().sum())

# #---------Data Cleaning: Remove rows where Brand or Category is missing---------
# df_clean = df.dropna(subset=['brand', 'category'])


# #---------------Filtering: Keep only 'lipstick' and 'foundation' as per project scope-----------------
# #------------We use NumPy logic to help filter or check unique types------------------

# categories_to_keep = ['lipstick', 'foundation']
# df_filtered = df_clean[df_clean['category'].isin(categories_to_keep)]

# df_filtered.to_csv('cleaned_makeup_data.csv', index=False)

# print(f"Cleaning complete! Total products left: {len(df_filtered)}")
# print(df_filtered.head())

# # Create a count plot of the categories
# plt.figure(figsize=(10,6))
# sns.countplot(x='category', data=df_filtered, palette='viridis')
# plt.title('Distribution of Lipstick vs Foundation')
# plt.savefig('data_distribution.png') # Save this to show your teacher!
# plt.show()

# ============================================================
# Project: BeautyReel AI - Phase 1: Data Handling & Cleaning
# Requirements: NumPy, Pandas, Matplotlib, Seaborn
# Instructor: Javeria Hassan (Batch 09 - SMIT)
# ========================================================

import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns 
import os

# 1. LOAD DATA
print("--- Step 1: Loading Data ---")
if not os.path.exists("makeup.csv"):
    print("Error: makeup.csv file not found. Please check the folder!")
else:
    df = pd.read_csv("makeup.csv")
    
    # Drop Unnamed columns to maintain clean data structure
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # 2. INITIAL NULL CHECK
    print("\nInitial Null values check:\n", df.isnull().sum())

    # 3. FILTER AND RENAME CATEGORIES
    print("\n--- Step 2: Filtering and Renaming Categories ---")
    # Updated target categories: Replacing highlighter with pencil
    target_cats = np.array(['lipstick', 'powder', 'pencil', 'concealer'])
    
    # Filter dataset for selected categories
    df_filtered = df[df['category'].str.lower().isin(target_cats)].copy()

    # Transformation: Rename 'pencil' to 'lip pencil' for better display
    df_filtered['category'] = df_filtered['category'].replace('pencil', 'lip pencil')
    
    # Update our target list for visualization to reflect the name change
    display_cats = np.array(['lipstick', 'powder', 'lip pencil', 'concealer'])

    # 4. DEALING WITH OUTLIERS (IQR Method using NumPy)
    print("\n--- Step 3: Handling Outliers in Price ---")
    # Statistical calculation using NumPy percentiles
    Q1 = np.percentile(df_filtered['price'].dropna(), 25)
    Q3 = np.percentile(df_filtered['price'].dropna(), 75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Capping outliers to the boundaries using np.where
    df_filtered['price'] = np.where(df_filtered['price'] > upper_bound, upper_bound, df_filtered['price'])
    df_filtered['price'] = np.where(df_filtered['price'] < lower_bound, lower_bound, df_filtered['price'])
    
    print(f"Outlier handling complete. Capping Threshold: {upper_bound:.2f}")

    # 5. DATA IMPUTATION (Filling Missing Values)
    print("\n--- Step 4: Filling Missing Values ---")
    
    # Handling textual missing data
    df_filtered['brand'] = df_filtered['brand'].fillna("Unknown")
    df_filtered['name'] = df_filtered['name'].fillna("Generic Product")
    df_filtered['description'] = df_filtered['description'].fillna("No description available")
    
    # Handling Currency using Mode (Most frequent value)
    if not df_filtered['currency'].mode().empty:
        df_filtered['currency'] = df_filtered['currency'].fillna(df_filtered['currency'].mode()[0])
    else:
        df_filtered['currency'] = df_filtered['currency'].fillna("USD")

    # Handling Price using Mean - [NumPy Requirement]
    mean_price = np.round(np.mean(df_filtered['price']), 2)
    df_filtered['price'] = df_filtered['price'].fillna(mean_price)

    # 6. FINAL VERIFICATION
    print("\nFinal verification of missing values:")
    print(df_filtered.isnull().sum())
    print(f"\nFinal count of cleaned products: {len(df_filtered)}")

    # 7. EXPORT DATA
    df_filtered.to_csv('final_cleaned_makeup.csv', index=False)
    print("\nCleaned data exported successfully.")

    # 8. VISUALIZATION
    print("\n--- Step 5: Generating Visualization Reports ---")
    
    # Chart 1: Category Count (Showing 'lip pencil' instead of 'pencil')
    plt.figure(figsize=(10,5))
    sns.set_style("darkgrid")
    sns.countplot(x='category', data=df_filtered, palette='magma', order=display_cats)
    plt.title('Makeup Product Distribution')
    plt.savefig('category_distribution.png')
    plt.show()

    # Chart 2: Price Distribution Check
    plt.figure(figsize=(8,4))
    sns.boxplot(x=df_filtered['price'], color='cyan')
    plt.title('Price Distribution after Outlier Capping')
    plt.savefig('price_boxplot_cleaned.png')
    plt.show()

    
