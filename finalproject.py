

# #working well but earlier version
# import streamlit as st
# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier

# # Load data from Excel
# def load_data(file_path):
#     df = pd.read_excel(file_path)

#     # Identify available time slots dynamically
#     time_slots = sorted(set(col.split("_")[-1] for col in df.columns if "PPHPD" in col))

#     # Define congestion labels for each time slot
#     for time in time_slots:
#         df[f'Rush_Boarding_{time}'] = (df[f'Boarding_{time}'] > 1000).astype(int)
#         df[f'Rush_Alighting_{time}'] = (df[f'Alighting_{time}'] > 1000).astype(int)

#     return df, time_slots

# # Train ML models for each time slot
# def train_ml_models(df, time_slots):
#     models_boarding = {}
#     models_alighting = {}

#     for time in time_slots:
#         # Train model for Boarding congestion
#         X_boarding = df[[f'Boarding_{time}', f'PPHPD_{time}']]
#         y_boarding = df[f'Rush_Boarding_{time}']
#         X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(X_boarding, y_boarding, test_size=0.2, random_state=42)
#         model_boarding = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
#         model_boarding.fit(X_train_b, y_train_b)
#         models_boarding[time] = model_boarding

#         # Train model for Alighting congestion
#         X_alighting = df[[f'Alighting_{time}', f'PPHPD_{time}']]
#         y_alighting = df[f'Rush_Alighting_{time}']
#         X_train_a, X_test_a, y_train_a, y_test_a = train_test_split(X_alighting, y_alighting, test_size=0.2, random_state=42)
#         model_alighting = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
#         model_alighting.fit(X_train_a, y_train_a)
#         models_alighting[time] = model_alighting

#     return models_boarding, models_alighting

# # Predict congestion status for Boarding or Alighting
# def predict_rush(model, station_data):
#     return model.predict([station_data])[0]

# # Function to compute distance between stations
# def compute_distance(df, station1, station2):
#     station_distances = df.set_index('Station')['Distance from SBC'].to_dict()
    
#     if station1 in station_distances and station2 in station_distances:
#         return abs(station_distances[station1] - station_distances[station2])
    
#     return None

# # Function to suggest the **nearest less-crowded alternate station**
# def suggest_alternate_station(station, direction, time, df, boarding_type):
#     rush_column = f'Rush_Boarding_{time}' if boarding_type == 'Boarding' else f'Rush_Alighting_{time}'
    
#     # Get the station data
#     station_data = df[(df['Station'] == station) & (df['Direction'] == direction)]
    
#     if not station_data.empty and station_data.iloc[0][rush_column] == 1:
#         st.write(f"⚠️ {station} ({direction}) is crowded for {boarding_type}. Finding nearest alternate station...")
        
#         # Get list of stations in the same direction
#         direction_stations = df[df['Direction'] == direction].sort_values('Distance from SBC')

#         # Find current station index
#         station_index = direction_stations[direction_stations['Station'] == station].index[0]
        
#         # Look for the nearest alternate station in the same direction
#         alternate_station = None
#         min_distance = float('inf')

#         for idx in range(station_index + 1, len(direction_stations)):  # Checking next stations
#             candidate_station = direction_stations.iloc[idx]
            
#             if candidate_station[rush_column] == 0:  # Less crowded station found
#                 distance = compute_distance(df, station, candidate_station['Station'])
                
#                 if distance is not None and distance < min_distance:
#                     alternate_station = candidate_station['Station']
#                     min_distance = distance
        
#         # Display result
#         if alternate_station:
#             st.write(f"✅ Suggested alternate station: **{alternate_station}** (🚆 {min_distance} km away)")
#         else:
#             st.write("❌ No alternate station available nearby.")
#     else:
#         st.write(f"✅ {station} ({direction}) is not crowded for {boarding_type}.")

# # Check congestion and apply ML model
# def check_rush_status(station, direction, time, boarding_type, df, models_boarding, models_alighting):
#     station_data = df[(df['Station'] == station) & (df['Direction'] == direction)]
    
#     if not station_data.empty:
#         station_row = station_data.iloc[0]
        
#         # Select appropriate model based on boarding type
#         model = models_boarding[time] if boarding_type == "Boarding" else models_alighting[time]
#         features = [f"{boarding_type}_{time}", f"PPHPD_{time}"]
        
#         predicted_rush = predict_rush(model, station_row[features])
        
#         if predicted_rush == 1:
#             st.write(f"⚠️ {station} ({direction}) is **predicted to be crowded** for {boarding_type} at {time}.")
#             suggest_alternate_station(station, direction, time, df, boarding_type)
#         else:
#             st.write(f"✅ {station} ({direction}) is **not predicted to be crowded** for {boarding_type} at {time}.")
#     else:
#         st.write("❌ Station data not found.")

# # Streamlit UI
# st.title("🚉 Peak Hour Traffic Analysis with ML & Distance Calculation")

# file_path = st.file_uploader("📂 Upload Excel File", type=["xlsx"])
# if file_path:
#     df, time_slots = load_data(file_path)
    
#     if df is not None:
#         models_boarding, models_alighting = train_ml_models(df, time_slots)
        
#         if models_boarding and models_alighting:
#             direction = st.radio("🔄 Select Direction", df['Direction'].unique())
#             station = st.selectbox("📍 Select a Station", df[df['Direction'] == direction]['Station'].unique())
#             time = st.selectbox("⏰ Select a Time Slot", time_slots)
#             boarding_type = st.radio("🚶 Boarding or Alighting?", ["Boarding", "Alighting"])
            
#             if st.button("🔍 Check Station"):
#                 check_rush_status(station, direction, time, boarding_type, df, models_boarding, models_alighting)
            
#             station2 = st.selectbox("📍 Select another station to calculate distance", df['Station'].unique())
#             if st.button("📏 Calculate Distance"):
#                 distance = compute_distance(df, station, station2)
#                 if distance is not None:
#                     st.write(f"🛤️ Distance between {station} and {station2}: **{distance} km**")
#                 else:
#                     st.write("❌ Distance calculation failed.")



# # #Working fine and well
# import streamlit as st
# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import accuracy_score

# # Load data from Excel
# def load_data(file_path):
#     df = pd.read_excel(file_path)

#     # Identify available time slots dynamically
#     time_slots = sorted(set(col.split("_")[-1] for col in df.columns if "PPHPD" in col))

#     # Define congestion labels for each time slot
#     for time in time_slots:
#         df[f'Rush_Boarding_{time}'] = (df[f'Boarding_{time}'] > 1000).astype(int)
#         df[f'Rush_Alighting_{time}'] = (df[f'Alighting_{time}'] > 1000).astype(int)

#     return df, time_slots

# # Train ML models and compute accuracy
# def train_ml_models(df, time_slots):
#     models_boarding = {}
#     models_alighting = {}
#     accuracy_boarding = {}
#     accuracy_alighting = {}

#     for time in time_slots:
#         # Train model for Boarding congestion
#         X_boarding = df[[f'Boarding_{time}', f'PPHPD_{time}']]
#         y_boarding = df[f'Rush_Boarding_{time}']
#         X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(X_boarding, y_boarding, test_size=0.2, random_state=42)
#         model_boarding = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
#         model_boarding.fit(X_train_b, y_train_b)
#         y_pred_b = model_boarding.predict(X_test_b)
#         accuracy_boarding[time] = accuracy_score(y_test_b, y_pred_b)  # Store accuracy
#         models_boarding[time] = model_boarding

#         # Train model for Alighting congestion
#         X_alighting = df[[f'Alighting_{time}', f'PPHPD_{time}']]
#         y_alighting = df[f'Rush_Alighting_{time}']
#         X_train_a, X_test_a, y_train_a, y_test_a = train_test_split(X_alighting, y_alighting, test_size=0.2, random_state=42)
#         model_alighting = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
#         model_alighting.fit(X_train_a, y_train_a)
#         y_pred_a = model_alighting.predict(X_test_a)
#         accuracy_alighting[time] = accuracy_score(y_test_a, y_pred_a)  # Store accuracy
#         models_alighting[time] = model_alighting

#     return models_boarding, models_alighting, accuracy_boarding, accuracy_alighting

# # Predict congestion status for Boarding or Alighting
# def predict_rush(model, station_data):
#     return model.predict([station_data])[0]

# # Function to compute distance between stations
# def compute_distance(df, station1, station2):
#     station_distances = df.set_index('Station')['Distance from SBC'].to_dict()
    
#     if station1 in station_distances and station2 in station_distances:
#         return abs(station_distances[station1] - station_distances[station2])
    
#     return None

# # Function to find the nearest station and check its congestion
# def find_nearest_station(station, direction, df, time, boarding_type):
#     direction_stations = df[df['Direction'] == direction].sort_values('Distance from SBC')

#     station_index = direction_stations[direction_stations['Station'] == station].index[0]
    
#     if station_index < len(direction_stations) - 1:
#         nearest_station = direction_stations.iloc[station_index + 1]
#         rush_column = f'Rush_Boarding_{time}' if boarding_type == 'Boarding' else f'Rush_Alighting_{time}'
#         return nearest_station['Station'], nearest_station[rush_column]
    
#     return None, None

# # Function to suggest an alternate station
# def suggest_alternate_station(station, direction, time, df, boarding_type):
#     rush_column = f'Rush_Boarding_{time}' if boarding_type == 'Boarding' else f'Rush_Alighting_{time}'
    
#     station_data = df[(df['Station'] == station) & (df['Direction'] == direction)]
    
#     if not station_data.empty and station_data.iloc[0][rush_column] == 1:
#         st.write(f"⚠️ {station} ({direction}) is crowded for {boarding_type}. Finding nearest alternate station...")
        
#         # Get list of stations in the same direction
#         direction_stations = df[df['Direction'] == direction].sort_values('Distance from SBC')

#         # Find current station index
#         station_index = direction_stations[direction_stations['Station'] == station].index[0]
        
#         # Look for the nearest alternate station
#         alternate_station = None
#         min_distance = float('inf')

#         for idx in range(station_index + 1, len(direction_stations)):  # Checking next stations
#             candidate_station = direction_stations.iloc[idx]
            
#             if candidate_station[rush_column] == 0:  # Less crowded station found
#                 distance = compute_distance(df, station, candidate_station['Station'])
                
#                 if distance is not None and distance < min_distance:
#                     alternate_station = candidate_station['Station']
#                     min_distance = distance
        
#         # Display result
#         if alternate_station:
#             st.write(f"✅ Suggested alternate station: **{alternate_station}** (🚆 {min_distance} km away)")
#         else:
#             st.write("❌ No alternate station available nearby.")
#     else:
#         st.write(f"✅ {station} ({direction}) is not crowded for {boarding_type}.")

# # Check congestion and apply ML model
# def check_rush_status(station, direction, time, boarding_type, df, models_boarding, models_alighting):
#     station_data = df[(df['Station'] == station) & (df['Direction'] == direction)]
    
#     if not station_data.empty:
#         station_row = station_data.iloc[0]
        
#         # Select appropriate model based on boarding type
#         model = models_boarding[time] if boarding_type == "Boarding" else models_alighting[time]
#         features = [f"{boarding_type}_{time}", f"PPHPD_{time}"]
        
