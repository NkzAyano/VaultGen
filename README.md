# 🔐 NKZ Password Vault

**A simple desktop password manager developed with Python.**

NKZ Password Vault is a local password management application designed to store and organize credentials using AES-256-GCM encryption.

## ✨ Features

- 🔐 Master password protection
- 🛡️ AES-256-GCM encryption
- 🔑 Password generator
- 📁 Credential categories
- 🔎 Search credentials
- ✏️ Edit and delete entries
- 📋 Copy passwords
- 👁️ Show and hide passwords
- 💾 Encrypted backup
- 🖥️ Windows desktop interface

## 🛠️ Technologies

- Python
- Tkinter
- Cryptography
- AES-256-GCM
- PBKDF2-HMAC-SHA256

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/NKZ-Password-Vault.git
```

Enter the project folder:

```bash
cd NKZ-Password-Vault
```

Install dependencies:

```bash
py -m pip install -r requirements.txt
```

Run the application:

```bash
py main.py
```

## 📂 Project Structure

```text
NKZ-Password-Vault/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

## 🔒 Security

- Credentials are encrypted locally.
- The vault uses AES-256-GCM.
- A master password derives the encryption key.
- The application does not require an online account.

**Important:** Losing the master password means losing access to the vault. Keep encrypted backups in a safe location.

This is an educational project and should receive further security testing before being used for critical credentials.

## 👨‍💻 Developer

**NKZ Cybersecurity**

GitHub: https://github.com/NkzAyano

## 📜

<img width="1052" height="707" alt="Captura de tela 2026-11-04 210657" src="https://github.com/user-attachments/assets/b970734e-afd2-4a86-b875-d6a08f6d6964" />
