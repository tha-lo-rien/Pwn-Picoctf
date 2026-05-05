# picoCTF 2024 – format string 1

**Category:** Binary Exploitation  
**Difficulty:** Medium  
**Author:** SYREAL  

---

## Description

![Challenge Description](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/b4e80841f3e1e43dd7e3825091d882a21b8d479c/des.png)

> Patrick and Sponge Bob were really happy with those orders you made for them, but now they're curious about the secret menu. Find it, and along the way, maybe you'll find something else of interest!

Challenge provides:
- **Binary**: `format-string-1`
- **Source code**: `format-string-1.c`
- **Server**: `nc mimas.picoctf.net 63418`

---

## Analysis

Download the binary and source code using `wget`, then make it executable:

![Download files](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/b4e80841f3e1e43dd7e3825091d882a21b8d479c/local.png)

Before anything else, let's see what we're actually dealing with:

![File check](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/b4e80841f3e1e43dd7e3825091d882a21b8d479c/check.png)

ELF 64-bit, dynamically linked, not stripped — a standard Linux x86-64 binary with nothing hidden.

Connect to the server and see how the program behaves:

![First connection](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/b4e80841f3e1e43dd7e3825091d882a21b8d479c/run.png)

It takes an input and echoes it right back. The challenge name already gives it away — let's throw a chain of `%p` at it and see if the program interprets the format specifiers:

![Sending %p](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/b4e80841f3e1e43dd7e3825091d882a21b8d479c/try.png)

Instead of printing `%p%p%p...` literally, the server spits out a long list of hex addresses. This confirms a **Format String Vulnerability** — `printf` is treating our input directly as a format string, and each `%p` pops a value right off the stack.

Looking closer at the output, some values in there look suspiciously familiar:

![Leaked stack](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/b4e80841f3e1e43dd7e3825091d882a21b8d479c/ex.png)

Values like `0x7b4654436f636970`, `0x355f31346d316e34`... are way too large to be typical addresses — they look like ASCII. Since x86-64 stores data in **little-endian**, we just need to reverse the bytes and decode:

![Decoding hex](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/b4e80841f3e1e43dd7e3825091d882a21b8d479c/AI.png)

```
0x7b4654436f636970  →  picoCTF{
0x355f31346d316e34  →  4n1m4_5
0x3478345f33317937  →  7y13_4x4
0x31395f673431665f  →  _f14g_91
0x7d653464663533    →  35fd4e}
```

The flag was sitting right on the stack the whole time, fully leaked through the format string. Now let's look at the source to understand exactly why:

![Source code](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/b4e80841f3e1e43dd7e3825091d882a21b8d479c/source.png)

The program declares `buf`, `secret1`, `flag`, `secret2` as adjacent stack variables, reads `flag.txt` into `flag`, then calls `printf(buf)` instead of `printf("%s", buf)` — a single careless line that exposes the entire stack.

---

## Exploitation

Send a long chain of `%p` to the server, scan the output for ASCII-looking values, reverse the bytes to account for little-endian, and concatenate the decoded pieces to get the flag.

---

## Flag

```
picoCTF{4n1m4_5_7y13_4x4_f14g_9135fd4e}
```

---
