# Chapter 5: Interlude — Process API

These notes cover the lesson and all 13 questions discussed in our study session. Explanations use plain English without analogies. Chinese clarifications appear only in the Q&A.

Source chapter: [OSTEP Chapter 5 — Interlude: Process API](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-api.pdf).

## 1. From a Process to the Process API

Chapter 4 introduced a process: a program being executed, together with its memory, register values, and other execution information.

Chapter 5 explains how programs request operations on processes. An **API**, or application programming interface, is a set of operations that programs can call. A **system call** requests a service from the operating system.

The central question is: how should the OS let programs create and control processes?

| Operation | Purpose | Creates a new process? |
|---|---|---|
| `fork()` | Create a child based on the calling process | Yes, if successful |
| `wait()` / `waitpid()` | Wait for a child and collect information about it | No |
| `exec()` family | Replace the program executing inside the calling process | No |

The name `exec()` refers to a family of functions, including `execvp()`. On systems such as Linux, these library functions use the underlying `execve()` system call.

## 2. `fork()`: Create a Child Process

Suppose a process executes:

```c
pid_t result = fork();
```

If the call succeeds, two processes continue from the return of `fork()`:

- The **parent** is the process that made the call.
- The **child** is the new process created by the call.

The child does not restart at `main()`. Both processes continue with the statements following `fork()`, but they receive different return values.

| Process or outcome | Value returned by `fork()` |
|---|---|
| Parent, on success | The child's PID, a positive integer |
| Child | `0` |
| Original process, on failure | `-1`; no child was created |

A **PID**, or process ID, identifies a process. The child has a different PID from its parent. Returning `0` in the child does not mean its PID is zero.

The return value allows different actions:

```c
if (result == 0) {
    // Child's actions.
} else if (result > 0) {
    // Parent's actions.
} else {
    // Handle failure to create a child.
}
```

The parent and child have separate private memory. An ordinary private variable initially equal to `7` has that value in both processes. If the child changes its copy to `12`, the parent's copy remains `7`. Explicitly shared memory is a separate case.

Some resources are still connected: inherited file descriptors can refer to the same underlying open file. Separate processes do not imply that every resource is independent.

After `fork()`, either process may execute first. Without an operation that establishes an order, we cannot assume which process prints first.

## 3. `wait()`: Wait for a Child

A parent can call:

```c
wait(NULL);
```

In our examples, the parent has one child. If that child is still executing, the parent normally blocks until the child terminates. The OS can run other processes during that wait.

If the child has already terminated and its exit information is available, the call can collect that information immediately without blocking.

Passing `NULL` means that the caller does not request the child's exit status. On success, `wait()` returns the PID of the child whose information it collected. `waitpid()` can select a particular child; its options can also request other behavior.

This connects directly to Chapter 4:

| State | Meaning |
|---|---|
| Running | Currently executing instructions |
| Ready | Can execute, but is waiting for CPU time |
| Blocked | Must wait for an event before continuing |

For an unfinished child, the usual sequence is:

```text
Parent calls wait(NULL)
    → Parent blocks
    → Child terminates
    → Parent becomes ready
    → OS schedules the parent
    → wait(NULL) returns
    → Parent continues after the call
```

Waiting also allows the OS to release the remaining record of a terminated child. Before that information is collected, a terminated child may remain as a **zombie**. It is no longer executing.

Our exercises assume successful calls and ordinary child termination. Real code must check return values: a wait can fail or be interrupted by a signal.

## 4. `exec()`: Execute a Different Program

Consider this call:

```c
char *args[] = {"ls", "-l", NULL};
execvp(args[0], args);
```

`execvp()` finds and executes `ls`, with `-l` as an argument. The final `NULL` marks the end of the argument array. The `p` variant searches the directories in `PATH` when the program name contains no slash.

A successful call replaces the program executing inside the current process. It replaces the old program's code and data and sets up memory for the new program, including its stack and heap. The process keeps its PID.

**A successful `exec()` never returns to the old program.** Execution begins in the new program. If `execvp()` fails, it returns `-1`, and the original program continues.

That makes this a useful error-handling pattern:

```c
execvp(args[0], args);

// Reached only if execvp() failed.
perror("execvp");
exit(1);
```

`perror()` prints an explanation of the error. `exit(1)` terminates the process with a failure status. This is a teaching fragment; a full program needs the appropriate headers and surrounding setup.