#         predicted_rush = predict_rush(model, station_row[features])
        
#         if predicted_rush == 1:
#             st.write(f"⚠️ {station} ({direction}) is **predicted to be crowded** for {boarding_type} at {time}.")
#             suggest_alternate_station(station, direction, time, df, boarding_type)
#         else:
#             st.write(f"✅ {station} ({direction}) is **not predicted to be crowded** for {boarding_type} at {time}.")
        
#         # Find nearest station and check congestion
#         nearest_station, nearest_rush = find_nearest_station(station, direction, df, time, boarding_type)
#         if nearest_station:
#             status = "Crowded" if nearest_rush == 1 else "Not Crowded"
#             st.write(f"🚉 Nearest station: **{nearest_station}** ({status})")
#     else:
#         st.write("❌ Station data not found.")

# # Streamlit UI
# st.title("🚉 Peak Hour Traffic Analysis with ML & Distance Calculation")

# file_path = st.file_uploader("📂 Upload Excel File", type=["xlsx"])
# if file_path:
#     df, time_slots = load_data(file_path)
    
#     if df is not None:
#         models_boarding, models_alighting, accuracy_boarding, accuracy_alighting = train_ml_models(df, time_slots)
        
#         if models_boarding and models_alighting:
#             direction = st.radio("🔄 Select Direction", df['Direction'].unique())
#             station = st.selectbox("📍 Select a Station", df[df['Direction'] == direction]['Station'].unique())
#             time = st.selectbox("⏰ Select a Time Slot", time_slots)
#             boarding_type = st.radio("🚶 Boarding or Alighting?", ["Boarding", "Alighting"])
            
#             if st.button("🔍 Check Station"):
#                 check_rush_status(station, direction, time, boarding_type, df, models_boarding, models_alighting)
            
#             st.write(f"📊 **Model Accuracy:**")
#             st.write(f"✅ Boarding Model: {accuracy_boarding[time]:.2%}")
#             st.write(f"✅ Alighting Model: {accuracy_alighting[time]:.2%}")





# import streamlit as st
# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


# # Custom CSS for better UI
# st.markdown("""
#     <style>
#         body { background-color: #f7f9fc; }
#         .title { font-size: 30px; font-weight: bold; color: #2c3e50; text-align: center; padding-top: 10px; }
#         .subheader { font-size: 16px; color: #34495e; text-align: center; margin-bottom: 20px; }
        
#         .success { color: #27ae60; font-weight: bold; font-size: 18px; }
#         .danger { color: #c0392b; font-weight: bold; font-size: 18px; }
#         .highlight { font-size: 20px; font-weight: bold; }
#         .sidebar .block-container { padding-top: 20px; }
#         .stButton > button { width: 100%; border-radius: 8px; padding: 12px; font-size: 16px; }
#     </style>
# """, unsafe_allow_html=True)

# # Load data from Excel
# def load_data(file_path):
#     df = pd.read_excel(file_path)

#     # Identify available time slots dynamically
#     time_slots = sorted(set(col.split("_")[-1] for col in df.columns if "PPHPD" in col))

#     # Define congestion labels for each time slot
#     for time in time_slots:
#         df[f'Rush_Boarding_{time}'] = (df[f'Boarding_{time}'] > 1000).astype(int)
#         df[f'Rush_Alighting_{time}'] = (df[f'Alighting_{time}'] > 1000).astype(int)

#     return df, time_slots

# # Train ML models
# def train_ml_models(df, time_slots):
#     models_boarding, models_alighting = {}, {}
#     accuracy_boarding, accuracy_alighting = {}, {}

#     for time in time_slots:
#         # Boarding model
#         X_boarding = df[[f'Boarding_{time}', f'PPHPD_{time}']]
#         y_boarding = df[f'Rush_Boarding_{time}']
#         X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(X_boarding, y_boarding, test_size=0.2, random_state=42)
#         model_boarding = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
#         model_boarding.fit(X_train_b, y_train_b)
#         accuracy_boarding[time] = accuracy_score(y_test_b, model_boarding.predict(X_test_b))
#         models_boarding[time] = model_boarding

#         # Alighting model
#         X_alighting = df[[f'Alighting_{time}', f'PPHPD_{time}']]
#         y_alighting = df[f'Rush_Alighting_{time}']
#         X_train_a, X_test_a, y_train_a, y_test_a = train_test_split(X_alighting, y_alighting, test_size=0.2, random_state=42)
#         model_alighting = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
#         model_alighting.fit(X_train_a, y_train_a)
#         accuracy_alighting[time] = accuracy_score(y_test_a, model_alighting.predict(X_test_a))
#         models_alighting[time] = model_alighting

#     return models_boarding, models_alighting, accuracy_boarding, accuracy_alighting

# # Predict rush
# def predict_rush(model, station_data):
#     return model.predict([station_data])[0]

# # Compute distance between stations
# def compute_distance(df, station1, station2):
#     station_distances = df.set_index('Station')['Distance from SBC'].to_dict()
#     return abs(station_distances.get(station1, 0) - station_distances.get(station2, 0))

# # Suggest an alternate station
# def suggest_alternate_station(station, direction, time, df, boarding_type):
#     rush_column = f'Rush_Boarding_{time}' if boarding_type == 'Boarding' else f'Rush_Alighting_{time}'
    
#     if df.loc[df['Station'] == station, rush_column].values[0] == 1:
#         st.write(f"⚠️ {station} is crowded. Finding nearest less crowded station...")

#         direction_stations = df[df['Direction'] == direction].sort_values('Distance from SBC')
#         station_index = direction_stations[direction_stations['Station'] == station].index[0]
        
#         for idx in range(station_index + 1, len(direction_stations)):  
#             candidate_station = direction_stations.iloc[idx]
#             if candidate_station[rush_column] == 0:  
#                 distance = compute_distance(df, station, candidate_station['Station'])
#                 st.write(f"✅ Suggested: **{candidate_station['Station']}** ({distance} km away)")
#                 return

#         st.write("❌ No alternate station available.")

# # Check congestion status
# def check_rush_status(station, direction, time, boarding_type, df, models_boarding, models_alighting):
#     station_row = df[(df['Station'] == station) & (df['Direction'] == direction)].iloc[0]
#     model = models_boarding[time] if boarding_type == "Boarding" else models_alighting[time]
#     features = [f"{boarding_type}_{time}", f"PPHPD_{time}"]
#     predicted_rush = predict_rush(model, station_row[features])

#     st.markdown('<div class="info-box">', unsafe_allow_html=True)
#     if predicted_rush == 1:
#         st.markdown(f'<p class="danger highlight">⚠️ {station} is predicted to be crowded.</p>', unsafe_allow_html=True)
#         suggest_alternate_station(station, direction, time, df, boarding_type)
#     else:
#         st.markdown(f'<p class="success highlight">✅ {station} is not predicted to be crowded.</p>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)

# # Streamlit UI
# st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)  
# st.sidebar.title("🚆 Smart Station Advisor")

# file_path = st.sidebar.file_uploader("📂 Upload Excel File", type=["xlsx"])

# if file_path:
#     df, time_slots = load_data(file_path)
#     models_boarding, models_alighting, accuracy_boarding, accuracy_alighting = train_ml_models(df, time_slots)

#     st.markdown('<p class="title">🚉 Peak Hour Traffic Prediction</p>', unsafe_allow_html=True)
#     st.markdown('<p class="subheader">Check congestion status and find alternate stations</p>', unsafe_allow_html=True)

#     with st.sidebar:
#         direction = st.radio("🔄 Select Direction", df['Direction'].unique())
#         station = st.selectbox("📍 Select a Station", df[df['Direction'] == direction]['Station'].unique())
#         time = st.selectbox("⏰ Select a Time Slot", time_slots)
#         boarding_type = st.radio("🚶 Boarding or Alighting?", ["Boarding", "Alighting"])
#         check_button = st.button("🔍 Check Station")

#     if check_button:
#         check_rush_status(station, direction, time, boarding_type, df, models_boarding, models_alighting)

#     st.markdown('<p class="title">📊 Model Performance</p>', unsafe_allow_html=True)
#     col1, col2 = st.columns(2)
#     col1.metric("🚆 Boarding Accuracy", f"{accuracy_boarding[time]*100:.2f}%")
#     col2.metric("🚉 Alighting Accuracy", f"{accuracy_alighting[time]*100:.2f}%")














# import streamlit as st
# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
# import plotly.graph_objects as go
# import plotly.express as px
# from datetime import datetime

# # Ultra-modern CSS with glassmorphism and animations
# st.markdown("""
#     <style>
#         @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
        
#         * { 
#             font-family: 'Poppins', sans-serif;
#             transition: all 0.3s ease;
#         }
        
#         .stApp {
#             background: linear-gradient(135deg, #0a0a0a 0%, #1a0a2e 30%, #16213e 60%, #0f0f23 100%);
#             background-attachment: fixed;
#         }
        
#         .main > div {
#             background: rgba(0, 0, 0, 0.4);
#             backdrop-filter: blur(10px);
#             border-radius: 30px;
#             padding: 30px;
#             border: 1px solid rgba(139, 92, 246, 0.2);
#         }
        
#         /* Hero Section */
#         .hero-title {
#             font-size: 56px;
#             font-weight: 800;
#             text-align: center;
#             background: linear-gradient(135deg, #a78bfa 0%, #c084fc 50%, #e879f9 100%);
#             -webkit-background-clip: text;
#             -webkit-text-fill-color: transparent;
#             margin-bottom: 10px;
#             text-shadow: 0 0 30px rgba(167, 139, 250, 0.5);
#             animation: glow 2s ease-in-out infinite alternate;
#         }
        
#         @keyframes glow {
#             from { filter: drop-shadow(0 0 10px rgba(167, 139, 250, 0.5)); }
#             to { filter: drop-shadow(0 0 20px rgba(167, 139, 250, 0.8)); }
#         }
        
#         .hero-subtitle {
#             text-align: center;
#             font-size: 20px;
#             color: rgba(255, 255, 255, 0.8);
#             font-weight: 400;
#             margin-bottom: 40px;
#             letter-spacing: 1px;
#         }
        
#         /* Glass Cards */
#         .glass-card {
#             background: rgba(255, 255, 255, 0.08);
#             backdrop-filter: blur(20px);
#             border-radius: 25px;
#             padding: 30px;
#             border: 1px solid rgba(255, 255, 255, 0.15);
#             box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
#             margin: 20px 0;
#         }
        
#         .glass-card:hover {
#             transform: translateY(-5px);
#             box-shadow: 0 25px 70px rgba(167, 139, 250, 0.3);
#             border-color: rgba(167, 139, 250, 0.5);
#         }
        
#         /* Status Cards */
#         .success-card {
#             background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.1) 100%);
#             backdrop-filter: blur(20px);
#             border-radius: 20px;
#             padding: 25px;
#             border-left: 5px solid #10b981;
#             box-shadow: 0 10px 40px rgba(16, 185, 129, 0.2);
#             margin: 15px 0;
#         }
        
