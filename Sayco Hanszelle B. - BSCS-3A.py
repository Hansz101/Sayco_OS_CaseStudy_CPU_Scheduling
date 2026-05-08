# ============================================================
# CPU Scheduling Simulation Program
# Implements: FCFS, SJF (Non-Preemptive), SRT (Preemptive),
#             Round Robin, Priority (Non-Preemptive),
#             and Priority with Round Robin
# ============================================================


# -------------------------------------------------------
# Process Class
# Represents a single process with all scheduling attributes.
# Each instance stores the process ID, arrival time, burst time,
# remaining time (used in preemptive algorithms), priority,
# and computed metrics: waiting time (WT), turnaround time (TAT),
# and finish time.
# -------------------------------------------------------
class Process:
    def __init__(self, pid, arrival, burst, priority=0):
        self.pid = pid              # Unique process identifier (e.g., P1, P2)
        self.arrival = arrival      # Time at which the process arrives in the ready queue
        self.burst = burst          # Total CPU time required by the process
        self.rem = burst            # Remaining burst time; used for preemptive scheduling
        self.priority = priority    # Priority value (lower integer = higher priority)
        self.wt = 0                 # Waiting Time: time spent waiting in the ready queue
        self.tat = 0                # Turnaround Time: total time from arrival to completion
        self.finish_time = 0        # The clock time when the process finishes execution


# -------------------------------------------------------
# safe_int_input()
# Prevents the program from crashing when the user enters
# invalid input such as letters or negative numbers.
# min_value allows enforcing minimum accepted values.
# -------------------------------------------------------
def safe_int_input(prompt, min_value=None):
    while True:
        try:
            value = int(input(prompt))

            if min_value is not None and value < min_value:
                print(f"Please enter a number greater than or equal to {min_value}.")
                continue

            return value

        except ValueError:
            print("Invalid input. Please enter a valid integer.")


# -------------------------------------------------------
# reset_processes()
# Resets computed values before running another algorithm.
# Prevents leftover values from previous simulations from
# affecting the next scheduling run.
# -------------------------------------------------------
def reset_processes(processes):
    for p in processes:
        p.rem = p.burst
        p.wt = 0
        p.tat = 0
        p.finish_time = 0


# -------------------------------------------------------
# print_metrics()
# Displays a formatted table of per-process WT and TAT,
# then prints the average WT and average TAT across all
# processes. Called at the end of every scheduling function.
# Includes protection against division by zero.
# -------------------------------------------------------
def print_metrics(processes):

    # Prevent division-by-zero errors if process list is empty
    if not processes:
        print("No processes to display.")
        return

    total_wt, total_tat = 0, 0

    print("\n-------------------------------------------")
    print("PID\tWT\tTAT")

    for p in processes:
        print(f"{p.pid}\t{p.wt}\t{p.tat}")
        total_wt += p.wt
        total_tat += p.tat

    # Compute and display averages
    print(f"\nAverage WT: {total_wt/len(processes):.2f}")
    print(f"Average TAT: {total_tat/len(processes):.2f}")
    print("-------------------------------------------\n")


# -------------------------------------------------------
# fcfs()
# First-Come, First-Served (Non-Preemptive)
# Processes are sorted by arrival time and executed in that
# order without interruption. If the CPU is idle when the
# next process arrives, time is advanced to its arrival.
# Simple but can cause the "convoy effect" where short
# processes wait behind long ones.
# -------------------------------------------------------
def fcfs(processes):

    # Reset process values before simulation
    reset_processes(processes)

    print("\n=== FCFS Scheduling ===")

    # Sort by arrival time so the earliest-arriving process runs first
    processes.sort(key=lambda x: x.arrival)

    time = 0
    gantt = []

    for p in processes:

        # If CPU is idle before this process arrives, fast-forward the clock
        if time < p.arrival:
            time = p.arrival

        start = time

        # Process runs to completion without preemption
        time += p.burst

        p.finish_time = time
        p.tat = p.finish_time - p.arrival   # TAT = Finish Time - Arrival Time
        p.wt = p.tat - p.burst              # WT  = TAT - Burst Time

        gantt.append(f"| {p.pid} ({start}-{time}) ")

    print("Gantt Chart:", "".join(gantt) + "|")
    print_metrics(processes)


# -------------------------------------------------------
# sjf_non_preemptive()
# Shortest Job First – Non-Preemptive
# At each scheduling decision point, the process with the
# smallest burst time among those already arrived is chosen.
# Once selected, it runs to completion. Minimizes average
# waiting time but may cause starvation for longer processes.
# -------------------------------------------------------
def sjf_non_preemptive(processes):

    # Reset process values before simulation
    reset_processes(processes)

    print("\n=== SJF (Non-Preemptive) ===")

    processes.sort(key=lambda x: x.arrival)

    time = 0
    completed = 0
    n = len(processes)

    gantt = []

    while completed != n:

        # Build the list of processes that have arrived and are not yet completed
        available = [
            p for p in processes
            if p.arrival <= time and p.finish_time == 0
        ]

        # If no process is ready, advance the clock by one unit
        if not available:
            time += 1
            continue

        # Select the process with the shortest burst time
        available.sort(key=lambda x: x.burst)

        p = available[0]

        start = time

        # Execute the chosen process to completion
        time += p.burst

        p.finish_time = time
        p.tat = p.finish_time - p.arrival
        p.wt = p.tat - p.burst

        completed += 1

        gantt.append(f"| {p.pid} ({start}-{time}) ")

    print("Gantt Chart:", "".join(gantt) + "|")
    print_metrics(processes)


