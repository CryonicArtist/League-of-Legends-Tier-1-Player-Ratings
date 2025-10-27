import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler

def analyze_lol_data():
    """
    Analyzes LoL player stats from a CSV to generate a "FIFA-style" rating.
    """
    
    # --- Configuration ---
    datafile = 'LoLData.xlsx - Sheet1.csv'
    min_games = 15
    
    # Define the stats and weights for the rating
    # (Column Name: Weight)
    stat_weights = {
        'Win Rate': 0.25,
        'KDA': 0.25,
        'GPM': 0.15,
        'DMG%': 0.15,
        'GD@15': 0.10,
        'VSPM': 0.10
    }
    key_stats = list(stat_weights.keys())

    # --- 1. Load Data ---
    print(f"Loading data from {datafile}...")
    try:
        # Read the CSV. 
        # index_col=0 sets the first column (player name) as the index.
        # na_values='-' tells pandas to treat '-' as missing data.
        df = pd.read_csv(datafile, index_col=0, na_values='-')
    except FileNotFoundError:
        print(f"Error: File not found at {datafile}")
        print("Please make sure the file is in the same directory as the script.")
        return
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return

    # --- 2. Clean Data ---
    
    # The second column in the file is unnamed and full of NaN, let's drop it.
    # It gets named 'Unnamed: 1' by pandas.
    if 'Unnamed: 1' in df.columns:
        df = df.drop(columns=['Unnamed: 1'])
        
    # Set the index name (which is the player name)
    df.index.name = 'Player'

    # Ensure all key stat columns are numeric, coercing errors to NaN
    for col in key_stats:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            print(f"Warning: Column '{col}' not found in the CSV. It will be ignored.")
            stat_weights.pop(col) # Remove from our calculation
            
    # --- 3. Filter and Impute ---
    
    # Filter out players with too few games
    original_count = len(df)
    df = df[df['Games'] >= min_games].copy()
    print(f"Filtered {original_count - len(df)} players with fewer than {min_games} games. Analyzing {len(df)} players.")

    # Impute (fill) missing data with the mean of that stat
    # This prevents missing stats from ruining a player's rating
    for col in key_stats:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].mean())

    # --- 4. Normalize Stats (Z-score) ---
    # This rescales all stats to a common scale
    scaler = StandardScaler()
    df_normalized = df[key_stats].copy()
    df_normalized.loc[:, :] = scaler.fit_transform(df_normalized)

    # --- 5. Calculate Weighted Score ---
    # Multiply each normalized stat by its weight and sum them up
    df['CompositeScore'] = 0
    for col, weight in stat_weights.items():
        df['CompositeScore'] += df_normalized[col] * weight

    # --- 6. Rescale to 0-100 Rating ---
    # Use MinMaxScaler to convert the composite Z-score to a 0-100 "FIFA-style" rating
    min_max_scaler = MinMaxScaler(feature_range=(0, 100))
    df['PlayerRating'] = min_max_scaler.fit_transform(df[['CompositeScore']])

    # --- 7. Display Results ---
    # Sort by the new rating to find the best players
    df_sorted = df.sort_values(by='PlayerRating', ascending=False)
    
    # Define columns to display
    display_cols = ['PlayerRating', 'Games', 'Win Rate', 'KDA', 'GPM', 'DMG%']
    
    print("\n--- Top 20 Highest Rated Players ---")
    print(df_sorted[display_cols].head(20).to_string())

if __name__ == "__main__":
    analyze_lol_data()