#!/usr/bin/env python3
"""
🌍 Carbon Emission Monitor with Real Reduction Strategies
Interactive CEP (Carbon Emission Project) System

This program monitors carbon emissions and applies REAL reduction strategies.
"""

import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')

import psutil
import time
import os
from typing import List, Tuple

from energy_calc import estimate_energy, estimate_carbon
from comparison import EmissionComparison, display_top_emitters
from reduction_strategies import apply_strategy_to_top_emitters, cleanup_strategy
from visualization import create_comparison_chart, MATPLOTLIB_AVAILABLE


def collect_metrics() -> List[Tuple[int, int, int, float, float]]:
    """
    Collect current system metrics
    Returns: List of (pid, cpu_time_ns, packets_estimate, energy, carbon)
    """
    metrics = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_times', 'num_ctx_switches']):
        try:
            pid = proc.info['pid']
            cpu_times = proc.info['cpu_times']
            
            if cpu_times is None:
                continue
            
            # Calculate CPU time in nanoseconds
            cpu_time_s = cpu_times.user + cpu_times.system
            cpu_time_ns = int(cpu_time_s * 1_000_000_000)
            
            # Estimate network activity
            ctx_switches = proc.info['num_ctx_switches']
            if ctx_switches:
                packets_estimate = ctx_switches.voluntary + ctx_switches.involuntary
            else:
                packets_estimate = 0
            
            # Only track processes with significant activity
            if cpu_time_ns > 50_000_000:  # > 50ms
                energy = estimate_energy(cpu_time_ns, packets_estimate)
                carbon = estimate_carbon(energy)
                
                metrics.append((pid, cpu_time_ns, packets_estimate, energy, carbon))
        
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return metrics


def display_menu():
    """Display interactive menu"""
    print("\n" + "="*70)
    print("🌍 CARBON REDUCTION STRATEGIES")
    print("="*70)
    print("\nChoose a reduction strategy:\n")
    print("  1️⃣  PAUSE high-emission processes (SIGSTOP)")
    print("       → Temporarily stop processes to save energy")
    print()
    print("  2️⃣  LOWER PRIORITY (renice)")
    print("       → Reduce CPU priority of high-emission processes")
    print()
    print("  3️⃣  LIMIT CPU usage (cpulimit)")
    print("       → Restrict CPU usage to 30% for high-emission processes")
    print()
    print("  4️⃣  TERMINATE processes (use with caution!)")
    print("       → Kill high-emission non-critical processes")
    print()
    print("  5️⃣  SKIP reduction (just monitor)")
    print()
    print("  0️⃣  EXIT")
    print("\n" + "="*70)


