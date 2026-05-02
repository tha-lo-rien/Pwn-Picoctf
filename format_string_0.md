# picoCTF 2024 – format string 0

**Category:** Binary Exploitation  
**Difficulty:** Easy  
**Author:** Cheng Zhang  
---

## Description

![Challenge Description](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/ef65139d409abf3f8fb8399926cd27c5537f7795/des.png)

> Can you use your knowledge of format strings to make the customers happy?

Challenge provides:
- **Binary**: `format-string-0`
- **Source code**: `format-string-0.c`
- **Server**: `nc mimas.picoctf.net 60222`

---

## Analysis

When connecting to the server, the program outputs:

![First connection](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/ef65139d409abf3f8fb8399926cd27c5537f7795/1.png)

Notice the burger names contain suspicious strings:
- `Breakf@st_Burger`
- `Gr%114d_Cheese` ← contains format specifier `%114d`
- `Bac0n_D3luxe`

This is a clear hint of a **Format String Vulnerability**: if user input is passed directly into `printf()` without a proper format string, specifiers like `%s`, `%p`, `%x` will be interpreted and executed by the C runtime.

---

## Exploitation

### Step 1: Use a long chain of `%s` specifiers

`%s` goes further than `%p`: instead of printing a raw address, it **dereferences** the stack value and prints the string stored at that address. By chaining many `%s` together, we force `printf` to keep popping values off the stack and dereferencing each one — eventually reaching the memory region where the flag is stored.

```
Enter your recommendation: %s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s
```

![Flag obtained](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/ef65139d409abf3f8fb8399926cd27c5537f7795/flag.png)

---

## Flag

```
picoCTF{7h3_cu570m3r_15_n3v3r_SEGFAULT_a1d85b3e}
```

---
