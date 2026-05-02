# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Chatbot

Activate the venv first, then run from the project root (required — `intents.json` and `source_data/` paths are relative):

```bash
.venv/Scripts/python.exe chatbot.py
```

To force model retraining, delete `model.h5` before running. The chatbot also accepts `/retrain` as a runtime command.

## Dependencies

Install into the venv:

```bash
pip install tensorflow==2.17.0 keras==3.4.1 mysql-connector-python==9.0.0 nltk==3.8.1 numpy==1.26.4 pandas==2.2.2
```

Download the required NLTK data once:

```bash
python -c "import nltk; nltk.download('punkt')"
```

## Architecture

The chatbot combines two data sources into one classification pipeline:

1. **`intents.json`** — hand-authored conversation patterns and responses (greetings, triage prompts, etc.). Preprocessed with Lancaster stemming + bag-of-words into a dense feature vector.
2. **MySQL / CSV fallback** — disease descriptions (`symptom_Description.csv`) and treatment precautions (`symptom_precaution.csv`) from Kaggle. The MySQL path is currently commented out; data loads from CSV files in `source_data/chatbot-symptom-description/`.

**Model (`model.h5`)** — a Keras Sequential network (Dense 128 → Dropout → Dense 64 → Dropout → Dense 32 → Softmax). Trained on `intents.json` patterns, saved to disk and reused on subsequent runs. Training runs 500 epochs.

**Confidence threshold** — predictions below 0.9 are rejected; the raw input is logged to `exceptions.txt` for review.

**Special chat commands** (entered at the `Patient:` prompt):
- `/bye` — exit
- `/retrain` — reload data and retrain model
- `/add_disease|<name>|<description>` — insert into MySQL and reload
- `/remove_disease|<name>` — delete from MySQL and reload

## Data Setup

**CSV mode (current default):** No setup needed beyond having `source_data/` present.

**MySQL mode:** Run the scripts in order from `sql_scripts/`:
1. `01_create_tables_chatbot.sql`
2. `02_all_table_insert.sql`

Then uncomment the MySQL blocks in `get_disease_data()` and `get_symptom_data()` and comment out the CSV fallback. Connection targets `localhost`, database `diagnosebot`.

A MongoDB version of all data exists in `mongodb/` but is not wired into the chatbot.

## Known Issues / In-Progress Work

- `TestChatBot.py` is a scratch/exploration file, not a runnable test suite — it contains disconnected code snippets and will error if run directly.
- `merged_model()` in `chatbot.py` exists but is commented out; it was intended to combine the intents model with the disease DB model.
- `create_db_model()` uses hardcoded placeholder labels and is not integrated into the main pipeline.
