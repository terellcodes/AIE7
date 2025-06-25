# LLM Python Basics – Practice Notebook

This repository contains a Jupyter Notebook (`llm_python_basics_extended.ipynb`) designed to help students build foundational Python skills essential for working with Large Language Models (LLMs).

## 📘 What This Notebook Covers

The notebook includes practical examples and exercises on:

- Python syntax and variables
- Functions and loops
- String and list manipulations
- Working with dates (`datetime`)
- Parsing with regular expressions (`re`)
- Basic data analysis using `pandas`
- Plotting with `matplotlib`
- Writing and using simple classes

These topics are essential for understanding, cleaning, and preparing data — which is a core task when building and deploying LLMs or working on machine learning applications.

---

## 🚀 How to Set Up and Run

We use [`uv`](https://github.com/astral-sh/uv), a fast dependency manager for Python, to ensure consistent and quick setup across all environments.

### Step-by-Step:

1. **Install `uv`** (only once per machine):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone this repo** (or download the files to your machine).

3. **Create a virtual environment and install dependencies**:

   ```bash
   uv venv                # Create virtual environment (.venv/)
   source .venv/bin/activate  # Activate it (Windows: .venv\Scripts\activate)
   uv sync                # Install all required dependencies from pyproject.toml
   ```

4. **Launch Jupyter Notebook**:

   ```bash
   jupyter notebook llm_python_basics_extended.ipynb
   ```

---

## 📦 Why `uv sync`?

We use `uv sync` because:

- ✅ It’s **much faster** than pip
- 📌 It **installs exact versions** defined in `pyproject.toml`
- 🧪 It ensures **everyone has the same environment**, reducing bugs and confusion
- ♻️ It keeps setup clean and reproducible for teaching or grading

---

## 🙋 Need Help?

If you encounter any problems, feel free to:
- Check that your Python version is 3.8 or newer
- Ensure `uv` is properly installed (`uv --version`)
- Try running `jupyter notebook` after activating your `.venv`

Happy coding!