#         .danger-card {
#             background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.1) 100%);
#             backdrop-filter: blur(20px);
#             border-radius: 20px;
#             padding: 25px;
#             border-left: 5px solid #ef4444;
#             box-shadow: 0 10px 40px rgba(239, 68, 68, 0.2);
#             margin: 15px 0;
#         }
        
#         .success-text {
#             color: #6ee7b7;
#             font-size: 24px;
#             font-weight: 600;
#             margin: 0;
#         }
        
#         .danger-text {
#             color: #fca5a5;
#             font-size: 24px;
#             font-weight: 600;
#             margin: 0;
#         }
        
#         /* Alternative Station Cards */
#         .alt-station-card {
#             background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(124, 58, 237, 0.15) 100%);
#             backdrop-filter: blur(15px);
#             border-radius: 18px;
#             padding: 20px;
#             margin: 12px 0;
#             border: 1px solid rgba(139, 92, 246, 0.4);
#             box-shadow: 0 8px 32px rgba(139, 92, 246, 0.25);
#         }
        
#         .alt-station-card:hover {
#             transform: translateX(10px);
#             border-color: rgba(139, 92, 246, 0.7);
#             box-shadow: 0 12px 40px rgba(139, 92, 246, 0.4);
#             background: linear-gradient(135deg, rgba(139, 92, 246, 0.25) 0%, rgba(124, 58, 237, 0.2) 100%);
#         }
        
#         .station-rank {
#             display: inline-block;
#             background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
#             color: white;
#             border-radius: 50%;
#             width: 40px;
#             height: 40px;
#             text-align: center;
#             line-height: 40px;
#             font-weight: 700;
#             font-size: 18px;
#             box-shadow: 0 5px 15px rgba(139, 92, 246, 0.4);
#         }
        
#         .station-name {
#             font-size: 22px;
#             font-weight: 700;
#             color: #e9d5ff;
#             margin: 10px 0;
#         }
        
#         .station-detail {
#             color: rgba(255, 255, 255, 0.8);
#             font-size: 15px;
#             margin: 8px 0;
#         }
        
#         .station-badge {
#             display: inline-block;
#             padding: 6px 14px;
#             border-radius: 20px;
#             font-size: 13px;
#             font-weight: 600;
#             margin: 5px 5px 5px 0;
#         }
        
#         .badge-success {
#             background: rgba(16, 185, 129, 0.2);
#             color: #6ee7b7;
#             border: 1px solid #10b981;
#         }
        
#         .badge-warning {
#             background: rgba(245, 158, 11, 0.2);
#             color: #fcd34d;
#             border: 1px solid #f59e0b;
#         }
        
#         /* Metrics Dashboard */
#         .metric-container {
#             background: rgba(0, 0, 0, 0.5);
#             backdrop-filter: blur(15px);
#             border-radius: 20px;
#             padding: 25px;
#             text-align: center;
#             border: 1px solid rgba(139, 92, 246, 0.3);
#             box-shadow: 0 8px 32px rgba(139, 92, 246, 0.2);
#         }
        
#         .metric-container:hover {
#             background: rgba(139, 92, 246, 0.15);
#             transform: scale(1.05);
#             border-color: rgba(139, 92, 246, 0.5);
#         }
        
#         .metric-label {
#             color: rgba(255, 255, 255, 0.7);
#             font-size: 14px;
#             font-weight: 500;
#             text-transform: uppercase;
#             letter-spacing: 1px;
#             margin-bottom: 10px;
#         }
        
#         .metric-value {
#             color: #fff;
#             font-size: 36px;
#             font-weight: 800;
#             background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%);
#             -webkit-background-clip: text;
#             -webkit-text-fill-color: transparent;
#         }
        
#         /* Distance Indicator */
#         .distance-indicator {
#             background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(37, 99, 235, 0.1) 100%);
#             border-radius: 15px;
#             padding: 15px;
#             margin: 10px 0;
#             border-left: 4px solid #3b82f6;
#         }
        
#         .distance-text {
#             color: #93c5fd;
#             font-size: 18px;
#             font-weight: 600;
#         }
        
#         /* Section Headers */
#         .section-header {
#             color: #fff;
#             font-size: 28px;
#             font-weight: 700;
#             margin: 30px 0 20px 0;
#             padding-bottom: 10px;
#             border-bottom: 2px solid rgba(139, 92, 246, 0.5);
#         }
        
#         /* Buttons */
#         .stButton > button {
#             background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
#             color: white;
#             border: none;
#             border-radius: 15px;
#             padding: 18px 35px;
#             font-size: 18px;
#             font-weight: 700;
#             width: 100%;
#             letter-spacing: 1px;
#             box-shadow: 0 10px 30px rgba(139, 92, 246, 0.4);
#             text-transform: uppercase;
#         }
        
#         .stButton > button:hover {
#             background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
#             transform: translateY(-3px);
#             box-shadow: 0 15px 40px rgba(139, 92, 246, 0.6);
#         }
        
#         /* Sidebar Styling */
#         section[data-testid="stSidebar"] {
#             background: linear-gradient(180deg, rgba(10, 10, 10, 0.98) 0%, rgba(26, 10, 46, 0.98) 100%);
#             backdrop-filter: blur(20px);
#             border-right: 1px solid rgba(139, 92, 246, 0.2);
#         }
        
#         section[data-testid="stSidebar"] > div {
#             background: transparent;
#         }
        
#         /* Input Fields */
#         .stSelectbox label, .stRadio label {
#             color: rgba(255, 255, 255, 0.9) !important;
#             font-weight: 600 !important;
#             font-size: 16px !important;
#         }
        
#         /* Info Box */
#         .info-box {
#             background: rgba(59, 130, 246, 0.1);
#             border-left: 4px solid #3b82f6;
#             border-radius: 12px;
#             padding: 20px;
#             margin: 15px 0;
#             color: #93c5fd;
#         }
        
#         /* Divider */
#         hr {
#             border: none;
#             height: 1px;
#             background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.5), transparent);
#             margin: 30px 0;
#         }
        
#         /* Metric Cards in Streamlit */
#         div[data-testid="stMetricValue"] {
#             font-size: 32px;
#             font-weight: 800;
#             color: #a78bfa;
#         }
        
#         div[data-testid="stMetricLabel"] {
#             color: rgba(255, 255, 255, 0.8);
#             font-weight: 600;
#         }
        
#         /* Tab styling */
#         .stTabs [data-baseweb="tab-list"] {
#             gap: 10px;
#             background: rgba(255, 255, 255, 0.05);
#             border-radius: 15px;
#             padding: 10px;
#         }
        
#         .stTabs [data-baseweb="tab"] {
#             background: transparent;
#             color: rgba(255, 255, 255, 0.7);
#             border-radius: 10px;
#             padding: 12px 24px;
#             font-weight: 600;
#         }
        
#         .stTabs [aria-selected="true"] {
#             background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
#             color: white;
#         }
#     </style>
# """, unsafe_allow_html=True)

# # Load and process data
# @st.cache_data
# def load_data(file_path):
#     df = pd.read_excel(file_path)
#     time_slots = sorted(set(col.split("_")[-1] for col in df.columns if "PPHPD" in col))
    
#     for time in time_slots:
#         boarding_threshold = df[f'Boarding_{time}'].quantile(0.70)
#         alighting_threshold = df[f'Alighting_{time}'].quantile(0.70)
        
#         df[f'Rush_Boarding_{time}'] = (df[f'Boarding_{time}'] > boarding_threshold).astype(int)
#         df[f'Rush_Alighting_{time}'] = (df[f'Alighting_{time}'] > alighting_threshold).astype(int)
    
#     return df, time_slots

# # Train ML models with comprehensive metrics
# @st.cache_resource
# def train_ml_models(df, time_slots):
#     models_boarding, models_alighting = {}, {}
#     metrics_boarding, metrics_alighting = {}, {}
    
#     for time in time_slots:
#         # Boarding model
#         X_boarding = df[[f'Boarding_{time}', f'PPHPD_{time}', 'Distance from SBC']]
#         y_boarding = df[f'Rush_Boarding_{time}']
#         X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(
#             X_boarding, y_boarding, test_size=0.2, random_state=42
#         )
        
#         model_boarding = RandomForestClassifier(n_estimators=300, max_depth=15, random_state=42)
#         model_boarding.fit(X_train_b, y_train_b)
        
#         y_pred_b = model_boarding.predict(X_test_b)
#         metrics_boarding[time] = {
#             'accuracy': accuracy_score(y_test_b, y_pred_b),
#             'precision': precision_score(y_test_b, y_pred_b, zero_division=0),
#             'recall': recall_score(y_test_b, y_pred_b, zero_division=0),
#             'f1': f1_score(y_test_b, y_pred_b, zero_division=0),
#             'confusion_matrix': confusion_matrix(y_test_b, y_pred_b)
#         }
#         models_boarding[time] = model_boarding
        
#         # Alighting model
#         X_alighting = df[[f'Alighting_{time}', f'PPHPD_{time}', 'Distance from SBC']]
#         y_alighting = df[f'Rush_Alighting_{time}']
#         X_train_a, X_test_a, y_train_a, y_test_a = train_test_split(
#             X_alighting, y_alighting, test_size=0.2, random_state=42
#         )
        
#         model_alighting = RandomForestClassifier(n_estimators=300, max_depth=15, random_state=42)
#         model_alighting.fit(X_train_a, y_train_a)
        
#         y_pred_a = model_alighting.predict(X_test_a)
#         metrics_alighting[time] = {
#             'accuracy': accuracy_score(y_test_a, y_pred_a),
#             'precision': precision_score(y_test_a, y_pred_a, zero_division=0),
#             'recall': recall_score(y_test_a, y_pred_a, zero_division=0),
#             'f1': f1_score(y_test_a, y_pred_a, zero_division=0),
#             'confusion_matrix': confusion_matrix(y_test_a, y_pred_a)
#         }
#         models_alighting[time] = model_alighting
    
#     return models_boarding, models_alighting, metrics_boarding, metrics_alighting

# # Predict with probability
# def predict_rush_with_probability(model, station_data):
#     prediction = model.predict([station_data])[0]
#     probability = model.predict_proba([station_data])[0]
#     return prediction, probability[1]

# # Calculate actual distance between two stations along the route
# def compute_distance_between_stations(df, station1, station2):
#     """
#     Calculate actual distance between two stations along the metro route.
    
#     How it works:
#     1. Each station has a 'Distance from SBC' value (in km)
#     2. SBC is the reference point (Station Base Center/Starting point)
#     3. Distance between any two stations = |Distance1 - Distance2|
    
#     Example:
#     - CLGT is at 58 km from SBC
#     - KGIT is at 12 km from SBC
#     - Distance between CLGT and KGIT = |58 - 12| = 46 km
    
#     This gives the actual route distance along the metro line.
#     """
#     station_distances = df.set_index('Station')['Distance from SBC'].to_dict()
#     dist1 = station_distances.get(station1, 0)
#     dist2 = station_distances.get(station2, 0)
#     actual_distance = abs(dist1 - dist2)
    
#     return actual_distance

