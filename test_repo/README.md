# *This project has been created as part of the 42 curriculum by <aberrami>*

# Codexion

## Description

Codexion is a multithreaded concurrency simulation inspired by the Dining Philosophers problem. The project models a set of coders competing for shared dongles in order to compile code while respecting strict timing and synchronization constraints.

Each coder is represented by a thread and requires two dongles to start compiling. Dongles are shared resources placed between neighboring coders in a circular topology. The simulation focuses on designing a fair, deadlock-free, and concurrent scheduling system capable of handling:

- atomic dual-resource acquisition,
- starvation prevention,
- cooldown constraints,
- precise burnout detection,
- concurrent execution of non-conflicting coders,
- serialized logging,
- scalable thread synchronization.

The project supports multiple scheduling policies, including FIFO and EDF (Earliest Deadline First).

---

# Features

- Multithreaded coder simulation using POSIX threads.
- FIFO and EDF scheduling modes.
- Atomic acquisition of two dongles.
- Concurrent compilation for non-conflicting coders.
- Deadlock prevention.
- Starvation mitigation.
- Cooldown management for dongles.
- Thread-safe logging system.
- Precise burnout monitoring.
- Lightweight local scheduling queues.
- Configurable simulation parameters.

---

# Instructions

## Requirements

- GCC / Clang
- POSIX threads (`pthread`)
- Linux or WSL environment
- Make

---

## Compilation

Run:

```bash
make
```

To clean object files:

```bash
make clean
```

To remove object files and executable:

```bash
make fclean
```

To rebuild the project:

```bash
make re
```

---

## Execution

```bash
./codexion number_of_coders time_to_burnout time_to_compile \
            time_to_debug time_to_refactor \
            compile_limit cooldown scheduler
```

### Parameters

| Argument | Description |
|---|---|
| `number_of_coders` | Number of coder threads |
| `time_to_burnout` | Maximum time without compiling before burnout |
| `time_to_compile` | Time spent compiling |
| `time_to_debug` | Time spent debugging |
| `time_to_refactor` | Time spent refactoring |
| `compile_limit` | Number of required compiles before stopping |
| `cooldown` | Dongle cooldown duration |
| `scheduler` | Scheduling policy (`fifo` or `edf`) |

---

## Example

```bash
./codexion 4 800 200 200 200 5 5 fifo
```

Example output:

```text
0 1 has taken left dongle
0 1 has taken right dongle
0 1 is compiling
0 3 has taken left dongle
0 3 has taken right dongle
0 3 is compiling
```

This demonstrates concurrent execution of non-conflicting coders.

---

# Architecture Overview

## Thread Model

The simulation contains:

- One thread per coder.
- One monitor thread responsible for burnout detection.

Each coder continuously performs:

1. Acquire two dongles.
2. Compile.
3. Release dongles.
4. Debug.
5. Refactor.

The monitor periodically checks all coders to determine whether a burnout condition occurred.

---

## Scheduling Strategy

The implementation uses lightweight local scheduling queues associated with each dongle.

Each dongle is shared by exactly two neighboring coders, therefore each dongle maintains a queue of size 2 representing alternating priority ownership.

A coder may compile only if:

- it owns both required dongles,
- both dongles are available,
- cooldown constraints are satisfied.

After compilation completes, ownership priority rotates locally between neighboring coders.

This approach allows:

- fairness,
- reduced contention,
- concurrent non-conflicting compilation,
- O(1) scheduling operations.

---

# Blocking Cases Handled

## Deadlock Prevention

The implementation prevents deadlocks by enforcing atomic dual-dongle acquisition.

A coder never partially acquires resources. Compilation begins only if both required dongles are simultaneously available.

This prevents circular wait situations and breaks the classical Coffman deadlock conditions.

Handled Coffman conditions:

| Condition | Handling |
|---|---|
| Mutual Exclusion | Required by project |
| Hold and Wait | Prevented through atomic acquisition |
| No Preemption | Controlled via scheduler ownership |
| Circular Wait | Prevented through synchronized arbitration |

---

## Starvation Prevention

Starvation is mitigated through alternating local ownership queues.

After each successful compile, dongle priority rotates between neighboring coders.

This ensures that:

- no coder can monopolize a dongle,
- waiting coders eventually gain ownership priority,
- fairness emerges naturally through local alternation.

EDF mode additionally prioritizes coders closest to burnout.

---

