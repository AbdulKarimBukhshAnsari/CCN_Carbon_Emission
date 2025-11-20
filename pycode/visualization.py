#!/usr/bin/env python3
"""
Visualization Module
Creates charts to visualize carbon emissions before and after reduction
"""

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for WSL
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

import psutil
from typing import List, Tuple


def create_comparison_chart(
    before_metrics: List[Tuple[int, int, int, float, float]],
    after_metrics: List[Tuple[int, int, int, float, float]],
    output_file: str = 'carbon_comparison.png',
    top_n: int = 10
):
    """
    Create a bar chart comparing carbon emissions before and after reduction
    
    Args:
        before_metrics: List of (pid, cpu_time_ns, packets, energy, carbon) before
        after_metrics: List of (pid, cpu_time_ns, packets, energy, carbon) after
        output_file: Path to save the chart
        top_n: Number of top processes to display
    """
    if not MATPLOTLIB_AVAILABLE:
        print("\n⚠️  Matplotlib not available. Skipping visualization.")
        print("   Install with: sudo apt-get install python3-matplotlib")
        return False
    
    # Sort by carbon emissions
    before_sorted = sorted(before_metrics, key=lambda x: x[4], reverse=True)[:top_n]
    
    # Create mapping of PID to carbon
    before_carbon = {pid: carbon for pid, _, _, _, carbon in before_sorted}
    after_carbon_map = {pid: carbon for pid, _, _, _, carbon in after_metrics}
    
    # Prepare data
    pids = []
    process_names = []
    carbon_before = []
    carbon_after = []
    
    for pid, _, _, _, carbon in before_sorted:
        pids.append(pid)
        
        try:
            proc = psutil.Process(pid)
            name = proc.name()[:15]  # Truncate name
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            name = f"PID {pid}"
        
        process_names.append(f"{name}\n({pid})")
        carbon_before.append(carbon)
        carbon_after.append(after_carbon_map.get(pid, 0))
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Plot 1: Side-by-side comparison
    x = range(len(process_names))
    width = 0.35
    
    bars1 = ax1.bar([i - width/2 for i in x], carbon_before, width, label='Before', color='#ff6b6b', alpha=0.8)
    bars2 = ax1.bar([i + width/2 for i in x], carbon_after, width, label='After', color='#51cf66', alpha=0.8)
    
    ax1.set_xlabel('Process', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Carbon Emissions (g CO2)', fontsize=12, fontweight='bold')
    ax1.set_title(f'Top {top_n} Carbon Emitters: Before vs After Reduction', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(process_names, rotation=45, ha='right', fontsize=9)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.4f}',
                        ha='center', va='bottom', fontsize=7)
    
    # Plot 2: Total emissions pie chart
    total_before = sum(carbon_before)
    total_after = sum(carbon_after)
    savings = total_before - total_after
    
    if total_before > 0:
        reduction_percent = (savings / total_before) * 100
    else:
        reduction_percent = 0
    
    # Pie chart data
    sizes = [total_after, savings] if savings > 0 else [total_before]
    labels = ['Remaining Emissions', 'Saved Emissions'] if savings > 0 else ['Total Emissions']
    colors = ['#ff6b6b', '#51cf66'] if savings > 0 else ['#ff6b6b']
    explode = (0.05, 0.1) if savings > 0 else (0,)
    
    ax2.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90, textprops={'fontsize': 11})
    ax2.set_title(f'Carbon Emission Reduction\nTotal Saved: {savings:.6f} g CO2 ({reduction_percent:.1f}%)',
                  fontsize=14, fontweight='bold')
    
    # Add summary text
    summary_text = f'Before: {total_before:.6f} g CO2\nAfter: {total_after:.6f} g CO2'
    ax2.text(0, -1.3, summary_text, ha='center', fontsize=11, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n📈 Chart saved to: {output_file}")
    
    return True


def create_simple_bar_chart(
    metrics: List[Tuple[int, int, int, float, float]],
    output_file: str = 'carbon_emissions.png',
    title: str = 'Carbon Emissions by Process',
    top_n: int = 15
):
    """
    Create a simple bar chart of carbon emissions
    
    Args:
        metrics: List of (pid, cpu_time_ns, packets, energy, carbon)
        output_file: Path to save the chart
        title: Chart title
        top_n: Number of processes to display
    """
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    sorted_metrics = sorted(metrics, key=lambda x: x[4], reverse=True)[:top_n]
    
    process_labels = []
    carbon_values = []
    
    for pid, _, _, _, carbon in sorted_metrics:
        try:
            proc = psutil.Process(pid)
            name = proc.name()[:12]
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            name = f"PID {pid}"
        
        process_labels.append(f"{name}\n({pid})")
        carbon_values.append(carbon)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    bars = ax.barh(range(len(process_labels)), carbon_values, color='#339af0', alpha=0.8)
    
    ax.set_yticks(range(len(process_labels)))
    ax.set_yticklabels(process_labels, fontsize=9)
    ax.set_xlabel('Carbon Emissions (g CO2)', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars, carbon_values)):
        ax.text(value, i, f' {value:.4f}', va='center', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n📊 Chart saved to: {output_file}")
    
    return True