## 5. How a Shell Uses These Operations

A **shell** is a program that reads and executes commands. For a typical external command running in the foreground, a simplified sequence is:

1. The shell calls `fork()`.
2. The child configures any requested input and output.
3. The child calls an `exec()` function to execute the command.
4. The parent shell waits for that child.
5. When the wait returns successfully, the shell can display the next prompt.

Shell built-in commands and background commands can follow different paths. This sequence describes the external foreground commands used in our examples.

The parent shell must remain available for later commands. If it replaced itself with `ls`, the original shell program would no longer be running.

Separating `fork()` from `exec()` gives the child an opportunity to configure its environment before starting the requested program.

## 6. Input and Output Redirection

A **file descriptor** is a small integer a process uses to refer to an open input or output resource.

| Standard connection | Descriptor | Common default |
|---|---|---|
| Standard input (`stdin`) | `0` | Terminal input |
| Standard output (`stdout`) | `1` | Terminal output |
| Standard error (`stderr`) | `2` | Terminal output |

For this command:

```sh
ls -l > results.txt
```

The shell parses `>`. The child connects its standard output to `results.txt` before executing `ls`. Ordinary standard-output writes from `ls` then go to that file. Standard error remains separate unless it is also redirected.

After `fork()`, the child has its own file descriptor table. Changing the child's standard-output connection does not change the parent's connection. The relevant standard descriptors remain open across `exec()` unless explicitly configured to close on execution.

| Process | Standard output destination |
|---|---|
| Parent shell | Terminal |
| Child running `ls` | `results.txt` |

For input and output together:

```sh
wc -l < notes.txt > count.txt
```

The child connects descriptor `0` to `notes.txt` for reading and descriptor `1` to `count.txt` for writing before `exec()`. `wc -l` reads standard input, counts lines, and writes the count to standard output.

The filenames following `<` and `>` are handled by the shell as redirection instructions. In this example, they are not passed to `wc` as ordinary command-line arguments. The `>` operator creates the output file or truncates an existing one.

A **pipe** connects one process's output to another process's input, as in:

```sh
ls | wc -l
```

The shell creates the pipe and arranges the processes' file descriptors. Here, `wc -l` counts the lines it receives from `ls`.

## 7. Signals, Permissions, and Observation Tools

A **signal** is a notification delivered to a process. Depending on the signal and the process's configuration, it may cause termination, suspension, resumption, or execution of a signal handler.

In a typical interactive terminal:

| Action | Signal or effect |
|---|---|
| Ctrl+C | Sends `SIGINT` to the foreground process group; normally terminates it |
| Ctrl+Z | Sends `SIGTSTP` to the foreground process group; normally suspends it |
| Shell command `fg` | Brings a job to the foreground and resumes it if stopped |

Programs can handle or ignore `SIGINT` and `SIGTSTP`, so the listed effects are defaults.

A stopped process still exists and can resume. A terminated process has finished execution and cannot resume. Being stopped is also distinct from being blocked for an event such as I/O completion.

Permissions limit which processes a user can control. Generally, users can control their own processes; privileged users can have broader authority.

| Tool | Purpose |
|---|---|
| `ps` | List process information, including PIDs |
| `top` | Repeatedly display process and resource-use information |
| `kill` | Send a signal to a process |

Despite its name, `kill` does not always terminate a process. Its effect depends on the signal and how the process responds.

## 8. Study Questions and Model Answers

Unless a question says otherwise, assume calls succeed, the examples use a single thread per process, and the parent has only the child described. The output-order exercises assume ordinary program termination and successful output.

### Q1. One process successfully calls `fork()` once. Both processes then successfully call `exec()` once. How many processes remain, assuming neither exits?

**Model answer:** Two. `fork()` increases the count from one to two. Each `exec()` replaces the program inside an existing process without creating another process. Each process keeps its PID across its own `exec()`.

### Q2. Does this print `Finished!` if `execvp()` succeeds?

```c
execvp(args[0], args);
printf("Finished!\n");
```

**Model answer:** No. A successful `execvp()` replaces the current program and never returns to its next statement. If it fails, it returns `-1`, and the original program can execute the `printf()`.

### Q3. The parent calls `wait(NULL)` while its child is unfinished. Is the waiting parent running, ready, or blocked?

