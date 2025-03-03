import pandas as pd
import plotly.graph_objects as go
import math

#-----------------------------------------------------------
# 1) Read the CSV
#    Replace 'packages.csv' with your actual filename/path
#-----------------------------------------------------------
df = pd.read_csv("Cleaned_Package_Data.csv")

#-----------------------------------------------------------
# 2) Group "Carriers" into five categories:
#    Amazon, USPS, UPS, FedEx, and "Other Carriers"
#-----------------------------------------------------------
def bucket_carrier(carrier_name):
    major_carriers = ["Amazon", "USPS", "UPS", "FedEx"]
    if carrier_name in major_carriers:
        return carrier_name
    else:
        return "Other Carriers"

df["Carrier_Bucket"] = df["Carrier"].apply(bucket_carrier)

#-----------------------------------------------------------
# 3) Compute total package count + average processing time
#    for each carrier bucket
#-----------------------------------------------------------
carrier_stats = df.groupby("Carrier_Bucket").agg(
    Total_Packages = ("Tracking #", "count"),
    Avg_Processing_Time = ("Processing Time (Hours)", "mean")
).reset_index()

# Convert any NaN averages to 0 or to "N/A"
carrier_stats["Avg_Processing_Time"] = carrier_stats["Avg_Processing_Time"].fillna(0)

# Make a quick dictionary for easy lookup
bucket_info = {
    row["Carrier_Bucket"]: {
        "count": row["Total_Packages"],
        "avg": row["Avg_Processing_Time"]
    }
    for _, row in carrier_stats.iterrows()
}

# For convenience, define the 5 final labels we expect:
ALL_BUCKETS = ["Amazon", "USPS", "UPS", "FedEx", "Other Carriers"]

# If a bucket is missing from the data, set it to 0
for b in ALL_BUCKETS:
    if b not in bucket_info:
        bucket_info[b] = {"count": 0, "avg": 0.0}

#-----------------------------------------------------------
# 4) Total packages = sum of all carriers
#-----------------------------------------------------------
total_pkgs = sum(bucket_info[b]["count"] for b in ALL_BUCKETS)

#-----------------------------------------------------------
# 5) Build Sankey nodes with enhanced styling:
#-----------------------------------------------------------

# Enhanced function to create carrier label with HTML formatting
def carrier_label(name):
    ccount = bucket_info[name]["count"]
    cavg = bucket_info[name]["avg"]

    # Color coding for processing time
    color = "#66BB6A"  # Green (good)
    if cavg > 100:
        color = "#D32F2F"  # Red (poor)
    elif cavg > 70:
        color = "#EF6C00"  # Dark orange (concerning)
    elif cavg > 40:
        color = "#FFA726"  # Orange (moderate)

    if ccount == 0:
        return f"<b>{name}</b><br>0 packages<br>N/A hours avg."
    else:
        return f"<b>{name}</b><br>{ccount} packages<br><span style='color:{color}'>{cavg:.1f} hours avg.</span>"

# Define node positions for better visual layout
node_labels = [
    "<b>Package Arrival</b>",         # 0
    "<b>Assignment</b>",              # 1
    "<b>Locker Storage</b>",          # 2
    carrier_label("Amazon"),          # 3
    carrier_label("USPS"),            # 4
    carrier_label("UPS"),             # 5
    carrier_label("FedEx"),           # 6
    carrier_label("Other Carriers"),  # 7
    "<b>Delivery/Pickup</b>"          # 8
]

# Node positions using x,y coordinates for better layout
node_x = [
    0.00,  # Package Arrival
    0.15,  # Assignment
    0.35,  # Locker Storage
    0.60,  # Amazon
    0.60,  # USPS
    0.60,  # UPS
    0.60,  # FedEx
    0.60,  # Other Carriers
    0.90   # Delivery/Pickup
]

# Position carriers in a vertical arrangement
node_y = [
    0.5,   # Package Arrival
    0.5,   # Assignment
    0.5,   # Locker Storage
    0.15,  # Amazon (top)
    0.3,   # USPS
    0.5,   # UPS (middle)
    0.7,   # FedEx
    0.85,  # Other Carriers (bottom)
    0.5    # Delivery/Pickup
]

# Enhanced node colors (from React sample)
node_colors = [
    "#4682B4",  # Package Arrival (Steel Blue)
    "#6495ED",  # Assignment (Cornflower Blue)
    "#87CEEB",  # Locker Storage (Sky Blue)
    "#FF9900",  # Amazon (Amazon Orange)
    "#004B87",  # USPS (USPS Blue)
    "#351C15",  # UPS (UPS Brown)
    "#4D148C",  # FedEx (FedEx Purple)
    "#888888",  # Other Carriers (Gray)
    "#66BB6A"   # Delivery/Pickup (Green)
]

