# BruteForge 🔥

**High-performance permutation-based wordlist generator**

BruteForge is a fast, flexible, and memory-efficient **command-line wordlist generator written in Python**.
It generates permutation-based wordlists from custom character sets and supports **Unicode**, **streaming output**, and **automatic file splitting** for large datasets.

Designed for **security researchers, developers, and educators**, BruteForge can generate extremely large wordlists without consuming excessive system memory.

---

# Badges

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey)
![Status](https://img.shields.io/badge/status-active-success)

---

# Features

* ⚡ **Fast permutation generation**
* 🔤 **Custom character sets**
* 🔠 Built-in character groups

  * lowercase letters
  * uppercase letters
  * digits
  * symbols
* 🌍 **Unicode support**
* 🧠 **Memory-efficient streaming generator**
* 📁 Output to **terminal or file**
* 📦 **Automatic file splitting**
* ⏩ Skip generated words
* 🎯 Limit total output count
* 🧾 Generation summary statistics

---

# Installation

## Clone the repository

```bash
git clone https://github.com/dhruva127/bruteforge.git
cd bruteforge
```

## Run the script

```bash
python bruteforge.py
```

or make it executable:

```bash
chmod +x bruteforge.py
./bruteforge.py
```

---

# Requirements

* Python **3.9 or newer**

All dependencies are part of the Python standard library:

* argparse
* itertools
* math
* string
* pathlib
* dataclasses

No external packages required.

---

# Quick Start

Generate permutations using characters **abc** with length **2**:

```bash
python bruteforge.py --chars abc --min-len 2 --max-len 2 --stdout
```

Output:

```
ab
ac
ba
bc
ca
cb
```

---

# Command Line Options

## Character Selection

| Option         | Description               |
| -------------- | ------------------------- |
| `--chars`      | Custom characters         |
| `--lower`      | Include lowercase letters |
| `--upper`      | Include uppercase letters |
| `--digits`     | Include digits            |
| `--symbols`    | Include default symbols   |
| `--symbol-set` | Custom symbol set         |

Example:

```bash
python bruteforge.py --lower --digits
```

---

## Length Options

| Option      | Description                   |
| ----------- | ----------------------------- |
| `--min-len` | Minimum generated word length |
| `--max-len` | Maximum generated word length |

Example:

```bash
--min-len 3 --max-len 6
```

---

## Output Options

| Option     | Description              |
| ---------- | ------------------------ |
| `--stdout` | Print output to terminal |
| `--output` | Save output to file      |

Example:

```bash
python bruteforge.py --lower --digits --output wordlist.txt
```

---

## Limiting Output

| Option    | Description                       |
| --------- | --------------------------------- |
| `--count` | Maximum number of generated words |
| `--start` | Skip first N generated words      |

Example:

```bash
--count 10000
```

---

## File Splitting

Large outputs can be automatically split.

```
--split-lines
```

Example:

```bash
python bruteforge.py --lower --digits --output words.txt --split-lines 100000
```

Generated files:

```
words_0001.txt
words_0002.txt
words_0003.txt
```

---

# Examples

## Simple permutations

```bash
python bruteforge.py --chars abc --min-len 2 --max-len 2 --stdout
```

---

## Generate passwords with letters and numbers

```bash
python bruteforge.py --lower --digits --min-len 4 --max-len 4 --output passwords.txt
```

---

## Generate complex wordlist

```bash
python bruteforge.py --lower --upper --digits --symbols --min-len 6 --max-len 6 --output list.txt
```

---

## Generate large dataset with splitting

```bash
python bruteforge.py --lower --digits --min-len 5 --max-len 5 --output data.txt --split-lines 500000
```

---

# How It Works

BruteForge generates **permutations** of characters.

Permutation means:

* order **matters**
* characters **cannot repeat** within a single word

Example:

Characters:

```
abc
```

Length:

```
2
```

Generated permutations:

```
ab
ac
ba
bc
ca
cb
```

The tool uses Python's **itertools.permutations()** and streams results using generators to maintain very low memory usage.

---

# Architecture

```
User Command
     │
     ▼
Argument Parser
     │
     ▼
Character Set Builder
     │
     ▼
Permutation Generator
     │
     ▼
Generator Stream
     │
     ▼
Output Engine
  │          │
  ▼          ▼
stdout      file writer
```

---

# Performance

BruteForge is optimized for **large wordlists**:

* uses **generators (`yield`)**
* does **not store results in memory**
* streams directly to output
* supports file splitting for huge datasets

This allows generation of **millions or billions of permutations** without exhausting system memory.



---

# License

MIT License

See the `LICENSE` file for details.

---

# Disclaimer

This tool is intended for **educational purposes, security research, and testing** only.

Do not use generated wordlists for unauthorized access or illegal activities.
