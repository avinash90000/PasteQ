# PasteQ

A lightweight and responsive clipboard manager for Linux, built using Python and GTK. Supports both text and image history, persistent sessions, and quick paste via `xdotool`.

---

## 🚀 Features

- 📄 Tracks clipboard history (text + images)
- 🖼️ Inline image previews
- 🔢 Limit history to 50 entries (configurable)
- ✂️ Remove items manually
- 📌 Always on top, hidden from Alt+Tab and Taskba
- 🧠 Remembers recent clipboard entries without duplicates

---

## 🛠 Requirements

### ✅ Python
- Python 3.7 or newer

### 📦 Python Dependencies

Install via pip:

```bash
pip install PyGObject
```
## 🧱 System Dependencies (Ubuntu/Debian)

Make sure these packages are installed on your system:

```bash
sudo apt update
sudo apt install -y \
  python3-gi \
  python3-gi-cairo \
  gir1.2-gtk-3.0 \
  gir1.2-gdkpixbuf-2.0 \
  xdotool
```