## Cooldown Handling

After a coder releases dongles, each dongle enters a cooldown phase.

The scheduler tracks:

```text
available_at timestamp
```

A dongle may only be reused once its cooldown period expires.

This prevents immediate reacquisition and introduces additional scheduling pressure.

---

## Precise Burnout Detection

A dedicated monitor thread continuously checks:

```text
current_time - last_compile_time
```

If the value exceeds `time_to_burnout`, the coder is declared burned out and the simulation stops safely.

The monitor uses synchronized access to shared state to avoid race conditions.

---

## Log Serialization

Console output is protected by a dedicated mutex.

This guarantees:

- non-interleaved logs,
- deterministic output formatting,
- thread-safe printing.

Without log serialization, simultaneous `printf` calls from multiple threads could corrupt output.

---

# Thread Synchronization Mechanisms

## pthread_mutex_t

Mutexes are used extensively to protect shared resources.

### Scheduler Mutex

Coordinates access to:

- dongle ownership,
- cooldown timestamps,
- queue rotations,
- shared scheduling state.

This guarantees atomic dual-dongle acquisition.

Example:

```c
pthread_mutex_lock(&sim->scheduler_mutex);
/* shared scheduling logic */
pthread_mutex_unlock(&sim->scheduler_mutex);
```

---

### Print Mutex

Protects console output:

```c
pthread_mutex_lock(&sim->print_mutex);
printf(...);
pthread_mutex_unlock(&sim->print_mutex);
```

This prevents race conditions during logging.

---

### Stop Mutex

Protects simulation termination state.

Ensures that:

- burnout detection,
- simulation shutdown,
- monitor termination

occur safely across threads.

---

## pthread_cond_t

Condition variables are used to notify waiting coders when scheduling conditions change.

Typical wake-up events include:

- dongle release,
- cooldown expiration,
- queue ownership changes.

Condition variables reduce unnecessary busy waiting and improve scheduler responsiveness.

---

## Atomic Resource Coordination

The implementation guarantees that a coder only acquires dongles when both are simultaneously available.

This avoids:

- partial acquisition,
- inconsistent shared state,
- circular waits,
- deadlocks.

The scheduler mutex protects the entire decision process atomically.

---

## Race Condition Prevention

Shared variables protected by synchronization primitives include:

- dongle ownership state,
- queue ownership positions,
- cooldown timestamps,
- burnout timestamps,
- simulation stop flag,
- log output.

Without synchronization, simultaneous thread access could lead to:

- corrupted scheduling state,
- invalid ownership,
- inconsistent burnout detection,
- undefined behavior.

---

# Performance Considerations

The implementation was designed to:

- maximize concurrency,
- minimize scheduler contention,
- support simultaneous non-conflicting compilation,
- reduce scheduling complexity.

The local queue architecture avoids:

- large global queues,
- expensive heap operations,
- unnecessary global serialization.

The resulting scheduler scales efficiently while maintaining fairness.

---

# Resources

## References

### POSIX Threads

- https://man7.org/linux/man-pages/man7/pthreads.7.html
- https://pubs.opengroup.org/onlinepubs/9699919799/functions/pthread_create.html
- https://www.youtube.com/watch?v=d9s_d28yJq0&list=PLfqABt5AS4FmuQf70psXrsMLEDQXNkLq2

### Dining Philosophers Problem

- https://en.wikipedia.org/wiki/Dining_philosophers_problem
- https://www.cs.cmu.edu/afs/cs/academic/class/15492-f07/www/pthreads.html

### Timing and Thread Scheduling

- https://man7.org/linux/man-pages/man2/usleep.2.html
- https://man7.org/linux/man-pages/man2/clock_gettime.2.html

---

## AI Usage

AI tools were used during the development process for:

- brainstorming synchronization strategies,
- discussing deadlock prevention techniques,
- analyzing starvation scenarios,
- validating scheduler architectures,
- reviewing concurrency edge cases,
- improving README structure and technical explanations.

AI assistance was used as a learning and review tool only.

The implementation design decisions, debugging, testing, synchronization logic, and final architecture integration were performed manually.

---

# Known Limitations

- Extremely aggressive timing configurations may still produce burnout due to OS scheduling jitter.
- Thread scheduling precision depends on the operating system and hardware.
- WSL environments may introduce additional timing variability compared to native Linux.

---

# License

This project was created for educational purposes as part of the 42 curriculum.

