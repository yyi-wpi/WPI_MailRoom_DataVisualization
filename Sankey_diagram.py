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

# Convert any NaN averages to 0 or to “N/A”
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
# 5) Build Sankey nodes:
#
#    We'll define 9 nodes (indexed 0..8)
#      0) Package Arrival
#      1) Assignment
#      2) Locker Storage
#      3) Amazon
#      4) USPS
#      5) UPS
#      6) FedEx
#      7) Other Carriers
#      8) Delivery/Pickup
#
#    We’ll label each carrier node with “Carrier Name
#    XXX packages
#    YYY hours avg.”
#-----------------------------------------------------------

def carrier_label(name):
    ccount = bucket_info[name]["count"]
    cavg   = bucket_info[name]["avg"]
    if ccount == 0:
        return f"{name}\n0 packages\nN/A hours avg."
    else:
        return f"{name}\n{ccount} packages\n{cavg:.1f} hours avg."

node_labels = [
    "Package Arrival",         # 0
    "Assignment",              # 1
    "Locker Storage",          # 2
    carrier_label("Amazon"),   # 3
    carrier_label("USPS"),     # 4
    carrier_label("UPS"),      # 5
    carrier_label("FedEx"),    # 6
    carrier_label("Other Carriers"),  # 7
    "Delivery/Pickup"          # 8
]

# We'll manually position the nodes in columns, similar to the reference image.
node_x = [
    0.00,  # Package Arrival
    0.10,  # Assignment
    0.30,  # Locker Storage
    0.55,  # Amazon
    0.55,  # USPS
    0.55,  # UPS
    0.55,  # FedEx
    0.55,  # Other Carriers
    0.90   # Delivery/Pickup
]

node_y = [
    0.5,   # Package Arrival
    0.5,   # Assignment
    0.5,   # Locker Storage

    0.2,   # Amazon
    0.35,  # USPS
    0.50,  # UPS
    0.65,  # FedEx
    0.80,  # Other

    0.5    # Delivery/Pickup
]

# Node colors
node_colors = [
    "rgba(20, 60, 120, 0.8)",   # Arrival (dark blue)
    "rgba(60, 120, 200, 0.8)",  # Assignment (lighter blue)
    "rgba(80, 50, 20, 0.8)",    # Locker Storage (brown)
    "rgba(255, 153, 51, 0.8)",  # Amazon (orange)
    "rgba(70, 130, 180, 0.8)",  # USPS (steelblue)
    "rgba(101, 67, 33, 0.8)",   # UPS (chocolate)
    "rgba(128, 0, 128, 0.8)",   # FedEx (purple)
    "rgba(128, 128, 128, 0.8)", # Other Carriers (gray)
    "rgba(0, 128, 0, 0.8)"      # Delivery/Pickup (green)
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

# (A) Arrival → Assignment (all packages)
source.append(PACK_ARR)
target.append(ASSIGN)
value.append(total_pkgs)
link_colors.append("rgba(150,150,150,0.4)")

# (B) Assignment → Locker Storage (all packages)
source.append(ASSIGN)
target.append(LOCKER)
value.append(total_pkgs)
link_colors.append("rgba(150,150,150,0.4)")

# (C) Locker Storage → each carrier
# (D) each carrier → Delivery/Pickup
#   We’ll color these links to match each carrier’s node color
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
    c_color = node_colors[node_idx]

    # Locker → carrier
    source.append(LOCKER)
    target.append(node_idx)
    value.append(c_count)
    link_colors.append(c_color)

    # carrier → Delivery
    source.append(node_idx)
    target.append(DELIVER)
    value.append(c_count)
    link_colors.append(c_color)

#-----------------------------------------------------------
# 7) Build and display the Sankey figure
#-----------------------------------------------------------
fig = go.Figure(data=[go.Sankey(
    arrangement="snap",
    node=dict(
        label=node_labels,
        x=node_x,
        y=node_y,
        pad=15,
        thickness=20,
        color=node_colors
    ),
    link=dict(
        source=source,
        target=target,
        value=value,
        color=link_colors
    )
)])

fig.update_layout(
    title_text="Package Flow by Carrier (from CSV)",
    font_size=12
)

fig.show()