def main():
    """Main interactive program"""
    
    print("\n" + "="*70)
    print("🌍 CARBON EMISSION MONITOR & REDUCTION SYSTEM")
    print("="*70)
    print("\nThis tool monitors process-level carbon emissions and applies")
    print("REAL reduction strategies to decrease your carbon footprint.")
    print("\nPress Ctrl+C at any time to exit safely.")
    print("="*70)
    
    try:
        # Step 1: Collect BEFORE metrics
        print("\n📊 Step 1: Collecting baseline metrics...")
        print("   (Monitoring system for 3 seconds...)")
        time.sleep(3)
        
        before_metrics = collect_metrics()
        
        if not before_metrics:
            print("\n⚠️  No significant process activity detected.")
            print("   Try running some applications and try again.")
            return
        
        print(f"   ✅ Collected metrics for {len(before_metrics)} processes")
        
        # Display top emitters
        display_top_emitters(before_metrics, top_n=10)
        
        # Calculate total emissions
        total_energy_before = sum(m[3] for m in before_metrics)
        total_carbon_before = sum(m[4] for m in before_metrics)
        
        print(f"\n📊 Total Energy (Before): {total_energy_before:.6f} J")
        print(f"🌍 Total Carbon (Before): {total_carbon_before:.6f} g CO2")
        
        # Step 2: Choose reduction strategy
        while True:
            display_menu()
            
            try:
                choice = input("\nEnter your choice (0-5): ").strip()
            except KeyboardInterrupt:
                print("\n\n👋 Exiting...")
                return
            
            if choice == '0':
                print("\n👋 Goodbye!")
                return
            
            elif choice == '1':
                strategy = 'pause'
                strategy_name = "PAUSE Processes"
                break
            
            elif choice == '2':
                strategy = 'renice'
                strategy_name = "LOWER PRIORITY"
                break
            
            elif choice == '3':
                strategy = 'limit'
                strategy_name = "LIMIT CPU"
                # Check if cpulimit is installed
                import subprocess
                try:
                    subprocess.run(['which', 'cpulimit'], check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    print("\n⚠️  cpulimit not installed!")
                    print("   Install with: sudo apt-get install cpulimit")
                    continue
                break
            
            elif choice == '4':
                strategy = 'kill'
                strategy_name = "TERMINATE Processes"
                print("\n⚠️  WARNING: This will kill processes!")
                confirm = input("   Are you sure? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    break
                else:
                    print("   Cancelled.")
                    continue
            
            elif choice == '5':
                print("\n📊 Skipping reduction strategy. Monitoring only.")
                strategy = None
                break
            
            else:
                print("\n❌ Invalid choice. Please try again.")
        
        # Step 3: Apply strategy
        affected_pids = []
        if strategy:
            print(f"\n🎯 Step 2: Applying '{strategy_name}' strategy...")
            
            try:
                num_targets = int(input("\n   How many top processes to target? (1-10): ").strip())
                num_targets = max(1, min(10, num_targets))
            except (ValueError, KeyboardInterrupt):
                num_targets = 5
                print(f"   Using default: {num_targets}")
            
            affected_pids = apply_strategy_to_top_emitters(before_metrics, strategy, num_targets)
            
            if not affected_pids:
                print("\n⚠️  No processes were affected. Exiting.")
                return
            
            print(f"\n✅ Successfully affected {len(affected_pids)} processes")
            
            # Wait for effects to take place
            wait_time = 5 if strategy == 'pause' else 10
            print(f"\n⏳ Waiting {wait_time} seconds for effects to take place...")
            time.sleep(wait_time)
        
        # Step 4: Collect AFTER metrics
        print("\n📊 Step 3: Collecting metrics after reduction...")
        print("   (Monitoring system for 3 seconds...)")
        time.sleep(3)
        
        after_metrics = collect_metrics()
        print(f"   ✅ Collected metrics for {len(after_metrics)} processes")
        
        # Step 5: Compare and display results
        comparison = EmissionComparison()
        comparison.record_before(before_metrics)
        comparison.record_after(after_metrics)
        
        comparison.display_comparison()
        
        # Step 6: Create visualization (optional)
        if MATPLOTLIB_AVAILABLE:
            print("\n📈 Step 4: Generating visualization...")
            create_comparison_chart(before_metrics, after_metrics, 'carbon_comparison.png')
        else:
            print("\n💡 Tip: Install matplotlib for visual charts:")
            print("   sudo apt-get install python3-matplotlib")
        
        # Step 7: Cleanup
        if strategy == 'pause' and affected_pids:
            print("\n🔄 Step 5: Cleanup...")
            cleanup_strategy(strategy, affected_pids)
        
        print("\n" + "="*70)
        print("✅ CARBON REDUCTION DEMONSTRATION COMPLETE")
        print("="*70)
        print("\n💡 Key Takeaways:")
        print("   • Real-time monitoring helps identify high-emission processes")
        print("   • Strategic reduction can significantly lower carbon footprint")
        print("   • Different strategies offer different trade-offs")
        print("\n🌱 Every joule saved contributes to a greener planet!")
        print("="*70 + "\n")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("   Cleaning up...")
        # Resume any paused processes
        if 'affected_pids' in locals() and 'strategy' in locals():
            if strategy == 'pause':
                cleanup_strategy(strategy, affected_pids)
        print("   ✅ Cleanup complete")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