# -------------------------------------------------------
# srt_preemptive()
# Shortest Remaining Time – Preemptive (Preemptive SJF)
# At every clock tick the process with the smallest remaining
# burst time is selected. If a new process arrives with a
# shorter remaining time than the current one, it preempts it.
# Provides optimal average waiting time but causes frequent
# context switches and can starve longer processes.
# -------------------------------------------------------
def srt_preemptive(processes):

    # Reset process values before simulation
    reset_processes(processes)

    print("\n=== Shortest Remaining Time (Preemptive) ===")

    processes.sort(key=lambda x: x.arrival)

    time = 0
    completed = 0
    n = len(processes)

    gantt = []

    last_pid = None
    start_time = 0

    while completed != n:

        # Get all arrived processes that still have remaining burst time
        available = [
            p for p in processes
            if p.arrival <= time and p.rem > 0
        ]

        # No process ready: record the gap in Gantt and advance clock
        if not available:

            if last_pid is not None:
                gantt.append(f"| {last_pid} ({start_time}-{time}) ")
                last_pid = None

            time += 1
            continue

        # Select the process with the least remaining time
        available.sort(key=lambda x: x.rem)

        p = available[0]

        # If a different process is now running, close previous Gantt segment
        if last_pid != p.pid:

            if last_pid is not None:
                gantt.append(f"| {last_pid} ({start_time}-{time}) ")

            last_pid = p.pid
            start_time = time

        # Execute for one time unit
        p.rem -= 1
        time += 1

        # Check if process completed
        if p.rem == 0:
            p.finish_time = time
            p.tat = p.finish_time - p.arrival
            p.wt = p.tat - p.burst

            completed += 1

    # Append final Gantt segment
    if last_pid is not None:
        gantt.append(f"| {last_pid} ({start_time}-{time}) ")

    print("Gantt Chart:", "".join(gantt) + "|")
    print_metrics(processes)


# -------------------------------------------------------
# round_robin()
# Round Robin Scheduling (Preemptive)
# Each process is given a fixed time slice called the
# Time Quantum (TQ). If a process does not finish within
# its quantum, it is placed at the back of the ready queue.
# Ensures fairness and good response time for all processes,
# but higher TQ values approach FCFS behaviour.
# -------------------------------------------------------
def round_robin(processes, tq):

    # Reset process values before simulation
    reset_processes(processes)

    print(f"\n=== Round Robin (TQ={tq}) ===")

    time = 0
    queue = []
    completed = 0
    n = len(processes)

    gantt = []

    processes.sort(key=lambda x: x.arrival)

    i = 0

    # Enqueue the first process to kick off simulation
    if processes:
        queue.append(processes[i])
        i += 1

    while completed != n:

        # If queue is empty, advance time
        if not queue:

            time += 1

            while i < n and processes[i].arrival <= time:
                queue.append(processes[i])
                i += 1

            continue

        # Dequeue front process
        p = queue.pop(0)

        start = time

        # Run process for min(rem, tq)
        run_time = min(p.rem, tq)

        time += run_time
        p.rem -= run_time

        gantt.append(f"| {p.pid} ({start}-{time}) ")

        # Add newly arrived processes
        while i < n and processes[i].arrival <= time:
            queue.append(processes[i])
            i += 1

        if p.rem > 0:

            # Process unfinished, place back in queue
            queue.append(p)

        else:

            # Process completed
            p.finish_time = time
            p.tat = p.finish_time - p.arrival
            p.wt = p.tat - p.burst

            completed += 1

    print("Gantt Chart:", "".join(gantt) + "|")
    print_metrics(processes)


# -------------------------------------------------------
# priority_non_preemptive()
# Priority Scheduling – Non-Preemptive
# Among all ready processes, the one with the highest priority
# (lowest integer value) is selected and runs to completion.
# No preemption occurs once a process starts. Can cause
# starvation for low-priority processes if high-priority
# processes keep arriving.
# -------------------------------------------------------
def priority_non_preemptive(processes):

    # Reset process values before simulation
    reset_processes(processes)

    print("\n=== Priority Scheduling (Non-Preemptive) ===")

    processes.sort(key=lambda x: x.arrival)

    time = 0
    completed = 0
    n = len(processes)

    gantt = []

    while completed != n:

        # Collect all arrived and unfinished processes
        available = [
            p for p in processes
            if p.arrival <= time and p.finish_time == 0
        ]

        # Advance clock if no process is ready
        if not available:
            time += 1
            continue

        # Select process with highest priority
        available.sort(key=lambda x: x.priority)

        p = available[0]

        start = time

        # Run to completion
        time += p.burst

        p.finish_time = time
        p.tat = p.finish_time - p.arrival
        p.wt = p.tat - p.burst

        completed += 1

        gantt.append(f"| {p.pid} ({start}-{time}) ")

    print("Gantt Chart:", "".join(gantt) + "|")
    print_metrics(processes)


