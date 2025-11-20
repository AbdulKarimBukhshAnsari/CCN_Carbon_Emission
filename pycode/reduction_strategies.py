#!/usr/bin/env python3
"""
Carbon Reduction Strategies Module
Implements real strategies to reduce carbon emissions from processes
"""

import os
import signal
import subprocess
import psutil
import time
from typing import List, Tuple

class CarbonReducer:
    """Implements various strategies to reduce carbon emissions"""
    
    def __init__(self):
        self.paused_pids = []
        self.limited_pids = []
        self.reniced_pids = []
        
    def pause_process(self, pid: int) -> bool:
        """
        Pause a process using SIGSTOP
        Returns True if successful
        """
        try:
            os.kill(pid, signal.SIGSTOP)
            self.paused_pids.append(pid)
            return True
        except (ProcessLookupError, PermissionError) as e:
            print(f"  ⚠️  Cannot pause PID {pid}: {e}")
            return False
    
    def resume_process(self, pid: int) -> bool:
        """
        Resume a paused process using SIGCONT
        Returns True if successful
        """
        try:
            os.kill(pid, signal.SIGCONT)
            if pid in self.paused_pids:
                self.paused_pids.remove(pid)
            return True
        except (ProcessLookupError, PermissionError) as e:
            print(f"  ⚠️  Cannot resume PID {pid}: {e}")
            return False
    
    def resume_all(self):
        """Resume all paused processes"""
        for pid in self.paused_pids[:]:
            self.resume_process(pid)
    
    def lower_priority(self, pid: int, niceness: int = 10) -> bool:
        """
        Lower process priority using renice
        niceness: 0-19 (higher = lower priority)
        Returns True if successful
        """
        try:
            subprocess.run(
                ['renice', '-n', str(niceness), '-p', str(pid)],
                check=True,
                capture_output=True
            )
            self.reniced_pids.append((pid, niceness))
            return True
        except (subprocess.CalledProcessError, PermissionError) as e:
            print(f"  ⚠️  Cannot renice PID {pid}: {e}")
            return False
    
    def limit_cpu(self, pid: int, limit_percent: int = 50) -> bool:
        """
        Limit CPU usage of a process using cpulimit
        limit_percent: CPU usage limit (e.g., 50 = 50%)
        Returns True if successful
        """
        try:
            # Check if cpulimit is installed
            subprocess.run(['which', 'cpulimit'], check=True, capture_output=True)
            
            # Start cpulimit in background
            subprocess.Popen(
                ['cpulimit', '-p', str(pid), '-l', str(limit_percent), '-b'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.limited_pids.append(pid)
            return True
        except subprocess.CalledProcessError:
            print(f"  ⚠️  cpulimit not installed. Install with: sudo apt-get install cpulimit")
            return False
        except Exception as e:
            print(f"  ⚠️  Cannot limit PID {pid}: {e}")
            return False
    
    def kill_process(self, pid: int) -> bool:
        """
        Terminate a process (use with caution!)
        Returns True if successful
        """
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
            
            # Safety check - don't kill critical processes
            critical_processes = ['systemd', 'init', 'ssh', 'sshd']
            if proc_name in critical_processes:
                print(f"  ⛔ Cannot kill critical process: {proc_name}")
                return False
            
            proc.terminate()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, PermissionError) as e:
            print(f"  ⚠️  Cannot kill PID {pid}: {e}")
            return False
    
    def get_process_info(self, pid: int) -> dict:
        """Get process information"""
        try:
            proc = psutil.Process(pid)
            return {
                'name': proc.name(),
                'status': proc.status(),
                'cpu_percent': proc.cpu_percent(interval=0.1),
                'num_threads': proc.num_threads()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None


def apply_strategy_to_top_emitters(
    metrics: List[Tuple[int, int, int, float, float]], 
    strategy: str, 
    top_n: int = 5
) -> List[int]:
    """
    Apply reduction strategy to top N carbon emitters
    
    Args:
        metrics: List of (pid, cpu_time_ns, packets, energy, carbon)
        strategy: 'pause', 'renice', 'limit', or 'kill'
        top_n: Number of top processes to target
    
    Returns:
        List of affected PIDs
    """
    reducer = CarbonReducer()
    affected_pids = []
    
    # Sort by carbon emissions (highest first)
    sorted_metrics = sorted(metrics, key=lambda x: x[4], reverse=True)
    
    print(f"\n🎯 Applying '{strategy}' strategy to top {top_n} emitters...")
    
    for i, (pid, cpu_time_ns, packets, energy, carbon) in enumerate(sorted_metrics[:top_n]):
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
            
            print(f"\n  Process {i+1}: PID {pid} ({proc_name})")
            print(f"    Energy: {energy:.6f} J, Carbon: {carbon:.6f} g CO2")
            
            success = False
            if strategy == 'pause':
                print(f"    Action: Pausing process...")
                success = reducer.pause_process(pid)
            elif strategy == 'renice':
                print(f"    Action: Lowering priority (nice +10)...")
                success = reducer.lower_priority(pid, 10)
            elif strategy == 'limit':
                print(f"    Action: Limiting CPU to 30%...")
                success = reducer.limit_cpu(pid, 30)
            elif strategy == 'kill':
                print(f"    Action: Terminating process...")
                success = reducer.kill_process(pid)
            
            if success:
                print(f"    ✅ Success!")
                affected_pids.append(pid)
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            print(f"    ⚠️  Process no longer accessible")
            continue
    
    return affected_pids


def cleanup_strategy(strategy: str, affected_pids: List[int]):
    """
    Cleanup after applying strategy (resume paused processes, etc.)
    """
    reducer = CarbonReducer()
    
    if strategy == 'pause':
        print("\n🔄 Resuming paused processes...")
        for pid in affected_pids:
            reducer.resume_process(pid)
        print("  ✅ All processes resumed")