#-----------------------------------------------------------
# 6) Build Sankey links (source, target, value, color)
#
#    Layout:
#     (0)Arrival → (1)Assignment → (2)Locker → each carrier → (8)Delivery
#-----------------------------------------------------------

PACK_ARR = 0
ASSIGN   = 1
LOCKER   = 2
AMAZON   = 3
USPS     = 4
UPS      = 5
FEDEX    = 6
OTHERS   = 7
DELIVER  = 8

source = []
target = []
value  = []
link_colors = []

# Utility function to get color based on processing time
def get_color_by_time(time):
    if time == 0:
        return "rgba(150,150,150,0.4)"
    if time < 40:
        return "rgba(102,187,106,0.7)"  # Green
    if time < 70:
        return "rgba(255,167,38,0.7)"   # Yellow
    if time < 100:
        return "rgba(239,108,0,0.7)"    # Orange
    return "rgba(211,47,47,0.7)"        # Red

# (A) Arrival → Assignment (all packages)
source.append(PACK_ARR)
target.append(ASSIGN)
value.append(total_pkgs)
link_colors.append("rgba(150,150,150,0.6)")

# (B) Assignment → Locker Storage (all packages)
source.append(ASSIGN)
target.append(LOCKER)
value.append(total_pkgs)
link_colors.append("rgba(135,206,235,0.6)")

# (C) Locker Storage → each carrier
# (D) each carrier → Delivery/Pickup
carrier_node_map = {
    "Amazon": AMAZON,
    "USPS": USPS,
    "UPS": UPS,
    "FedEx": FEDEX,
    "Other Carriers": OTHERS
}

for name in ALL_BUCKETS:
    node_idx = carrier_node_map[name]
    c_count = bucket_info[name]["count"]
    c_time = bucket_info[name]["avg"]
    c_color = get_color_by_time(c_time)

    # Locker → carrier (colored by processing time)
    source.append(LOCKER)
    target.append(node_idx)
    value.append(c_count)
    link_colors.append(c_color)

    # carrier → Delivery (match carrier node color, but transparent)
    source.append(node_idx)
    target.append(DELIVER)
    value.append(c_count)
    link_colors.append(node_colors[node_idx].replace(")", ",0.7)").replace("rgb", "rgba"))

#-----------------------------------------------------------
# 7) Build and display the Sankey figure with enhanced layout
#-----------------------------------------------------------
fig = go.Figure(data=[go.Sankey(
    arrangement="fixed",  # Fixed positions for better control
    node=dict(
        label=node_labels,
        x=node_x,
        y=node_y,
        pad=20,
        thickness=20,
        color=node_colors,
        line=dict(color="black", width=0.5)
    ),
    link=dict(
        source=source,
        target=target,
        value=value,
        color=link_colors,
        hovertemplate='%{source.label} → %{target.label}<br>Packages: %{value}<extra></extra>'
    )
)])

# Add a title and annotations
fig.update_layout(
    title=dict(
        text="<b>Package Flow by Carrier</b>",
        font=dict(size=24),
        x=0.5,
        y=0.98
    ),
    font=dict(size=14),
    plot_bgcolor="white",
    annotations=[
        # Legend for processing time
        dict(
            x=0.01, y=0.01,
            xref="paper", yref="paper",
            text="<b>Processing Time:</b>",
            showarrow=False
        ),
        dict(
            x=0.01, y=-0.05,
            xref="paper", yref="paper",
            text="<span style='color:#66BB6A'>◼</span> < 40 hrs",
            showarrow=False
        ),
        dict(
            x=0.12, y=-0.05,
            xref="paper", yref="paper",
            text="<span style='color:#FFA726'>◼</span> 40-70 hrs",
            showarrow=False
        ),
        dict(
            x=0.23, y=-0.05,
            xref="paper", yref="paper",
            text="<span style='color:#EF6C00'>◼</span> 70-100 hrs",
            showarrow=False
        ),
        dict(
            x=0.34, y=-0.05,
            xref="paper", yref="paper",
            text="<span style='color:#D32F2F'>◼</span> > 100 hrs",
            showarrow=False
        )
    ],
    margin=dict(l=50, r=50, t=70, b=100)
)

fig.show()