# # Smart scoring for alternatives
# def calculate_station_score(distance_km, is_congested, pphpd, boarding_count):
#     """
#     Scoring system:
#     - Distance: closer is better (50% weight)
#     - Congestion: not congested is much better (30% weight)
#     - Traffic density: lower is better (15% weight)
#     - Boarding count: lower is better (5% weight)
#     """
#     # Normalize distance (assume max 20km difference)
#     dist_score = min(distance_km / 20, 1.0)
    
#     # Congestion penalty (heavy penalty for congestion)
#     congestion_score = 1.0 if is_congested else 0.0
    
#     # Normalize PPHPD (assume max 5000)
#     pphpd_score = min(pphpd / 5000, 1.0)
    
#     # Normalize boarding count (assume max 2000)
#     boarding_score = min(boarding_count / 2000, 1.0)
    
#     # Weighted score (lower is better)
#     total_score = (0.50 * dist_score) + (0.30 * congestion_score) + (0.15 * pphpd_score) + (0.05 * boarding_score)
    
#     return total_score

# # Find alternate stations in the same direction
# def find_alternate_stations(station, direction, time, df, boarding_type, top_n=5):
#     rush_column = f'Rush_Boarding_{time}' if boarding_type == 'Boarding' else f'Rush_Alighting_{time}'
#     traffic_column = f'{boarding_type}_{time}'
#     pphpd_column = f'PPHPD_{time}'
    
#     current_station_data = df[df['Station'] == station].iloc[0]
#     current_rush = current_station_data[rush_column]
#     current_distance = current_station_data['Distance from SBC']
    
#     # If current station is not congested, no need for alternatives
#     if current_rush == 0:
#         return []
    
#     # Get all stations in same direction
#     same_direction_stations = df[df['Direction'] == direction].copy()
    
#     alternatives = []
#     for idx, row in same_direction_stations.iterrows():
#         if row['Station'] == station:
#             continue
        
#         # Calculate distance between stations
#         distance = compute_distance_between_stations(df, station, row['Station'])
        
#         # Get congestion status
#         is_congested = row[rush_column]
#         pphpd = row[pphpd_column]
#         traffic = row[traffic_column]
        
#         # Calculate score
#         score = calculate_station_score(distance, is_congested, pphpd, traffic)
        
#         alternatives.append({
#             'Station': row['Station'],
#             'Distance_km': round(distance, 2),
#             'Distance_from_SBC': row['Distance from SBC'],
#             'Is_Congested': is_congested,
#             'PPHPD': int(pphpd),
#             'Traffic_Count': int(traffic),
#             'Score': score,
#             'Direction': row['Direction']
#         })
    
#     # Sort by score (lower is better) and return top N
#     alternatives = sorted(alternatives, key=lambda x: x['Score'])[:top_n]
    
#     return alternatives

# # Enhanced rush status check
# def check_rush_status(station, direction, time, boarding_type, df, models_boarding, models_alighting):
#     station_row = df[(df['Station'] == station) & (df['Direction'] == direction)].iloc[0]
#     model = models_boarding[time] if boarding_type == "Boarding" else models_alighting[time]
    
#     features_cols = [f"{boarding_type}_{time}", f"PPHPD_{time}", 'Distance from SBC']
#     station_features = station_row[features_cols].values
    
#     predicted_rush, probability = predict_rush_with_probability(model, station_features)
    
#     # Current Station Status
#     st.markdown('<div class="glass-card">', unsafe_allow_html=True)
#     st.markdown(f'<h3 style="color: #a78bfa; margin-bottom: 20px;">📍 Current Station: {station}</h3>', unsafe_allow_html=True)
    
#     col1, col2, col3, col4 = st.columns(4)
#     with col1:
#         st.markdown(f'''
#             <div class="metric-container">
#                 <div class="metric-label">🚉 Station</div>
#                 <div style="color: white; font-size: 20px; font-weight: 700;">{station}</div>
#             </div>
#         ''', unsafe_allow_html=True)
    
#     with col2:
#         traffic_val = station_row[f'{boarding_type}_{time}']
#         st.markdown(f'''
#             <div class="metric-container">
#                 <div class="metric-label">👥 {boarding_type}</div>
#                 <div class="metric-value">{int(traffic_val)}</div>
#             </div>
#         ''', unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f'''
#             <div class="metric-container">
#                 <div class="metric-label">🚦 PPHPD</div>
#                 <div class="metric-value">{int(station_row[f'PPHPD_{time}'])}</div>
#             </div>
#         ''', unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f'''
#             <div class="metric-container">
#                 <div class="metric-label">📏 From SBC</div>
#                 <div class="metric-value">{station_row['Distance from SBC']} km</div>
#             </div>
#         ''', unsafe_allow_html=True)
    
#     st.markdown('</div>', unsafe_allow_html=True)
    
#     # Prediction Result
#     if predicted_rush == 1:
#         st.markdown(f'''
#         <div class="danger-card">
#             <p class="danger-text">⚠️ {station} is CROWDED at {time}</p>
#             <p style="color: rgba(255, 255, 255, 0.7); margin: 10px 0 0 0;">
#                 Confidence: {probability*100:.1f}% | Direction: {direction}
#             </p>
#         </div>
#         ''', unsafe_allow_html=True)
        
#         # Find alternates
#         alternates = find_alternate_stations(station, direction, time, df, boarding_type, top_n=5)
        
#         if alternates:
#             st.markdown(f'<h3 class="section-header">🎯 Recommended Alternative Stations (Same Direction: {direction})</h3>', unsafe_allow_html=True)
#             st.markdown('<p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 20px;">Stations ranked by proximity, congestion level, and traffic density</p>', unsafe_allow_html=True)
            
#             for i, alt in enumerate(alternates, 1):
#                 status_badge = "badge-success" if alt['Is_Congested'] == 0 else "badge-warning"
#                 status_text = "✅ Clear" if alt['Is_Congested'] == 0 else "⚠️ Busy"
#                 status_icon = "🟢" if alt['Is_Congested'] == 0 else "🟡"
                
#                 st.markdown(f'''
#                 <div class="alt-station-card">
#                     <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
#                         <span class="station-rank">#{i}</span>
#                         <div style="flex-grow: 1;">
#                             <div class="station-name">{alt['Station']}</div>
#                             <span class="station-badge {status_badge}">{status_icon} {status_text}</span>
#                         </div>
#                     </div>
                    
#                     <div class="info-box" style="margin-bottom: 15px; background: rgba(59, 130, 246, 0.15);">
#                         <strong>📐 Distance Calculation:</strong><br>
#                         {station} is at <strong>{station_row['Distance from SBC']} km</strong> from SBC<br>
#                         {alt['Station']} is at <strong>{alt['Distance_from_SBC']} km</strong> from SBC<br>
#                         <strong>Route Distance = |{station_row['Distance from SBC']} - {alt['Distance_from_SBC']}| = {alt['Distance_km']} km</strong>
#                     </div>
                    
#                     <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
#                         <div class="distance-indicator">
#                             <div class="distance-text">📍 Distance from {station}</div>
#                             <div style="color: white; font-size: 24px; font-weight: 800; margin-top: 5px;">
#                                 {alt['Distance_km']} km
#                             </div>
#                         </div>
                        
#                         <div style="background: rgba(139, 92, 246, 0.15); border-radius: 15px; padding: 15px;">
#                             <div style="color: #c4b5fd; font-size: 14px; font-weight: 600;">📏 Position from SBC</div>
#                             <div style="color: white; font-size: 24px; font-weight: 800; margin-top: 5px;">
#                                 {alt['Distance_from_SBC']} km
#                             </div>
#                         </div>
#                     </div>
                    
#                     <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 15px;">
#                         <div class="station-detail">
#                             <strong>🚦 PPHPD:</strong> {alt['PPHPD']}
#                         </div>
#                         <div class="station-detail">
#                             <strong>👥 Traffic:</strong> {alt['Traffic_Count']}
#                         </div>
#                         <div class="station-detail">
#                             <strong>⭐ Score:</strong> {alt['Score']:.3f}
#                         </div>
#                     </div>
                    
#                     <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(139, 92, 246, 0.3);">
#                         <div style="color: #c4b5fd; font-size: 13px;">
#                             <strong>🚆 Same Direction:</strong> All trains going to {direction} will stop here
#                         </div>
#                     </div>
#                 </div>
#                 ''', unsafe_allow_html=True)
            
#             st.markdown('''
#             <div class="info-box">
#                 <strong>💡 How Distance is Calculated:</strong><br><br>
                
#                 <strong>📐 Distance Calculation Method:</strong><br>
#                 • Each station has a fixed position from SBC (Station Base Center/Starting Point)<br>
#                 • The system calculates the absolute difference between two stations' positions<br>
#                 • <strong>Formula:</strong> Distance = |Station1_Position - Station2_Position|<br><br>
                
#                 <strong>Example with your data:</strong><br>
#                 • CLGT is at 58 km from SBC<br>
#                 • KGIT is at 12 km from SBC<br>
#                 • Distance between them = |58 - 12| = <strong>46 km</strong><br><br>
                
#                 <strong>🚆 Route Information:</strong><br>
#                 All suggested stations are on the <strong>same direction/route</strong>, so your train will stop at all of them. 
#                 Choose the nearest one with lower congestion for a comfortable journey!<br><br>
                
#                 <strong>⭐ Smart Ranking:</strong><br>
#                 Stations are ranked by a smart score considering:<br>
#                 • Distance from your selected station (50% weight) - closer is better<br>
#                 • Congestion level (30% weight) - less crowded is better<br>
#                 • Traffic density/PPHPD (15% weight) - lower is better<br>
#                 • Passenger count (5% weight) - fewer people is better
#             </div>
#             ''', unsafe_allow_html=True)
#         else:
#             st.markdown('''
#             <div class="info-box">
#                 ❌ No suitable alternative stations found in this direction at this time.
#             </div>
#             ''', unsafe_allow_html=True)
#     else:
#         st.markdown(f'''
#         <div class="success-card">
#             <p class="success-text">✅ {station} is NOT CROWDED at {time}</p>
#             <p style="color: rgba(255, 255, 255, 0.7); margin: 10px 0 0 0;">
#                 Confidence: {(1-probability)*100:.1f}% | Direction: {direction}
#             </p>
#             <p style="color: #6ee7b7; margin-top: 15px; font-size: 16px;">
#                 🎉 Perfect! You can comfortably board/alight at this station.
#             </p>
#         </div>
#         ''', unsafe_allow_html=True)

# # Create comprehensive metrics visualization
# def create_metrics_dashboard(metrics, model_type, time):
#     fig = go.Figure()
    
#     metrics_data = metrics[time]
#     metric_names = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
#     metric_values = [
#         metrics_data['accuracy'] * 100,
#         metrics_data['precision'] * 100,
#         metrics_data['recall'] * 100,
#         metrics_data['f1'] * 100
#     ]
    
#     colors = ['#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe']
    
#     fig.add_trace(go.Bar(
#         x=metric_names,
#         y=metric_values,
#         marker=dict(
#             color=colors,
#             line=dict(color='rgba(255, 255, 255, 0.3)', width=2)
#         ),
#         text=[f'{v:.2f}%' for v in metric_values],
#         textposition='outside',
#         textfont=dict(size=14, color='white', family='Poppins'),
#         hovertemplate='<b>%{x}</b><br>Score: %{y:.2f}%<extra></extra>'
#     ))
    
