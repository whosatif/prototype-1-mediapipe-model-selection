import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os

cwd = r'c:\Users\ATIF\Desktop\fyp project\prototype 1'

# --- 1. Model Comparison Bar Chart ---
labels = ['OpenPose', 'AlphaPose', 'HRNet', 'YOLOv8', 'MoveNet', 'MediaPipe']
fps = [5, 8, 3, 18, 32, 25]  # mobile edge performance estimates
memory = [1500, 1200, 2000, 600, 420, 95] # MB footprint (Updated to reflect actual prototype RAM usage)

fig, ax1 = plt.subplots(figsize=(8, 5))
x = np.arange(len(labels))
width = 0.35

bar1 = ax1.bar(x - width/2, fps, width, label='FPS (Higher is Better)', color='royalblue')
ax1.set_ylabel('Frames Per Second (FPS)', color='royalblue')
ax1.tick_params(axis='y', labelcolor='royalblue')
ax1.set_xticks(x)
ax1.set_xticklabels(labels, rotation=15)
line1 = ax1.axhline(20, color='gray', linestyle='--', alpha=0.5, label='Minimum Viable FPS')

ax2 = ax1.twinx()
bar2 = ax2.bar(x + width/2, memory, width, label='Memory Footprint (Lower is Better)', color='crimson')
ax2.set_ylabel('Memory (MB)', color='crimson')
ax2.tick_params(axis='y', labelcolor='crimson')

# Add Legend
lines, labels_leg = ax1.get_legend_handles_labels()
lines2, labels_leg2 = ax2.get_legend_handles_labels()
ax2.legend(lines + lines2, labels_leg + labels_leg2, loc='upper left')

plt.title('Edge Mobile Performance: Pose Estimation Models')
fig.tight_layout()
plt.savefig(os.path.join(cwd, 'model_comparison.png'), dpi=150)
plt.close()


# --- 2. Sensor Fusion Architecture ---
fig, ax = plt.subplots(figsize=(8, 4))
ax.axis('off')

# Drawing blocks
from matplotlib.patches import FancyBboxPatch

def draw_block(ax, text, xy, width, height, color):
    p = FancyBboxPatch(xy, width, height, boxstyle="round,pad=0.1", fc=color, ec="black", lw=1.5)
    ax.add_patch(p)
    ax.text(xy[0] + width/2, xy[1] + height/2, text, ha='center', va='center', fontsize=10, weight='bold')

draw_block(ax, "MediaPipe\n(3D Landmarks)", (0.1, 0.6), 0.3, 0.2, "lightgreen")
draw_block(ax, "Android IMU\n(Gyro/Accel)", (0.1, 0.2), 0.3, 0.2, "lightblue")
draw_block(ax, "Sensor Fusion Engine\n(Rotation Matrix)", (0.6, 0.4), 0.3, 0.2, "salmon")

# arrows
ax.annotate("", xy=(0.6, 0.55), xytext=(0.4, 0.7), arrowprops=dict(arrowstyle="->", lw=2))
ax.annotate("", xy=(0.6, 0.45), xytext=(0.4, 0.3), arrowprops=dict(arrowstyle="->", lw=2))

plt.title('Architecture: IMU-Based Perspective Calibration')
fig.tight_layout()
plt.savefig(os.path.join(cwd, 'sensor_fusion.png'), dpi=150)
plt.close()


# --- 3. Person Locking State Machine ---
G = nx.DiGraph()
G.add_edge('Idle', 'Set Started')
G.add_edge('Set Started', 'Active Lock\n(Save Morph Signature)')
G.add_edge('Active Lock\n(Save Morph Signature)', 'Active Lock\n(Save Morph Signature)')
G.add_edge('Active Lock\n(Save Morph Signature)', 'Ghost State\n(User Occluded)')
G.add_edge('Ghost State\n(User Occluded)', 'Active Lock\n(Save Morph Signature)')
G.add_edge('Ghost State\n(User Occluded)', 'Set Ended\n(Timeout)')
G.add_edge('Active Lock\n(Save Morph Signature)', 'Set Ended\n(Timeout)')

pos = {
    'Idle': (0, 1),
    'Set Started': (1, 1),
    'Active Lock\n(Save Morph Signature)': (2, 1),
    'Ghost State\n(User Occluded)': (2, 0),
    'Set Ended\n(Timeout)': (3, 1)
}

plt.figure(figsize=(8, 4))
nx.draw(G, pos, with_labels=True, node_size=4000, node_color='lightgoldenrodyellow', edge_color='gray', 
        font_size=8, font_weight='bold', arrowsize=20, node_shape='s')

# Adjust edge curve for self-loop manually or let networkx handle it (it does okay)
plt.title('State Machine: Morphological Person Locking')
plt.tight_layout()
plt.savefig(os.path.join(cwd, 'person_locking.png'), dpi=150)
plt.close()

print("Images generated.")
