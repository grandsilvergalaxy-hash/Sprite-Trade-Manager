# Sprite Trade Manager

A Python-based Fortnite Sprite collection tracker and text-based trade advertisement generator.

Sprite Trade Manager helps players keep track of their owned Sprite variants, monitor mastery progress, and automatically generate organized trade advertisements.

## Features

- **Collection Tracking** – Keep track of which Sprite variants you own.
- **Variant Management** – Track individual variants, including Base, Fortune, and Cursed.
- **Mastery Tracking** – Mark owned variants as Unmastered, Mastered, or Level 5.
- **Automatic Trade Advertisements** – Generate organized trade listings using three categories:
  - **LF (Looking For):** Variants you don't own.
  - **UNMASTERED:** Variants you own but haven't mastered.
  - **FT (For Trade):** Mastered variants available for trade.
- **Level 5 Identification** – Highlight Level 5 variants in your trade advertisement.
- **Duplicate Prevention** – Prevent accidentally adding the same variant twice.
- **Automatic Saving** – Save your collection locally using JSON.

## Requirements

- Python 3.10 or newer recommended.
- No external Python packages required.

## Getting Started

1. Download or clone this repository.
2. Open the project folder.
3. Run the application:

```bash
python main.py
```

Your collection will automatically be saved in:

```text
data/collection.json
```

The collection file is generated locally when you use the program. It is not included in the repository.

## Project Structure

```text
SpriteTracker/
├── main.py
├── collection.py
├── sprites.py
├── data/
│   └── collection.json
├── README.md
├── LICENSE
└── .gitignore
```

## Trade Advertisement Categories

| Category | Description |
|---|---|
| LF | Sprite variants you are looking for. |
| UNMASTERED | Owned variants that still need mastery. |
| FT | Mastered variants available for trade. |

Each Sprite variant is tracked independently, so owning one variant does not mean you own the others.

## Data Storage

Your collection is stored locally in a JSON file. This allows your collection to persist between sessions