#     fig.update_layout(
#         title=dict(
#             text=f'{model_type} Model Performance - {time}',
#             font=dict(size=20, color='white', family='Poppins', weight=700),
#             x=0.5,
#             xanchor='center'
#         ),
#         xaxis=dict(
#             title='Metrics',
#             title_font=dict(size=16, color='rgba(255,255,255,0.8)'),
#             tickfont=dict(size=14, color='rgba(255,255,255,0.8)'),
#             gridcolor='rgba(255,255,255,0.1)'
#         ),
#         yaxis=dict(
#             title='Score (%)',
#             title_font=dict(size=16, color='rgba(255,255,255,0.8)'),
#             tickfont=dict(size=14, color='rgba(255,255,255,0.8)'),
#             gridcolor='rgba(255,255,255,0.1)',
#             range=[0, 105]
#         ),
#         plot_bgcolor='rgba(0,0,0,0)',
#         paper_bgcolor='rgba(0,0,0,0)',
#         height=400,
#         showlegend=False,
#         margin=dict(t=60, b=40, l=60, r=40)
#     )
    
#     return fig

# # Create confusion matrix heatmap
# def create_confusion_matrix_plot(cm, model_type, time):
#     fig = go.Figure(data=go.Heatmap(
#         z=cm,
#         x=['Not Crowded', 'Crowded'],
#         y=['Not Crowded', 'Crowded'],
#         colorscale=[[0, '#8b5cf6'], [1, '#c4b5fd']],
#         text=cm,
#         texttemplate='<b>%{text}</b>',
#         textfont=dict(size=18, color='white'),
#         hovertemplate='Predicted: %{x}<br>Actual: %{y}<br>Count: %{z}<extra></extra>'
#     ))
    
#     fig.update_layout(
#         title=dict(
#             text=f'{model_type} Confusion Matrix - {time}',
#             font=dict(size=20, color='white', family='Poppins', weight=700),
#             x=0.5,
#             xanchor='center'
#         ),
#         xaxis=dict(
#             title='Predicted',
#             title_font=dict(size=16, color='rgba(255,255,255,0.8)'),
#             tickfont=dict(size=14, color='rgba(255,255,255,0.8)')
#         ),
#         yaxis=dict(
#             title='Actual',
#             title_font=dict(size=16, color='rgba(255,255,255,0.8)'),
#             tickfont=dict(size=14, color='rgba(255,255,255,0.8)')
#         ),
#         plot_bgcolor='rgba(0,0,0,0)',
#         paper_bgcolor='rgba(0,0,0,0)',
#         height=400,
#         margin=dict(t=60, b=40, l=60, r=60)
#     )
    
#     return fig

# # Traffic visualization
# def create_traffic_heatmap(df, time, boarding_type, direction):
#     df_filtered = df[df['Direction'] == direction].sort_values('Distance from SBC')
#     data_col = f'{boarding_type}_{time}'
    
#     fig = go.Figure()
    
#     fig.add_trace(go.Bar(
#         x=df_filtered['Station'],
#         y=df_filtered[data_col],
#         marker=dict(
#             color=df_filtered[data_col],
#             colorscale='Turbo',
#             showscale=True,
            
#             colorbar=dict(
#                 title=dict(
#                     text='Traffic',
#                     font=dict(color='white')     # ✅ correct place
#                 ),
#                 tickfont=dict(color='white')
#             ),

            
#             line=dict(color='rgba(255,255,255,0.3)', width=1)
#         ),
#         text=df_filtered[data_col],
#         textposition='outside',
#         textfont=dict(color='white', size=12),
#         hovertemplate='<b>%{x}</b><br>Traffic: %{y}<extra></extra>'
#     ))
    
#     fig.update_layout(
#         title=dict(
#             text=f'{boarding_type} Traffic Distribution - {time} ({direction})',
#             font=dict(size=20, color='white', family='Poppins', weight=700),
#             x=0.5,
#             xanchor='center'
#         ),
#         xaxis=dict(
#             title='Station',
#             title_font=dict(size=16, color='rgba(255,255,255,0.8)'),
#             tickfont=dict(size=12, color='rgba(255,255,255,0.8)'),
#             tickangle=-45,
#             gridcolor='rgba(255,255,255,0.1)'
#         ),
#         yaxis=dict(
#             title=f'{boarding_type} Count',
#             title_font=dict(size=16, color='rgba(255,255,255,0.8)'),
#             tickfont=dict(size=14, color='rgba(255,255,255,0.8)'),
#             gridcolor='rgba(255,255,255,0.1)'
#         ),
#         plot_bgcolor='rgba(0,0,0,0)',
#         paper_bgcolor='rgba(0,0,0,0)',
#         height=500,
#         showlegend=False,
#         margin=dict(t=60, b=100, l=60, r=40)
#     )
    
#     return fig

# # Main App
# def main():
#     # Sidebar
#     st.sidebar.markdown('''
#         <div style="text-align: center; padding: 20px 0;">
#             <div style="font-size: 60px; margin-bottom: 10px;">🚇</div>
#             <h1 style="color: #a78bfa; font-size: 28px; margin: 0;">Smart Station</h1>
#             <h1 style="color: #a78bfa; font-size: 28px; margin: 0;">Advisor</h1>
#             <p style="color: rgba(255,255,255,0.6); font-size: 14px; margin-top: 10px;">AI-Powered Metro Intelligence</p>
#         </div>
#     ''', unsafe_allow_html=True)
    
#     st.sidebar.markdown("---")
    
#     file_path = st.sidebar.file_uploader(
#         "📂 Upload Metro Data",
#         type=["xlsx"],
#         help="Upload Excel file with station traffic data"
#     )
    
#     if file_path:
#         df, time_slots = load_data(file_path)
#         models_boarding, models_alighting, metrics_boarding, metrics_alighting = train_ml_models(df, time_slots)
        
#         # Hero Section
#         st.markdown('<h1 class="hero-title">🚇 Smart Metro Station Advisor</h1>', unsafe_allow_html=True)
#         st.markdown('<p class="hero-subtitle">AI-Powered Congestion Prediction & Intelligent Route Planning</p>', unsafe_allow_html=True)
        
#         # Sidebar Controls
#         with st.sidebar:
#             st.markdown("### 🎯 Configuration")
#             direction = st.selectbox(
#                 "🔄 Select Direction",
#                 df['Direction'].unique(),
#                 help="Choose your travel direction"
#             )
            
#             station = st.selectbox(
#                 "📍 Select Station",
#                 df[df['Direction'] == direction]['Station'].unique(),
#                 help="Choose your preferred station"
#             )
            
#             time = st.selectbox(
#                 "⏰ Time Slot",
#                 time_slots,
#                 help="Select your travel time"
#             )
            
#             boarding_type = st.radio(
#                 "🚶 Action Type",
#                 ["Boarding", "Alighting"],
#                 help="Are you boarding or alighting?"
#             )
            
#             st.markdown("---")
#             check_button = st.button("🔍 Analyze Station", use_container_width=True)
        
#         # Main Content
#         if check_button:
#             check_rush_status(station, direction, time, boarding_type, df, models_boarding, models_alighting)
            
#             st.markdown("---")
            
#             # Traffic Visualization
#             st.markdown('<h2 class="section-header">📊 Traffic Distribution Analysis</h2>', unsafe_allow_html=True)
#             fig_traffic = create_traffic_heatmap(df, time, boarding_type, direction)
#             st.plotly_chart(fig_traffic, use_container_width=True)
        
#         # Model Performance Section
#         st.markdown("---")
#         st.markdown('<h2 class="section-header">🎯 Model Performance Analytics</h2>', unsafe_allow_html=True)
        
#         tab1, tab2 = st.tabs(["📈 Metrics Dashboard", "🔥 Confusion Matrix"])
        
#         with tab1:
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 st.markdown("#### 🚆 Boarding Model")
#                 metrics_b = metrics_boarding[time]
                
#                 col_a, col_b, col_c, col_d = st.columns(4)
#                 with col_a:
#                     st.metric("Accuracy", f"{metrics_b['accuracy']*100:.2f}%")
#                 with col_b:
#                     st.metric("Precision", f"{metrics_b['precision']*100:.2f}%")
#                 with col_c:
#                     st.metric("Recall", f"{metrics_b['recall']*100:.2f}%")
#                 with col_d:
#                     st.metric("F1 Score", f"{metrics_b['f1']*100:.2f}%")
                
#                 fig_b = create_metrics_dashboard(metrics_boarding, "Boarding", time)
#                 st.plotly_chart(fig_b, use_container_width=True)
            
#             with col2:
#                 st.markdown("#### 🚉 Alighting Model")
#                 metrics_a = metrics_alighting[time]
                
#                 col_a, col_b, col_c, col_d = st.columns(4)
#                 with col_a:
#                     st.metric("Accuracy", f"{metrics_a['accuracy']*100:.2f}%")
#                 with col_b:
#                     st.metric("Precision", f"{metrics_a['precision']*100:.2f}%")
#                 with col_c:
#                     st.metric("Recall", f"{metrics_a['recall']*100:.2f}%")
#                 with col_d:
#                     st.metric("F1 Score", f"{metrics_a['f1']*100:.2f}%")
                
#                 fig_a = create_metrics_dashboard(metrics_alighting, "Alighting", time)
#                 st.plotly_chart(fig_a, use_container_width=True)
        
#         with tab2:
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 cm_b = metrics_boarding[time]['confusion_matrix']
#                 fig_cm_b = create_confusion_matrix_plot(cm_b, "Boarding", time)
#                 st.plotly_chart(fig_cm_b, use_container_width=True)
            
#             with col2:
#                 cm_a = metrics_alighting[time]['confusion_matrix']
#                 fig_cm_a = create_confusion_matrix_plot(cm_a, "Alighting", time)
#                 st.plotly_chart(fig_cm_a, use_container_width=True)
        
#         # Summary Stats
#         st.markdown("---")
#         st.markdown('<h2 class="section-header">📊 Dataset Summary</h2>', unsafe_allow_html=True)
        
#         col1, col2, col3, col4 = st.columns(4)
#         with col1:
#             st.markdown(f'''
#                 <div class="metric-container">
#                     <div class="metric-label">🚉 Total Stations</div>
#                     <div class="metric-value">{len(df)}</div>
#                 </div>
#             ''', unsafe_allow_html=True)
        
#         with col2:
#             st.markdown(f'''
#                 <div class="metric-container">
#                     <div class="metric-label">🔄 Directions</div>
#                     <div class="metric-value">{df['Direction'].nunique()}</div>
#                 </div>
#             ''', unsafe_allow_html=True)
        
#         with col3:
#             st.markdown(f'''
#                 <div class="metric-container">
#                     <div class="metric-label">⏰ Time Slots</div>
#                     <div class="metric-value">{len(time_slots)}</div>
#                 </div>
#             ''', unsafe_allow_html=True)
        
#         with col4:
#             avg_acc = (metrics_boarding[time]['accuracy'] + metrics_alighting[time]['accuracy']) / 2
#             st.markdown(f'''
#                 <div class="metric-container">
#                     <div class="metric-label">🎯 Avg Accuracy</div>
#                     <div class="metric-value">{avg_acc*100:.1f}%</div>
#                 </div>
#             ''', unsafe_allow_html=True)
    
