# Chapter 4 Overview: The Process

## 1. The Central Problem

A computer may have only a small number of physical CPUs, but users expect it to run many programs at once.

The operating system solves this problem by **virtualizing the CPU**:

1. Run one process for a short time.
2. Stop it and save its state.
3. Run another process.
4. Continue switching among processes.

This technique is called **time sharing**. It creates the appearance that every running program has its own CPU. The cost is that each process may run more slowly because it shares the physical CPU with other processes.

The chapter's central question is:

> How can the operating system provide the illusion of many CPUs when the computer has only one or a few physical CPUs?

## 2. Program versus Process

A **program** and a **process** are related, but they are not the same thing.

- A **program** is stored code and static data, usually in an executable file on disk.
- A **process** is a program that is currently being executed.

A process includes everything needed to describe the program's current execution:

- Its instructions and data in memory
- Its CPU register values
- The address of its next instruction
- Its stack position
- Its open files
- Its current execution state

Therefore, the short definition is:

> A process is a running program.

Two processes can run the same program while still being separate processes. Each has its own execution state and normally its own address space.

## 3. The Machine State of a Process

If the OS stops a process and later wants to continue it correctly, it must preserve the process's **machine state**.

The important parts include:

### Address Space

The process's accessible memory contains:

- **Code**: the program's instructions
- **Static data**: global and static variables
- **Heap**: dynamically allocated memory
- **Stack**: function calls, local variables, parameters, and return addresses

### CPU Registers

Registers hold the values currently being used by the CPU. Two registers are especially important:

- **Program counter (PC)**: the address of the next instruction
- **Stack pointer**: the current position in the process's stack

### I/O Information

The OS also records information such as:

- Open files
- Current working directory
- Pending I/O operations

Together, these values describe where the process is and what it is doing.

## 4. How a Process Is Created

To turn a program into a running process, the OS performs several operations:

1. **Load code and static data** from the executable file into memory.
2. **Create a stack** and place initial information there, including program arguments.
3. **Create a heap**, initially small, for dynamically allocated data.
4. **Initialize I/O**, such as standard input, standard output, and standard error.
5. **Begin execution** at the program's entry point, eventually reaching `main()` in a C program.

Modern systems may load program data only when it is actually needed. This is called **lazy loading**.

## 5. The Process API

Operating systems provide operations for managing processes. The chapter introduces five general categories:

- **Create**: start a new process
- **Destroy**: force a process to stop
- **Wait**: wait for another process to finish
- **Miscellaneous control**: suspend or resume a process
- **Status**: obtain information about a process

Later chapters explain concrete UNIX system calls such as `fork()`, `exec()`, and `wait()`.

## 6. Process States

The chapter uses three main process states:

### Running

The process is currently executing instructions on a CPU.

### Ready

The process could run, but the OS has selected another process to use the CPU.

### Blocked

The process cannot continue until some event occurs. This commonly happens when it is waiting for I/O.

The main transitions are:

```text
Ready   --scheduled------> Running
Running --descheduled----> Ready
Running --starts I/O-----> Blocked
Blocked --I/O completes--> Ready
```

A blocked process does not need the CPU. The OS can run another ready process during that time, which keeps the CPU useful.

## 7. Mechanism versus Policy

The chapter introduces an important distinction.

### Mechanism: How Something Is Done

For example:

> How can the OS stop one process and start another?

The relevant mechanism is a **context switch**, which saves one process's register state and restores another process's register state.

### Policy: Which Choice Should Be Made

For example:

> Which ready process should run next?

A **scheduling policy** makes that decision.

Keeping mechanisms and policies separate allows the OS to change its decision-making rules without redesigning the low-level switching operations.

## 8. How the OS Records Processes

The OS maintains a **process list** containing information about the processes in the system.

Each process normally has an entry called a:

- **Process Control Block**, or **PCB**
- Sometimes a **process descriptor**

A PCB may contain:

- Process ID, or PID
- Current process state
- Saved register values
- Memory information
- Open files
- Parent-process information
- Whether the process has been terminated
- Information needed to resume execution

When the OS performs a context switch, it saves the outgoing process's CPU registers in its PCB and restores the incoming process's saved registers.

## 9. Additional Process States

Real operating systems use more states than the simplified running-ready-blocked model.

For example:

- A process may have an initial state while it is being created.
- A finished UNIX process may enter the **zombie** state.

A zombie has finished executing, but the OS temporarily keeps its exit information. Its parent can call `wait()` to read that information and allow the OS to remove the remaining process record.

## 10. The Chapter's Complete Idea

Chapter 4 establishes the basic structure for the following CPU-virtualization chapters:

```text
Program on disk
      |
      | OS creates and initializes it
      v
   Process
      |
      | CPU time sharing
      v
Running, Ready, or Blocked
      |
      | tracked using a PCB
      v
OS can stop and resume it correctly
```

The essential points to remember are:

1. A **process is a running program**.
2. Its current execution is described by memory, registers, and I/O information.
3. The OS uses **time sharing** to virtualize the CPU.
4. Processes move among **running**, **ready**, and **blocked** states.
5. The OS stores process information in a **PCB**.
6. **Mechanisms** implement operations; **policies** decide when and for whom to use them.

This chapter provides the concepts. The next chapters explain how process APIs, CPU control, context switching, and scheduling work in more detail.

Source: [OSTEP Chapter 4 — The Abstraction: The Process](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-intro.pdf)