**Model answer:** Blocked. It must wait for the child to finish before this wait can complete normally. Receiving CPU time alone cannot satisfy that condition. The parent does not repeatedly check the child while consuming CPU time.

### Q4. Must the parent block if its child has already finished before `wait(NULL)` is called?

**Model answer:** No. If the child's exit information is still available, `wait(NULL)` collects it and returns immediately. The parent does not need to wait for a future termination event.

### Q5. Can `B` appear before `A` here, even if the OS runs the parent first?

```c
pid_t result = fork();

if (result == 0) {
    printf("A\n");
} else {
    wait(NULL);
    printf("B\n");
}
return 0;
```

**Model answer:** No. The child prints `A` and exits before the parent's successful wait returns. Only then does the parent print `B`. If the parent runs first, it reaches the wait and blocks.

The precise rule is that the parent continues **past the wait** after the child finishes. It does not mean that the parent cannot execute any instructions before the child.

中文澄清：`wait()` 约束的是父进程在该调用返回之后的执行。父进程仍然可能先获得 CPU，执行到 `wait()` 后再阻塞。

### Q6. Is `A` still guaranteed to appear before `B` if the parent prints before waiting?

```c
if (result == 0) {
    printf("A\n");
} else {
    printf("B\n");
    wait(NULL);
}
```

**Model answer:** No. Either order is possible. The parent prints `B` before calling `wait()`, so that wait cannot establish an order between these two prints. It only constrains what the parent does after the wait returns.

### Q7. Why should a child execute `ls` through `exec()`, rather than the parent shell itself?

**Model answer:** The parent shell needs to remain available for later commands. If it successfully executed `ls` through `exec()`, its shell program would be replaced. When `ls` finished, that process would exit. Using a child lets the parent wait and then display another prompt.

The parent resumes because its `wait()` returns, not because the child's `exec()` returns.

### Q8. For `ls > results.txt`, should the child configure output redirection before or after `exec()`?

**Model answer:** Before `exec()`. The child first connects standard output to `results.txt`, then executes `ls`. That standard-output connection survives the successful `exec()`. The old program cannot configure it afterward because a successful `exec()` never returns.

### Q9. Why configure redirection in the child rather than in the parent shell?

**Model answer:** The shell's own standard output should remain connected to the terminal so that later prompts appear there. Changing the child's file descriptor table leaves the parent's standard-output connection unchanged. The child writes to `results.txt` while the shell continues to use the terminal.

### Q10. Does the child's PID change after it successfully executes `ls` through `exec()`?

**Model answer:** No. The existing child process keeps its PID. Its executing program changes, but `exec()` does not create a new process.

### Q11. Has a process finished executing if it is suspended by Ctrl+Z?

**Model answer:** No. Assuming the default `SIGTSTP` action, it is stopped and still exists. It executes no instructions while stopped, but it can resume later, for example through the shell's `fg` command. Termination would end its execution permanently.

### Q12. If a process keeps the same PID, must it still be executing the same program?

**Model answer:** No. It can successfully call `exec()` to execute a different program while retaining its PID. A PID identifies the process, not the particular program it is executing. This question follows one existing process; PIDs can also be reused after a process is removed.

### Q13. What input/output changes should the child make between `fork()` and `exec()` for this command?

```sh
wc -l < notes.txt > count.txt
```

**Model answer:** Connect standard input, descriptor `0`, to `notes.txt` for reading, and standard output, descriptor `1`, to `count.txt` for writing. Then execute `wc` with `-l`. The new program reads the file contents through standard input and writes its line count through standard output.

中文澄清：不是把文件名传给 `stdin` 或 `stdout`，而是让它们分别连接到对应的文件。`<` 和 `>` 由 shell 解析；`wc` 通过已经配置好的标准输入和标准输出读写数据。

## 9. Further Reading

- [OSTEP Chapter 5 — Interlude: Process API](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-api.pdf)
- [Linux manual: fork(2)](https://man7.org/linux/man-pages/man2/fork.2.html)
- [Linux manual: wait(2)](https://man7.org/linux/man-pages/man2/wait.2.html)
- [Linux manual: exec(3)](https://man7.org/linux/man-pages/man3/exec.3.html)

The Linux manuals provide detailed return values and error conditions. These notes focus on the UNIX process behavior used in the chapter's examples.