#     else:
#         st.markdown('<h1 class="hero-title">🚇 Smart Metro Station Advisor</h1>', unsafe_allow_html=True)
#         st.markdown('<p class="hero-subtitle">AI-Powered Congestion Prediction & Intelligent Route Planning</p>', unsafe_allow_html=True)
        
#         st.markdown('''
#         <div class="glass-card" style="text-align: center;">
#             <h2 style="color: #a78bfa; margin-bottom: 20px;">👈 Get Started</h2>
#             <p style="color: rgba(255,255,255,0.8); font-size: 18px; line-height: 1.8;">
#                 Upload your metro station traffic data using the sidebar to begin intelligent congestion analysis
#             </p>
#         </div>
#         ''', unsafe_allow_html=True)
        
#         with st.expander("📋 Required Data Format", expanded=True):
#             st.markdown("""
#             <div style="color: rgba(255,255,255,0.9);">
            
#             **Your Excel file should contain these columns:**
            
#             - `Station` - Station name
#             - `Direction` - Travel direction (e.g., Direction 1, Direction 2)
#             - `Boarding_[TIME]` - Number of passengers boarding
#             - `Alighting_[TIME]` - Number of passengers alighting
#             - `PPHPD_[TIME]` - Passengers Per Hour Per Direction
#             - `Distance from SBC` - Distance in kilometers from starting point
            
#             **Example:** `Boarding_0800-0900`, `Alighting_1700-1800`, etc.
#             </div>
#             """, unsafe_allow_html=True)

# if __name__ == "__main__":
#     main()















import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Ultra-modern CSS with glassmorphism and animations
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
        
        * { 
            font-family: 'Poppins', sans-serif;
            transition: all 0.3s ease;
        }
        
        .stApp {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a0a2e 30%, #16213e 60%, #0f0f23 100%);
            background-attachment: fixed;
        }
        
        .main > div {
            background: rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(10px);
            border-radius: 30px;
            padding: 30px;
            border: 1px solid rgba(139, 92, 246, 0.2);
        }
        
        /* Hero Section */
        .hero-title {
            font-size: 56px;
            font-weight: 800;
            text-align: center;
            background: linear-gradient(135deg, #a78bfa 0%, #c084fc 50%, #e879f9 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            text-shadow: 0 0 30px rgba(167, 139, 250, 0.5);
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from { filter: drop-shadow(0 0 10px rgba(167, 139, 250, 0.5)); }
            to { filter: drop-shadow(0 0 20px rgba(167, 139, 250, 0.8)); }
        }
        
        .hero-subtitle {
            text-align: center;
            font-size: 20px;
            color: rgba(255, 255, 255, 0.8);
            font-weight: 400;
            margin-bottom: 40px;
            letter-spacing: 1px;
        }
        
        /* Glass Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            margin: 20px 0;
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 25px 70px rgba(167, 139, 250, 0.3);
            border-color: rgba(167, 139, 250, 0.5);
        }
        
        /* Status Cards */
        .success-card {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.1) 100%);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 25px;
            border-left: 5px solid #10b981;
            box-shadow: 0 10px 40px rgba(16, 185, 129, 0.2);
            margin: 15px 0;
        }
        
        .danger-card {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.1) 100%);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 25px;
            border-left: 5px solid #ef4444;
            box-shadow: 0 10px 40px rgba(239, 68, 68, 0.2);
            margin: 15px 0;
        }
        
        .success-text {
            color: #6ee7b7;
            font-size: 24px;
            font-weight: 600;
            margin: 0;
        }
        
        .danger-text {
            color: #fca5a5;
            font-size: 24px;
            font-weight: 600;
            margin: 0;
        }
        
        /* Alternative Station Cards */
        .alt-station-card {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(124, 58, 237, 0.15) 100%);
            backdrop-filter: blur(15px);
            border-radius: 18px;
            padding: 20px;
            margin: 12px 0;
            border: 1px solid rgba(139, 92, 246, 0.4);
            box-shadow: 0 8px 32px rgba(139, 92, 246, 0.25);
        }
        
        .alt-station-card:hover {
            transform: translateX(10px);
            border-color: rgba(139, 92, 246, 0.7);
            box-shadow: 0 12px 40px rgba(139, 92, 246, 0.4);
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.25) 0%, rgba(124, 58, 237, 0.2) 100%);
        }
        
        .station-rank {
            display: inline-block;
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
            color: white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            text-align: center;
            line-height: 40px;
            font-weight: 700;
            font-size: 18px;
            box-shadow: 0 5px 15px rgba(139, 92, 246, 0.4);
        }
        
        .station-name {
            font-size: 22px;
            font-weight: 700;
            color: #e9d5ff;
            margin: 10px 0;
        }
        
        .station-detail {
            color: rgba(255, 255, 255, 0.8);
            font-size: 15px;
            margin: 8px 0;
        }
        
        .station-badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            margin: 5px 5px 5px 0;
        }
        
        .badge-success {
            background: rgba(16, 185, 129, 0.2);
            color: #6ee7b7;
            border: 1px solid #10b981;
        }
        
        .badge-warning {
            background: rgba(245, 158, 11, 0.2);
            color: #fcd34d;
            border: 1px solid #f59e0b;
        }
        
        /* Metrics Dashboard */
        .metric-container {
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 25px;
            text-align: center;
            border: 1px solid rgba(139, 92, 246, 0.3);
            box-shadow: 0 8px 32px rgba(139, 92, 246, 0.2);
        }
        
        .metric-container:hover {
            background: rgba(139, 92, 246, 0.15);
            transform: scale(1.05);
            border-color: rgba(139, 92, 246, 0.5);
        }
        
        .metric-label {
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        
        .metric-value {
            color: #fff;
            font-size: 36px;
            font-weight: 800;
            background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Distance Indicator */
        .distance-indicator {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(37, 99, 235, 0.1) 100%);
            border-radius: 15px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #3b82f6;
        }
        
        .distance-text {
            color: #93c5fd;
            font-size: 18px;
            font-weight: 600;
        }
        
        /* Section Headers */
        .section-header {
            color: #fff;
            font-size: 28px;
            font-weight: 700;
            margin: 30px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(139, 92, 246, 0.5);
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
            color: white;
            border: none;
            border-radius: 15px;
            padding: 18px 35px;
            font-size: 18px;
            font-weight: 700;
            width: 100%;
            letter-spacing: 1px;
            box-shadow: 0 10px 30px rgba(139, 92, 246, 0.4);
            text-transform: uppercase;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(139, 92, 246, 0.6);
        }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(10, 10, 10, 0.98) 0%, rgba(26, 10, 46, 0.98) 100%);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(139, 92, 246, 0.2);
        }
        
        section[data-testid="stSidebar"] > div {
            background: transparent;
        }
        
        /* Input Fields */
        .stSelectbox label, .stRadio label {
            color: rgba(255, 255, 255, 0.9) !important;
            font-weight: 600 !important;
            font-size: 16px !important;
        }
        
        /* Info Box */
        .info-box {
            background: rgba(59, 130, 246, 0.1);
            border-left: 4px solid #3b82f6;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            color: #93c5fd;
        }
        
        /* Divider */
        hr {
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.5), transparent);
            margin: 30px 0;
        }
        
        /* Metric Cards in Streamlit */
        div[data-testid="stMetricValue"] {
            font-size: 32px;
            font-weight: 800;
            color: #a78bfa;
        }
        
        div[data-testid="stMetricLabel"] {
            color: rgba(255, 255, 255, 0.8);
            font-weight: 600;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: rgba(255, 255, 255, 0.7);
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Load and process data
@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path)
    time_slots = sorted(set(col.split("_")[-1] for col in df.columns if "PPHPD" in col))
    
    # Use a more balanced threshold to create meaningful classification
    for time in time_slots:
        # Use 60th percentile for better class distribution
        boarding_threshold = df[f'Boarding_{time}'].quantile(0.60)
        alighting_threshold = df[f'Alighting_{time}'].quantile(0.60)
        
        df[f'Rush_Boarding_{time}'] = (df[f'Boarding_{time}'] > boarding_threshold).astype(int)
        df[f'Rush_Alighting_{time}'] = (df[f'Alighting_{time}'] > alighting_threshold).astype(int)
    
    return df, time_slots

# Train ML models with comprehensive metrics
@st.cache_resource
def train_ml_models(df, time_slots):
    models_boarding, models_alighting = {}, {}
    metrics_boarding, metrics_alighting = {}, {}
    
    for time in time_slots:
        # Boarding model
        X_boarding = df[[f'Boarding_{time}', f'PPHPD_{time}', 'Distance from SBC']]
        y_boarding = df[f'Rush_Boarding_{time}']
        X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(
            X_boarding, y_boarding, test_size=0.2, random_state=42
        )
        
        model_boarding = RandomForestClassifier(n_estimators=300, max_depth=15, random_state=42)
        model_boarding.fit(X_train_b, y_train_b)
        
        y_pred_b = model_boarding.predict(X_test_b)
        metrics_boarding[time] = {
            'accuracy': accuracy_score(y_test_b, y_pred_b),
            'precision': precision_score(y_test_b, y_pred_b, zero_division=0),
            'recall': recall_score(y_test_b, y_pred_b, zero_division=0),
            'f1': f1_score(y_test_b, y_pred_b, zero_division=0),
            'confusion_matrix': confusion_matrix(y_test_b, y_pred_b)
        }
        models_boarding[time] = model_boarding
        
        # Alighting model
        X_alighting = df[[f'Alighting_{time}', f'PPHPD_{time}', 'Distance from SBC']]
        y_alighting = df[f'Rush_Alighting_{time}']
        X_train_a, X_test_a, y_train_a, y_test_a = train_test_split(
            X_alighting, y_alighting, test_size=0.2, random_state=42
        )
        
        model_alighting = RandomForestClassifier(n_estimators=300, max_depth=15, random_state=42)
        model_alighting.fit(X_train_a, y_train_a)
        
        y_pred_a = model_alighting.predict(X_test_a)
        metrics_alighting[time] = {
            'accuracy': accuracy_score(y_test_a, y_pred_a),
            'precision': precision_score(y_test_a, y_pred_a, zero_division=0),
            'recall': recall_score(y_test_a, y_pred_a, zero_division=0),
            'f1': f1_score(y_test_a, y_pred_a, zero_division=0),
            'confusion_matrix': confusion_matrix(y_test_a, y_pred_a)
        }
        models_alighting[time] = model_alighting
    
    return models_boarding, models_alighting, metrics_boarding, metrics_alighting

# Predict with probability
def predict_rush_with_probability(model, station_data):
    prediction = model.predict([station_data])[0]
    probability = model.predict_proba([station_data])[0]
    return prediction, probability[1]

