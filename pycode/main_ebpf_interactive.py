#!/usr/bin/env python3
"""
🌍 Carbon Emission Monitor with eBPF - Interactive Edition
Real kernel-level monitoring with actual reduction strategies

REQUIRES: Native Linux with eBPF support and kernel headers
"""

import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')

import os
import time
import signal
from typing import List, Tuple

try:
    from bcc import BPF
except ImportError:
    print("❌ Error: BCC not available")
    print("Install with: sudo apt-get install python3-bpfcc bpfcc-tools")
    sys.exit(1)

from energy_calc import estimate_energy, estimate_carbon
from comparison import EmissionComparison, display_top_emitters
from reduction_strategies import apply_strategy_to_top_emitters, cleanup_strategy
from visualization import create_comparison_chart, MATPLOTLIB_AVAILABLE
import psutil


class eBPFCarbonMonitor:
    """eBPF-based carbon emission monitor"""
    
    def __init__(self):
        self.bpf_cpu = None
        self.bpf_net = None
        self.cpu_map = None
        self.net_map = None
        
    def load_ebpf_programs(self):
        """Load and attach eBPF programs"""
        print("\n📡 Loading eBPF programs...")
        
        try:
            # Load CPU monitor
            print("   Loading CPU monitor (eBPF/cpu_monitor.c)...")
            self.bpf_cpu = BPF(src_file="eBPF/cpu_monitor.c")
            self.cpu_map = self.bpf_cpu["cpu_usage"]
            print("   ✅ CPU monitor loaded")
            
            # Load Network monitor
            print("   Loading Network monitor (eBPF/net_monitor.c)...")
            self.bpf_net = BPF(src_file="eBPF/net_monitor.c")
            self.net_map = self.bpf_net["packet_count"]
            print("   ✅ Network monitor loaded")
            
            print("\n✅ All eBPF programs loaded successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Failed to load eBPF programs: {e}")
            print("\nPossible issues:")
            print("  • Kernel headers not installed")
            print("  • Not running on native Linux")
            print("  • BCC not properly configured")
            print("\nFor WSL2, use: python3 pycode/main_interactive.py")
            return False
    
    def collect_metrics(self) -> List[Tuple[int, int, int, float, float]]:
        """
        Collect metrics from eBPF maps
        Returns: List of (pid, cpu_time_ns, packets, energy, carbon)
        """
        metrics = []
        
        # Iterate through CPU usage map
        for k, v in self.cpu_map.items():
            pid = k.value
            cpu_time_ns = v.value
            
            # Get packet count for this PID
            try:
                packets_key = self.net_map.Key(pid)
                packets = self.net_map[packets_key].value
            except KeyError:
                packets = 0
            
            # Only include processes with significant activity
            if cpu_time_ns > 50_000_000:  # > 50ms
                energy = estimate_energy(cpu_time_ns, packets)
                carbon = estimate_carbon(energy)
                
                metrics.append((pid, cpu_time_ns, packets, energy, carbon))
        
        return metrics
    
    def cleanup(self):
        """Cleanup eBPF resources"""
        if self.bpf_cpu:
            self.bpf_cpu.cleanup()
        if self.bpf_net:
            self.bpf_net.cleanup()


def display_menu():
    """Display interactive menu"""
    print("\n" + "="*70)
    print("🌍 CARBON REDUCTION STRATEGIES (eBPF Mode)")
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
    """Main eBPF interactive program"""
    
    # Check if running as root
    if os.geteuid() != 0:
        print("\n❌ Error: eBPF requires root privileges")
        print("Usage: sudo python3 pycode/main_ebpf_interactive.py")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("🌍 CARBON EMISSION MONITOR (eBPF Edition)")
    print("="*70)
    print("\nKernel-level monitoring using eBPF for maximum accuracy.")
    print("This version applies REAL reduction strategies.")
    print("\nPress Ctrl+C at any time to exit safely.")
    print("="*70)
    
    # Initialize monitor
    monitor = eBPFCarbonMonitor()
    
    try:
        # Load eBPF programs
        if not monitor.load_ebpf_programs():
            return
        
        # Step 1: Collect BEFORE metrics
        print("\n📊 Step 1: Collecting baseline metrics...")
        print("   (Monitoring with eBPF for 5 seconds...)")
        
        # Let eBPF collect some data
        time.sleep(5)
        
        before_metrics = monitor.collect_metrics()
        
        if not before_metrics:
            print("\n⚠️  No significant process activity detected.")
            print("   Try running some applications and try again.")
            monitor.cleanup()
            return
        
        print(f"   ✅ Collected metrics for {len(before_metrics)} processes via eBPF")
        
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
                print("\n\n👋 Cleaning up...")
                monitor.cleanup()
                return
            
            if choice == '0':
                print("\n👋 Cleaning up and exiting...")
                monitor.cleanup()
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
                monitor.cleanup()
                return
            
            print(f"\n✅ Successfully affected {len(affected_pids)} processes")
            
            # Wait for effects to take place
            wait_time = 5 if strategy == 'pause' else 10
            print(f"\n⏳ Waiting {wait_time} seconds for strategy to take effect...")
            print("   (eBPF continues monitoring in the background...)")
            time.sleep(wait_time)
        
        # Step 4: Collect AFTER metrics
        print("\n📊 Step 3: Collecting metrics after reduction...")
        print("   (eBPF monitoring for 5 more seconds...)")
        time.sleep(5)
        
        after_metrics = monitor.collect_metrics()
        print(f"   ✅ Collected metrics for {len(after_metrics)} processes via eBPF")
        
        # Step 5: Compare and display results
        comparison = EmissionComparison()
        comparison.record_before(before_metrics)
        comparison.record_after(after_metrics)
        
        comparison.display_comparison()
        
        # Step 6: Create visualization (optional)
        if MATPLOTLIB_AVAILABLE:
            print("\n📈 Step 4: Generating visualization...")
            create_comparison_chart(before_metrics, after_metrics, 'carbon_comparison_ebpf.png')
        else:
            print("\n💡 Tip: Install matplotlib for visual charts:")
            print("   sudo apt-get install python3-matplotlib")
        
        # Step 7: Cleanup
        if strategy == 'pause' and affected_pids:
            print("\n🔄 Step 5: Cleanup...")
            cleanup_strategy(strategy, affected_pids)
        
        print("\n" + "="*70)
        print("✅ eBPF CARBON REDUCTION DEMONSTRATION COMPLETE")
        print("="*70)
        print("\n💡 Key Achievements:")
        print("   • Kernel-level monitoring with eBPF")
        print("   • Real-time carbon emission tracking")
        print("   • Actual reduction strategies applied")
        print("   • Measurable carbon savings demonstrated")
        print("\n🌱 eBPF enables accurate, low-overhead system monitoring!")
        print("="*70 + "\n")
        
        # Cleanup eBPF
        print("🧹 Cleaning up eBPF programs...")
        monitor.cleanup()
        print("✅ Done!\n")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("   Cleaning up...")
        # Resume any paused processes
        if 'affected_pids' in locals() and 'strategy' in locals():
            if strategy == 'pause':
                cleanup_strategy(strategy, affected_pids)
        # Cleanup eBPF
        monitor.cleanup()
        print("   ✅ Cleanup complete")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        monitor.cleanup()


if __name__ == "__main__":
    main()
