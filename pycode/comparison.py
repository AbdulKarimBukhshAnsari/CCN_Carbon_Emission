#!/usr/bin/env python3
"""
Before/After Comparison Module
Tracks and displays carbon emission changes
"""

import time
from typing import List, Tuple
from prettytable import PrettyTable

class EmissionComparison:
    """Track and compare emissions before and after reduction"""
    
    def __init__(self):
        self.before_metrics = []
        self.after_metrics = []
        self.before_total_energy = 0.0
        self.before_total_carbon = 0.0
        self.after_total_energy = 0.0
        self.after_total_carbon = 0.0
    
    def record_before(self, metrics: List[Tuple[int, int, int, float, float]]):
        """
        Record baseline metrics before reduction
        metrics: List of (pid, cpu_time_ns, packets, energy, carbon)
        """
        self.before_metrics = metrics.copy()
        self.before_total_energy = sum(m[3] for m in metrics)
        self.before_total_carbon = sum(m[4] for m in metrics)
    
    def record_after(self, metrics: List[Tuple[int, int, int, float, float]]):
        """
        Record metrics after reduction
        metrics: List of (pid, cpu_time_ns, packets, energy, carbon)
        """
        self.after_metrics = metrics.copy()
        self.after_total_energy = sum(m[3] for m in metrics)
        self.after_total_carbon = sum(m[4] for m in metrics)
    
    def calculate_savings(self) -> dict:
        """Calculate energy and carbon savings"""
        energy_saved = self.before_total_energy - self.after_total_energy
        carbon_saved = self.before_total_carbon - self.after_total_carbon
        
        energy_reduction_percent = (energy_saved / self.before_total_energy * 100) if self.before_total_energy > 0 else 0
        carbon_reduction_percent = (carbon_saved / self.before_total_carbon * 100) if self.before_total_carbon > 0 else 0
        
        return {
            'energy_saved': energy_saved,
            'carbon_saved': carbon_saved,
            'energy_reduction_percent': energy_reduction_percent,
            'carbon_reduction_percent': carbon_reduction_percent
        }
    
    def display_comparison(self):
        """Display side-by-side comparison"""
        print("\n" + "="*80)
        print("📊 BEFORE vs AFTER COMPARISON")
        print("="*80)
        
        # Before Table
        print("\n🔴 BEFORE Reduction:")
        print("-" * 80)
        table_before = PrettyTable()
        table_before.field_names = ["PID", "CPU Time (ms)", "Packets", "Energy (J)", "Carbon (g CO2)"]
        
        for pid, cpu_time_ns, packets, energy, carbon in sorted(self.before_metrics, key=lambda x: x[4], reverse=True)[:10]:
            cpu_ms = cpu_time_ns / 1_000_000
            table_before.add_row([
                pid,
                f"{cpu_ms:.2f}",
                packets,
                f"{energy:.6f}",
                f"{carbon:.6f}"
            ])
        
        print(table_before)
        print(f"\n  📊 Total Energy: {self.before_total_energy:.6f} J")
        print(f"  🌍 Total Carbon: {self.before_total_carbon:.6f} g CO2")
        print(f"  💡 Equivalent to: {self.before_total_carbon/1000:.9f} kg CO2")
        
        # After Table
        print("\n\n🟢 AFTER Reduction:")
        print("-" * 80)
        table_after = PrettyTable()
        table_after.field_names = ["PID", "CPU Time (ms)", "Packets", "Energy (J)", "Carbon (g CO2)"]
        
        for pid, cpu_time_ns, packets, energy, carbon in sorted(self.after_metrics, key=lambda x: x[4], reverse=True)[:10]:
            cpu_ms = cpu_time_ns / 1_000_000
            table_after.add_row([
                pid,
                f"{cpu_ms:.2f}",
                packets,
                f"{energy:.6f}",
                f"{carbon:.6f}"
            ])
        
        print(table_after)
        print(f"\n  📊 Total Energy: {self.after_total_energy:.6f} J")
        print(f"  🌍 Total Carbon: {self.after_total_carbon:.6f} g CO2")
        print(f"  💡 Equivalent to: {self.after_total_carbon/1000:.9f} kg CO2")
        
        # Savings Summary
        savings = self.calculate_savings()
        print("\n\n" + "="*80)
        print("💰 SAVINGS SUMMARY")
        print("="*80)
        print(f"\n  ⚡ Energy Saved: {savings['energy_saved']:.6f} J ({savings['energy_reduction_percent']:.2f}% reduction)")
        print(f"  🌱 Carbon Saved: {savings['carbon_saved']:.6f} g CO2 ({savings['carbon_reduction_percent']:.2f}% reduction)")
        print(f"  📉 Carbon Reduction: {savings['carbon_saved']/1000:.9f} kg CO2")
        
        if savings['carbon_saved'] > 0:
            print(f"\n  ✅ Successfully reduced carbon emissions!")
        else:
            print(f"\n  ⚠️  No significant reduction detected (processes may have increased activity)")
        
        print("\n" + "="*80)
    
    def display_compact_comparison(self):
        """Display compact comparison"""
        print("\n" + "="*60)
        print("📊 EMISSION COMPARISON")
        print("="*60)
        
        savings = self.calculate_savings()
        
        print(f"\n  BEFORE:")
        print(f"    Energy:  {self.before_total_energy:.4f} J")
        print(f"    Carbon:  {self.before_total_carbon:.6f} g CO2")
        
        print(f"\n  AFTER:")
        print(f"    Energy:  {self.after_total_energy:.4f} J")
        print(f"    Carbon:  {self.after_total_carbon:.6f} g CO2")
        
        print(f"\n  SAVINGS:")
        print(f"    Energy:  -{savings['energy_saved']:.4f} J ({savings['energy_reduction_percent']:.1f}%)")
        print(f"    Carbon:  -{savings['carbon_saved']:.6f} g CO2 ({savings['carbon_reduction_percent']:.1f}%)")
        
        print("\n" + "="*60)


def display_top_emitters(metrics: List[Tuple[int, int, int, float, float]], top_n: int = 10):
    """Display top carbon emitters"""
    import psutil
    
    sorted_metrics = sorted(metrics, key=lambda x: x[4], reverse=True)[:top_n]
    
    print(f"\n🔥 Top {top_n} Carbon Emitters:")
    print("-" * 80)
    
    table = PrettyTable()
    table.field_names = ["Rank", "PID", "Process Name", "Energy (J)", "Carbon (g CO2)"]
    
    for rank, (pid, cpu_time_ns, packets, energy, carbon) in enumerate(sorted_metrics, 1):
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            proc_name = "Unknown"
        
        table.add_row([
            rank,
            pid,
            proc_name[:20],  # Truncate long names
            f"{energy:.6f}",
            f"{carbon:.6f}"
        ])
    
    print(table)