# Calculate actual distance between two stations along the route
def compute_distance_between_stations(df, station1, station2):
    """
    Calculate actual distance between two stations along the metro route.
    
    How it works:
    1. Each station has a 'Distance from SBC' value (in km)
    2. SBC is the reference point (Station Base Center/Starting point)
    3. Distance between any two stations = |Distance1 - Distance2|
    
    Example:
    - CLGT is at 58 km from SBC
    - KGIT is at 12 km from SBC
    - Distance between CLGT and KGIT = |58 - 12| = 46 km
    
    This gives the actual route distance along the metro line.
    """
    station_distances = df.set_index('Station')['Distance from SBC'].to_dict()
    dist1 = station_distances.get(station1, 0)
    dist2 = station_distances.get(station2, 0)
    actual_distance = abs(dist1 - dist2)
    
    return actual_distance

# Smart scoring for alternatives
def calculate_station_score(distance_km, is_congested, pphpd, boarding_count):
    """
    Scoring system:
    - Distance: closer is better (50% weight)
    - Congestion: not congested is much better (30% weight)
    - Traffic density: lower is better (15% weight)
    - Boarding count: lower is better (5% weight)
    """
    # Normalize distance (assume max 20km difference)
    dist_score = min(distance_km / 20, 1.0)
    
    # Congestion penalty (heavy penalty for congestion)
    congestion_score = 1.0 if is_congested else 0.0
    
    # Normalize PPHPD (assume max 5000)
    pphpd_score = min(pphpd / 5000, 1.0)
    
    # Normalize boarding count (assume max 2000)
    boarding_score = min(boarding_count / 2000, 1.0)
    
    # Weighted score (lower is better)
    total_score = (0.50 * dist_score) + (0.30 * congestion_score) + (0.15 * pphpd_score) + (0.05 * boarding_score)
    
    return total_score

# Find alternate stations in the same direction
def find_alternate_stations(station, direction, time, df, boarding_type, top_n=5):
    rush_column = f'Rush_Boarding_{time}' if boarding_type == 'Boarding' else f'Rush_Alighting_{time}'
    traffic_column = f'{boarding_type}_{time}'
    pphpd_column = f'PPHPD_{time}'
    
    current_station_data = df[df['Station'] == station].iloc[0]
    current_rush = current_station_data[rush_column]
    current_distance = current_station_data['Distance from SBC']
    
    # If current station is not congested, no need for alternatives
    if current_rush == 0:
        return []
    
    # Get all stations in same direction
    same_direction_stations = df[df['Direction'] == direction].copy()
    
    alternatives = []
    for idx, row in same_direction_stations.iterrows():
        if row['Station'] == station:
            continue
        
        # Calculate distance between stations
        distance = compute_distance_between_stations(df, station, row['Station'])
        
        # Get congestion status
        is_congested = row[rush_column]
        pphpd = row[pphpd_column]
        traffic = row[traffic_column]
        
        # Calculate score
        score = calculate_station_score(distance, is_congested, pphpd, traffic)
        
        alternatives.append({
            'Station': row['Station'],
            'Distance_km': round(distance, 2),
            'Distance_from_SBC': row['Distance from SBC'],
            'Is_Congested': is_congested,
            'PPHPD': int(pphpd),
            'Traffic_Count': int(traffic),
            'Score': score,
            'Direction': row['Direction']
        })
    
    # Sort by score (lower is better) and return top N
    alternatives = sorted(alternatives, key=lambda x: x['Score'])[:top_n]
    
    return alternatives