# -------------------------------------------------------
# priority_with_rr()
# Priority Scheduling with Round Robin (Preemptive via TQ)
# Processes of the same highest priority level share the CPU
# using Round Robin with the given Time Quantum. Higher-priority
# processes still preempt lower-priority ones at scheduling
# points, combining fairness within priority groups with
# strict priority ordering between groups.
# -------------------------------------------------------
def priority_with_rr(processes, tq):

    # Reset process values before simulation
    reset_processes(processes)

    print(f"\n=== Priority Scheduling with RR (TQ={tq}) ===")

    processes.sort(key=lambda x: x.arrival)

    time = 0
    completed = 0
    n = len(processes)

    gantt = []

    queue = []

    i = 0

    while completed != n:

        # Add arrived processes to queue
        while i < n and processes[i].arrival <= time:
            queue.append(processes[i])
            i += 1

        # If queue empty, advance time
        if not queue:
            time += 1
            continue

        # Find highest priority level
        highest_pri = min(p.priority for p in queue)

        # Collect processes with highest priority
        candidates = [
            p for p in queue
            if p.priority == highest_pri
        ]

        # Pick first candidate
        p = candidates[0]

        queue.remove(p)

        start = time

        # Run process for min(rem, tq)
        run_time = min(p.rem, tq)

        time += run_time
        p.rem -= run_time

        gantt.append(f"| {p.pid} ({start}-{time}) ")

        # Add newly arrived processes
        while i < n and processes[i].arrival <= time:
            queue.append(processes[i])
            i += 1

        if p.rem > 0:

            # Requeue unfinished process
            queue.append(p)

        else:

            # Process completed
            p.finish_time = time
            p.tat = p.finish_time - p.arrival
            p.wt = p.tat - p.burst

            completed += 1

    print("Gantt Chart:", "".join(gantt) + "|")
    print_metrics(processes)


# -------------------------------------------------------
# main()
# Entry point and interactive menu loop.
# Repeatedly prompts the user to select a scheduling algorithm,
# collects process parameters (arrival time, burst time, and
# optionally priority), and dispatches to the appropriate
# scheduling function. The loop exits when the user selects 7.
# Includes input validation to prevent runtime crashes.
# -------------------------------------------------------
def main():

    while True:

        print("\n--- CPU Scheduling Simulator ---")
        print("1. FCFS")
        print("2. SJF (Non-Preemptive)")
        print("3. SRT (Preemptive SJF)")
        print("4. Round Robin")
        print("5. Priority (Non-Preemptive)")
        print("6. Priority with Round Robin")
        print("7. Exit")

        choice = input("Select an algorithm (1-7): ").strip()

        # Validate menu selection
        if choice not in ['1', '2', '3', '4', '5', '6', '7']:
            print("Invalid choice. Please select from 1 to 7.")
            continue

        # Exit condition
        if choice == '7':
            print("Exiting program...")
            break

        # Collect process count safely
        n = safe_int_input(
            "Enter number of processes: ",
            min_value=1
        )

        processes = []

        # Collect process data
        for i in range(n):

            pid = f"P{i+1}"

            print(f"\n--- Enter details for {pid} ---")

            arr = safe_int_input(
                f"Enter Arrival Time for {pid}: ",
                min_value=0
            )

            burst = safe_int_input(
                f"Enter Burst Time for {pid}: ",
                min_value=1
            )

            pri = 0

            # Priority only needed for Priority algorithms
            if choice in ['5', '6']:

                pri = safe_int_input(
                    f"Enter Priority for {pid} (lower = higher priority): ",
                    min_value=0
                )

            processes.append(Process(pid, arr, burst, pri))

        # Dispatch selected scheduling algorithm
        if choice == '1':

            fcfs(processes)

        elif choice == '2':

            sjf_non_preemptive(processes)

        elif choice == '3':

            srt_preemptive(processes)

        elif choice == '4':

            tq = safe_int_input(
                "Enter Time Quantum: ",
                min_value=1
            )

            round_robin(processes, tq)

        elif choice == '5':

            priority_non_preemptive(processes)

        elif choice == '6':

            tq = safe_int_input(
                "Enter Time Quantum: ",
                min_value=1
            )

            priority_with_rr(processes, tq)


# -------------------------------------------------------
# Standard Python entry point guard
# -------------------------------------------------------
if __name__ == "__main__":
    main()