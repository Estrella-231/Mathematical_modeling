"""
3D Uncertainty Visualization
Creates a high-quality 3D surface plot showing uncertainty across seasons and weeks
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path

# Configure matplotlib for publication-quality scientific figures
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 14
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

def load_uncertainty_data():
    """Load V2 model output with uncertainty estimates"""
    data_path = Path(__file__).parent.parent / 'Data' / 'models' / 'ridge_v2' / 'ridge_fan_vote_shares_v2.csv'
    df = pd.read_csv(data_path)
    return df

def prepare_3d_data(df):
    """
    Prepare data for 3D surface plot
    Returns X (season), Y (week), Z (uncertainty) meshgrids
    """
    # Calculate mean uncertainty per season-week
    heatmap_data = df.groupby(['season', 'week'])['uncertainty_upper'].mean().reset_index()

    # Pivot to create matrix format
    pivot_data = heatmap_data.pivot(index='week', columns='season', values='uncertainty_upper')

    # Fill missing values with interpolation for smooth surface
    pivot_data_filled = pivot_data.interpolate(method='linear', axis=1, limit_direction='both')
    pivot_data_filled = pivot_data_filled.interpolate(method='linear', axis=0, limit_direction='both')

    # Create meshgrid
    seasons = pivot_data_filled.columns.values
    weeks = pivot_data_filled.index.values
    X, Y = np.meshgrid(seasons, weeks)
    Z = pivot_data_filled.values

    return X, Y, Z, pivot_data

def create_3d_surface_plot(X, Y, Z, output_dir):
    """
    Create publication-quality 3D surface plot
    """
    # Create figure with larger size for 3D
    fig = plt.figure(figsize=(16, 10), dpi=300)
    ax = fig.add_subplot(111, projection='3d')

    # Create surface plot with scientific colormap
    # Using 'Reds' for uncertainty (white=low, deep red=high)
    surf = ax.plot_surface(
        X, Y, Z,
        cmap='Reds',
        edgecolor='none',
        alpha=0.9,
        antialiased=True,
        shade=True,
        linewidth=0,
        rcount=50,
        ccount=50
    )

    # Add contour lines on the bottom for reference
    ax.contour(X, Y, Z, zdir='z', offset=Z.min()-0.02, cmap='Reds', alpha=0.4, linewidths=1)

    # Customize axes
    ax.set_xlabel('Season', fontsize=13, fontweight='bold', labelpad=10)
    ax.set_ylabel('Week', fontsize=13, fontweight='bold', labelpad=10)
    ax.set_zlabel('Uncertainty (SE)', fontsize=13, fontweight='bold', labelpad=10)

    # Set title
    ax.set_title('Fan Vote Uncertainty Across Seasons and Weeks\n(Ridge Regression Model V2)',
                 fontsize=14, fontweight='bold', pad=20)

    # Customize viewing angle for better perspective
    ax.view_init(elev=25, azim=45)

    # Set z-axis limits for better visualization
    z_min = Z.min() - 0.02
    z_max = Z.max() + 0.02
    ax.set_zlim(z_min, z_max)

    # Customize tick parameters
    ax.tick_params(axis='x', which='major', pad=5)
    ax.tick_params(axis='y', which='major', pad=5)
    ax.tick_params(axis='z', which='major', pad=8)

    # Add colorbar
    cbar = fig.colorbar(surf, ax=ax, shrink=0.6, aspect=15, pad=0.1)
    cbar.set_label('Uncertainty (Standard Error)', fontsize=11, fontweight='bold')

    # Improve grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

    # Tight layout
    plt.tight_layout()

    # Save figure
    output_path_png = output_dir / 'uncertainty_3d_surface.png'
    output_path_pdf = output_dir / 'uncertainty_3d_surface.pdf'

    plt.savefig(output_path_png, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path_pdf, bbox_inches='tight', facecolor='white')

    print(f"[OK] 3D surface plot saved to:")
    print(f"  - {output_path_png}")
    print(f"  - {output_path_pdf}")

    plt.close()

    return output_path_png, output_path_pdf

def create_3d_wireframe_plot(X, Y, Z, output_dir):
    """
    Create alternative wireframe visualization
    """
    fig = plt.figure(figsize=(16, 10), dpi=300)
    ax = fig.add_subplot(111, projection='3d')

    # Create wireframe plot
    wire = ax.plot_wireframe(
        X, Y, Z,
        color='#C0392B',
        alpha=0.6,
        linewidth=1.2,
        rcount=20,
        ccount=20
    )




 


    # Add surface with transparency
    surf = ax.plot_surface(
        X, Y, Z,
        cmap='Reds',
        alpha=0.3,
        antialiased=True,
        shade=True
    )

    # Customize axes
    ax.set_xlabel('Season', fontsize=13, fontweight='bold', labelpad=10)
    ax.set_ylabel('Week', fontsize=13, fontweight='bold', labelpad=10)
    ax.set_zlabel('Uncertainty (SE)', fontsize=13, fontweight='bold', labelpad=10)

    ax.set_title('Fan Vote Uncertainty - Wireframe View\n(Ridge Regression Model V2)',
                 fontsize=14, fontweight='bold', pad=20)

    # Viewing angle
    ax.view_init(elev=25, azim=45)

    # Set limits
    z_min = Z.min() - 0.02
    z_max = Z.max() + 0.02
    ax.set_zlim(z_min, z_max)

    # Grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

    plt.tight_layout()

    # Save
    output_path_png = output_dir / 'uncertainty_3d_wireframe.png'
    output_path_pdf = output_dir / 'uncertainty_3d_wireframe.pdf'

    plt.savefig(output_path_png, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path_pdf, bbox_inches='tight', facecolor='white')

    print(f"[OK] 3D wireframe plot saved to:")
    print(f"  - {output_path_png}")
    print(f"  - {output_path_pdf}")

    plt.close()

    return output_path_png, output_path_pdf

def create_multiple_views(X, Y, Z, output_dir):
    """
    Create a figure with multiple viewing angles
    """
    fig = plt.figure(figsize=(18, 12), dpi=300)

    views = [
        (25, 45, 'View 1: Standard'),
        (25, 135, 'View 2: Rotated 90°'),
        (60, 45, 'View 3: Top View'),
        (10, 45, 'View 4: Side View')
    ]

    for idx, (elev, azim, title) in enumerate(views, 1):
        ax = fig.add_subplot(2, 2, idx, projection='3d')

        surf = ax.plot_surface(
            X, Y, Z,
            cmap='Reds',
            edgecolor='none',
            alpha=0.9,
            antialiased=True,
            shade=True
        )

        ax.set_xlabel('Season', fontsize=10, fontweight='bold')
        ax.set_ylabel('Week', fontsize=10, fontweight='bold')
        ax.set_zlabel('Uncertainty', fontsize=10, fontweight='bold')
        ax.set_title(title, fontsize=11, fontweight='bold')

        ax.view_init(elev=elev, azim=azim)
        ax.grid(True, alpha=0.3)

        z_min = Z.min() - 0.02
        z_max = Z.max() + 0.02
        ax.set_zlim(z_min, z_max)

    plt.suptitle('Fan Vote Uncertainty - Multiple Perspectives',
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()

    output_path_png = output_dir / 'uncertainty_3d_multiview.png'
    output_path_pdf = output_dir / 'uncertainty_3d_multiview.pdf'

    plt.savefig(output_path_png, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path_pdf, bbox_inches='tight', facecolor='white')

    print(f"[OK] Multi-view plot saved to:")
    print(f"  - {output_path_png}")
    print(f"  - {output_path_pdf}")

    plt.close()

    return output_path_png, output_path_pdf

def main():
    """Main execution"""
    print("=" * 60)
    print("3D Uncertainty Visualization")
    print("=" * 60)

    # Load data
    print("\n[1/5] Loading uncertainty data...")
    df = load_uncertainty_data()
    print(f"  Loaded {len(df)} contestant-week observations")
    print(f"  Seasons: {df['season'].min()} to {df['season'].max()}")
    print(f"  Weeks: {df['week'].min()} to {df['week'].max()}")

    # Prepare 3D data
    print("\n[2/5] Preparing 3D surface data...")
    X, Y, Z, pivot_data = prepare_3d_data(df)
    print(f"  Surface dimensions: {Z.shape[0]} weeks x {Z.shape[1]} seasons")
    print(f"  Z-axis range: [{Z.min():.4f}, {Z.max():.4f}]")

    # Create output directory
    output_dir = Path(__file__).parent.parent / 'figures' / 'uncertainty'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create 3D surface plot
    print("\n[3/5] Creating 3D surface plot...")
    create_3d_surface_plot(X, Y, Z, output_dir)

    # Create wireframe plot
    print("\n[4/5] Creating 3D wireframe plot...")
    create_3d_wireframe_plot(X, Y, Z, output_dir)

    # Create multi-view plot
    print("\n[5/5] Creating multi-view plot...")
    create_multiple_views(X, Y, Z, output_dir)

    print("\n" + "=" * 60)
    print("[OK] 3D Visualization complete!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  1. uncertainty_3d_surface.png/pdf - Main 3D surface plot")
    print("  2. uncertainty_3d_wireframe.png/pdf - Wireframe view")
    print("  3. uncertainty_3d_multiview.png/pdf - Multiple perspectives")

if __name__ == '__main__':
    main()