# Enhanced rush status check
def check_rush_status(station, direction, time, boarding_type, df, models_boarding, models_alighting):
    station_row = df[(df['Station'] == station) & (df['Direction'] == direction)].iloc[0]
    model = models_boarding[time] if boarding_type == "Boarding" else models_alighting[time]
    
    features_cols = [f"{boarding_type}_{time}", f"PPHPD_{time}", 'Distance from SBC']
    station_features = station_row[features_cols].values
    
    predicted_rush, probability = predict_rush_with_probability(model, station_features)
    
    # Current Station Status
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f'<h3 style="color: #a78bfa; margin-bottom: 20px;">📍 Current Station: {station}</h3>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'''
            <div class="metric-container">
                <div class="metric-label">🚉 Station</div>
                <div style="color: white; font-size: 20px; font-weight: 700;">{station}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        traffic_val = station_row[f'{boarding_type}_{time}']
        st.markdown(f'''
            <div class="metric-container">
                <div class="metric-label">👥 {boarding_type}</div>
                <div class="metric-value">{int(traffic_val)}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
            <div class="metric-container">
                <div class="metric-label">🚦 PPHPD</div>
                <div class="metric-value">{int(station_row[f'PPHPD_{time}'])}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
            <div class="metric-container">
                <div class="metric-label">📏 From SBC</div>
                <div class="metric-value">{station_row['Distance from SBC']} km</div>
            </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Prediction Result
    if predicted_rush == 1:
        st.markdown(f'''
        <div class="danger-card">
            <p class="danger-text">⚠️ {station} is CROWDED at {time}</p>
            <p style="color: rgba(255, 255, 255, 0.7); margin: 10px 0 0 0;">
                Confidence: {probability*100:.1f}% | Direction: {direction}
            </p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Find alternates
        alternates = find_alternate_stations(station, direction, time, df, boarding_type, top_n=5)
        
        if alternates:
            st.markdown(f'<h3 class="section-header">🎯 Recommended Alternative Stations (Same Direction: {direction})</h3>', unsafe_allow_html=True)
            st.markdown('<p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 20px;">Stations ranked by proximity, congestion level, and traffic density</p>', unsafe_allow_html=True)
            
            for i, alt in enumerate(alternates, 1):
             status_badge = "badge-success" if alt['Is_Congested'] == 0 else "badge-warning"
            status_text = "✅ Clear" if alt['Is_Congested'] == 0 else "⚠️ Busy"
            status_icon = "🟢" if alt['Is_Congested'] == 0 else "🟡"

            st.markdown(f"""
            <div class="alt-station-card">
                <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                    <span class="station-rank">#{i}</span>
                    <div style="flex-grow: 1;">
                        <div class="station-name">{alt['Station']}</div>
                        <span class="station-badge {status_badge}">
                            {status_icon} {status_text}
                        </span>
                        <div style="margin-top: 6px; font-size: 13px; color: #e5e7eb;">
                            📏 Route Distance = |{station_row['Distance from SBC']} − {alt['Distance_from_SBC']}|
                            = <strong>{alt['Distance_km']} km</strong>
                        </div>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 15px;">
                    <div class="station-detail">
                        <strong>🚦 PPHPD:</strong> {alt['PPHPD']}
                    </div>
                    <div class="station-detail">
                        <strong>👥 Traffic:</strong> {alt['Traffic_Count']}
                    </div>
                    <div class="station-detail">
                        <strong>⭐ Score:</strong> {alt['Score']:.3f}
                    </div>
                </div>

                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(139, 92, 246, 0.3);">
                    <div style="color: #c4b5fd; font-size: 13px;">
                        <strong>🚆 Same Direction:</strong> All trains going to {direction} will stop here
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('''
            <div class="info-box">
                <strong>💡 How Distance is Calculated:</strong><br><br>
                
                <strong>📐 Distance Calculation Method:</strong><br>
                • Each station has a fixed position from SBC (Station Base Center/Starting Point)<br>
                • The system calculates the absolute difference between two stations' positions<br>
                • <strong>Formula:</strong> Distance = |Station1_Position - Station2_Position|<br><br>
                
                <strong>Example with your data:</strong><br>
                • CLGT is at 58 km from SBC<br>
                • KGIT is at 12 km from SBC<br>
                • Distance between them = |58 - 12| = <strong>46 km</strong><br><br>
                
                <strong>🚆 Route Information:</strong><br>
                All suggested stations are on the <strong>same direction/route</strong>, so your train will stop at all of them. 
                Choose the nearest one with lower congestion for a comfortable journey!<br><br>
                
                <strong>⭐ Smart Ranking:</strong><br>
                Stations are ranked by a smart score considering:<br>
                • Distance from your selected station (50% weight) - closer is better<br>
                • Congestion level (30% weight) - less crowded is better<br>
                • Traffic density/PPHPD (15% weight) - lower is better<br>
                • Passenger count (5% weight) - fewer people is better
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="info-box">
                ❌ No suitable alternative stations found in this direction at this time.
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div class="success-card">
            <p class="success-text">✅ {station} is NOT CROWDED at {time}</p>
            <p style="color: rgba(255, 255, 255, 0.7); margin: 10px 0 0 0;">
                Confidence: {(1-probability)*100:.1f}% | Direction: {direction}
            </p>
            <p style="color: #6ee7b7; margin-top: 15px; font-size: 16px;">
                🎉 Perfect! You can comfortably board/alight at this station.
            </p>
        </div>
        ''', unsafe_allow_html=True)

# Create comprehensive metrics visualization
def create_metrics_dashboard(metrics, model_type, time):
    fig = go.Figure()
    
    metrics_data = metrics[time]
    metric_names = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
    metric_values = [
        metrics_data['accuracy'] * 100,
        metrics_data['precision'] * 100,
        metrics_data['recall'] * 100,
        metrics_data['f1'] * 100
    ]
    
    colors = ['#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe']
    
    fig.add_trace(go.Bar(
        x=metric_names,
        y=metric_values,
        marker=dict(
            color=colors,
            line=dict(color='rgba(255, 255, 255, 0.3)', width=2)
        ),
        text=[f'{v:.2f}%' for v in metric_values],
        textposition='outside',
        textfont=dict(size=14, color='white', family='Poppins'),
        hovertemplate='<b>%{x}</b><br>Score: %{y:.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f'{model_type} Model Performance - {time}',
            font=dict(size=20, color='white', family='Poppins', weight=700),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='Metrics',
            title_font=dict(size=16, color='rgba(255,255,255,0.8)'),
            tickfont=dict(size=14, color='rgba(255,255,255,0.8)'),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title='Score (%)',
            title_font=dict(size=16, color='rgba(255,255,255,0.8)'),
            tickfont=dict(size=14, color='rgba(255,255,255,0.8)'),
            gridcolor='rgba(255,255,255,0.1)',
            range=[0, 105]
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=False,
        margin=dict(t=60, b=40, l=60, r=40)
    )
    
    return fig

# Create confusion matrix heatmap
def create_confusion_matrix_plot(cm, model_type, time):
    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=['Not Crowded', 'Crowded'],
        y=['Not Crowded', 'Crowded'],
        colorscale=[[0, '#8b5cf6'], [1, '#c4b5fd']],
        text=cm,
        texttemplate='<b>%{text}</b>',
        textfont=dict(size=18, color='white'),
        hovertemplate='Predicted: %{x}<br>Actual: %{y}<br>Count: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f'{model_type} Confusion Matrix - {time}',
            font=dict(size=20, color='white', family='Poppins', weight=700),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='Predicted',
            title_font=dict(size=16, color='rgba(255,255,255,0.8)'),
            tickfont=dict(size=14, color='rgba(255,255,255,0.8)')
        ),
        yaxis=dict(
            title='Actual',
            title_font=dict(size=16, color='rgba(255,255,255,0.8)'),
            tickfont=dict(size=14, color='rgba(255,255,255,0.8)')
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(t=60, b=40, l=60, r=60)
    )
    
    return fig

# Traffic visualization
def create_traffic_heatmap(df, time, boarding_type, direction):
    df_filtered = df[df['Direction'] == direction].sort_values('Distance from SBC')
    data_col = f'{boarding_type}_{time}'
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_filtered['Station'],
        y=df_filtered[data_col],
        marker=dict(
            color=df_filtered[data_col],
            colorscale='Turbo',
            showscale=True,
            colorbar=dict(
                title=dict(
                    text='Traffic',
                    font=dict(color='white')     # ✅ correct place
                ),
                tickfont=dict(color='white')
            ),
            line=dict(color='rgba(255,255,255,0.3)', width=1)
        ),
        text=df_filtered[data_col],
        textposition='outside',
        textfont=dict(color='white', size=12),
        hovertemplate='<b>%{x}</b><br>Traffic: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f'{boarding_type} Traffic Distribution - {time} ({direction})',
            font=dict(size=20, color='white', family='Poppins', weight=700),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='Station',
            title_font=dict(size=16, color='rgba(255,255,255,0.8)'),
            tickfont=dict(size=12, color='rgba(255,255,255,0.8)'),
            tickangle=-45,
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title=f'{boarding_type} Count',
            title_font=dict(size=16, color='rgba(255,255,255,0.8)'),
            tickfont=dict(size=14, color='rgba(255,255,255,0.8)'),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,
        showlegend=False,
        margin=dict(t=60, b=100, l=60, r=40)
    )
    
    return fig

# Main App
def main():
    # Sidebar
    st.sidebar.markdown('''
        <div style="text-align: center; padding: 20px 0;">
            <div style="font-size: 60px; margin-bottom: 10px;">🚇</div>
            <h1 style="color: #a78bfa; font-size: 28px; margin: 0;">Smart Station</h1>
            <h1 style="color: #a78bfa; font-size: 28px; margin: 0;">Advisor</h1>
            <p style="color: rgba(255,255,255,0.6); font-size: 14px; margin-top: 10px;">AI-Powered Metro Intelligence</p>
        </div>
    ''', unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    file_path = st.sidebar.file_uploader(
        "📂 Upload Metro Data",
        type=["xlsx"],
        help="Upload Excel file with station traffic data"
    )
    
    if file_path:
        df, time_slots = load_data(file_path)
        models_boarding, models_alighting, metrics_boarding, metrics_alighting = train_ml_models(df, time_slots)
        
        # Hero Section
        st.markdown('<h1 class="hero-title">🚇 Smart Metro Station Advisor</h1>', unsafe_allow_html=True)
        st.markdown('<p class="hero-subtitle">AI-Powered Congestion Prediction & Intelligent Route Planning</p>', unsafe_allow_html=True)
        
        # Sidebar Controls
        with st.sidebar:
            st.markdown("### 🎯 Configuration")
            direction = st.selectbox(
                "🔄 Select Direction",
                df['Direction'].unique(),
                help="Choose your travel direction"
            )
            
            station = st.selectbox(
                "📍 Select Station",
                df[df['Direction'] == direction]['Station'].unique(),
                help="Choose your preferred station"
            )
            
            time = st.selectbox(
                "⏰ Time Slot",
                time_slots,
                help="Select your travel time"
            )
            
            boarding_type = st.radio(
                "🚶 Action Type",
                ["Boarding", "Alighting"],
                help="Are you boarding or alighting?"
            )
            
            st.markdown("---")
            check_button = st.button("🔍 Analyze Station", use_container_width=True)
        
        # Main Content
        if check_button:
            check_rush_status(station, direction, time, boarding_type, df, models_boarding, models_alighting)
            
            st.markdown("---")
            
            # Traffic Visualization
            st.markdown('<h2 class="section-header">📊 Traffic Distribution Analysis</h2>', unsafe_allow_html=True)
            fig_traffic = create_traffic_heatmap(df, time, boarding_type, direction)
            st.plotly_chart(fig_traffic, use_container_width=True)
        
        # Model Performance Section
        st.markdown("---")
        st.markdown('<h2 class="section-header">🎯 Model Performance Analytics</h2>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["📈 Metrics Dashboard", "🔥 Confusion Matrix"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🚆 Boarding Model")
                metrics_b = metrics_boarding[time]
                
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Accuracy", f"{metrics_b['accuracy']*100:.2f}%")
                with col_b:
                    st.metric("Precision", f"{metrics_b['precision']*100:.2f}%")
                with col_c:
                    st.metric("Recall", f"{metrics_b['recall']*100:.2f}%")
                with col_d:
                    st.metric("F1 Score", f"{metrics_b['f1']*100:.2f}%")
                
                fig_b = create_metrics_dashboard(metrics_boarding, "Boarding", time)
                st.plotly_chart(fig_b, use_container_width=True)
            
            with col2:
                st.markdown("#### 🚉 Alighting Model")
                metrics_a = metrics_alighting[time]
                
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Accuracy", f"{metrics_a['accuracy']*100:.2f}%")
                with col_b:
                    st.metric("Precision", f"{metrics_a['precision']*100:.2f}%")
                with col_c:
                    st.metric("Recall", f"{metrics_a['recall']*100:.2f}%")
                with col_d:
                    st.metric("F1 Score", f"{metrics_a['f1']*100:.2f}%")
                
                fig_a = create_metrics_dashboard(metrics_alighting, "Alighting", time)
                st.plotly_chart(fig_a, use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                cm_b = metrics_boarding[time]['confusion_matrix']
                fig_cm_b = create_confusion_matrix_plot(cm_b, "Boarding", time)
                st.plotly_chart(fig_cm_b, use_container_width=True)
            
            with col2:
                cm_a = metrics_alighting[time]['confusion_matrix']
                fig_cm_a = create_confusion_matrix_plot(cm_a, "Alighting", time)
                st.plotly_chart(fig_cm_a, use_container_width=True)
        
        # Summary Stats
        st.markdown("---")
        st.markdown('<h2 class="section-header">📊 Dataset Summary & Diagnostics</h2>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'''
                <div class="metric-container">
                    <div class="metric-label">🚉 Total Stations</div>
                    <div class="metric-value">{len(df)}</div>
                </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''
                <div class="metric-container">
                    <div class="metric-label">🔄 Directions</div>
                    <div class="metric-value">{df['Direction'].nunique()}</div>
                </div>
            ''', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f'''
                <div class="metric-container">
                    <div class="metric-label">⏰ Time Slots</div>
                    <div class="metric-value">{len(time_slots)}</div>
                </div>
            ''', unsafe_allow_html=True)
        
        with col4:
            avg_acc = (metrics_boarding[time]['accuracy'] + metrics_alighting[time]['accuracy']) / 2
            st.markdown(f'''
                <div class="metric-container">
                    <div class="metric-label">🎯 Avg Accuracy</div>
                    <div class="metric-value">{avg_acc*100:.1f}%</div>
                </div>
            ''', unsafe_allow_html=True)
        
        # Data Distribution Analysis
        st.markdown('<h3 class="section-header">🔍 Class Distribution Analysis</h3>', unsafe_allow_html=True)
        
        rush_boarding_col = f'Rush_Boarding_{time}'
        rush_alighting_col = f'Rush_Alighting_{time}'
        
        col1, col2 = st.columns(2)
        
        with col1:
            boarding_dist = df[rush_boarding_col].value_counts()
            st.markdown(f'''
                <div class="glass-card">
                    <h4 style="color: #a78bfa; margin-bottom: 15px;">🚆 Boarding Classification</h4>
                    <div style="color: rgba(255,255,255,0.9);">
                        <p><strong>Not Crowded (0):</strong> {boarding_dist.get(0, 0)} stations ({boarding_dist.get(0, 0)/len(df)*100:.1f}%)</p>
                        <p><strong>Crowded (1):</strong> {boarding_dist.get(1, 0)} stations ({boarding_dist.get(1, 0)/len(df)*100:.1f}%)</p>
                        <p style="margin-top: 10px; color: #fbbf24;"><strong>⚠️ Note:</strong> If distribution is very imbalanced (like 90-10), 
                        the model might achieve high accuracy by just predicting the majority class.</p>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            alighting_dist = df[rush_alighting_col].value_counts()
            st.markdown(f'''
                <div class="glass-card">
                    <h4 style="color: #a78bfa; margin-bottom: 15px;">🚉 Alighting Classification</h4>
                    <div style="color: rgba(255,255,255,0.9);">
                        <p><strong>Not Crowded (0):</strong> {alighting_dist.get(0, 0)} stations ({alighting_dist.get(0, 0)/len(df)*100:.1f}%)</p>
                        <p><strong>Crowded (1):</strong> {alighting_dist.get(1, 0)} stations ({alighting_dist.get(1, 0)/len(df)*100:.1f}%)</p>
                        <p style="margin-top: 10px; color: #fbbf24;"><strong>⚠️ Note:</strong> Balanced classes (close to 50-50) lead to more reliable metrics.</p>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
        
        # Model Insights
        st.markdown('''
            <div class="info-box">
                <strong>📚 Understanding Your Metrics:</strong><br><br>
                
                <strong>Why might metrics be 100%?</strong><br>
                • <strong>Small dataset:</strong> With only 5 stations, the model might memorize patterns<br>
                • <strong>Clear patterns:</strong> If crowded vs not-crowded is very obvious from the data, perfect classification is possible<br>
                • <strong>Overfitting:</strong> Model might be too complex for the small dataset<br><br>
                
                <strong>What the metrics mean:</strong><br>
                • <strong>Accuracy:</strong> Overall correctness - (Correct predictions / Total predictions)<br>
                • <strong>Precision:</strong> Of all predicted crowded stations, how many were actually crowded<br>
                • <strong>Recall:</strong> Of all actually crowded stations, how many did we correctly identify<br>
                • <strong>F1 Score:</strong> Harmonic mean of precision and recall (balances both)<br><br>
                
                <strong>💡 Recommendation:</strong> Test with more diverse data for more realistic metrics!
            </div>
        ''', unsafe_allow_html=True)
    
    else:
        st.markdown('<h1 class="hero-title">🚇 Smart Metro Station Advisor</h1>', unsafe_allow_html=True)
        st.markdown('<p class="hero-subtitle">AI-Powered Congestion Prediction & Intelligent Route Planning</p>', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="glass-card" style="text-align: center;">
            <h2 style="color: #a78bfa; margin-bottom: 20px;">👈 Get Started</h2>
            <p style="color: rgba(255,255,255,0.8); font-size: 18px; line-height: 1.8;">
                Upload your metro station traffic data using the sidebar to begin intelligent congestion analysis
            </p>
        </div>
        ''', unsafe_allow_html=True)
        
        with st.expander("📋 Required Data Format", expanded=True):
            st.markdown("""
            <div style="color: rgba(255,255,255,0.9);">
            
            **Your Excel file should contain these columns:**
            
            - `Station` - Station name
            - `Direction` - Travel direction (e.g., Direction 1, Direction 2)
            - `Boarding_[TIME]` - Number of passengers boarding
            - `Alighting_[TIME]` - Number of passengers alighting
            - `PPHPD_[TIME]` - Passengers Per Hour Per Direction
            - `Distance from SBC` - Distance in kilometers from starting point
            
            **Example:** `Boarding_0800-0900`, `Alighting_1700-1800`, etc.
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()