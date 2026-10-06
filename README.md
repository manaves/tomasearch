# TomaSearch: Tomato Co-expression Network Viewer

Explore your tomato database effortlessly with our intuitive viewer. Navigate through tables to get information about co-expression networks. Search for specific terms, view images, and download data in CSV format.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.1-092E20?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-database-4169E1?logo=postgresql&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-graphs-2C8EBB)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

> **Live website:** not available yet. The database that powers TomaSearch is currently private and will be made public in the future. As soon as it is, a link to the deployed application will be added here.

> **Note:** The database information is private, so you cannot run this code with the provided data. You can connect your own database if the tables have the same structure (column names and types).

---

## Demo

Watch the full walkthrough of TomaSearch. Click the thumbnail below to play it on YouTube:

[![Watch the TomaSearch demo video](https://img.youtube.com/vi/sicuC1XOn84/maxresdefault.jpg)](https://youtu.be/sicuC1XOn84)

---

## Features

- **Search** the database by gene name, GO term, GO identifier, or subontology.
- **Interactive tables** with selectable columns, including subgraph membership, enrichment, and p-values.
- **Gene network visualization** of co-expression subgraphs, with customizable node size, node color, font size, edge width, and edge opacity.
- **Download** search results as CSV and export graphs as PNG.
- **Informational pages** documenting how the data was collected, processed, and analyzed.

---

## Screenshots

### Home

![Home](https://drive.google.com/uc?export=view&id=17E35LeUQQSV0AcvC9IyFAEWP0Qi00J9W)

### Information

![Information](https://drive.google.com/uc?export=view&id=1qaYN1VqXKpcBSazmpRm_wY4LhiuB-0Uz)

### How It Works

![HowItWorks](https://drive.google.com/uc?export=view&id=1q91NcM9yfYmEZcbFvqZKLblWtLRtDn3D)

### Search

The **Search** section allows you to query the database by:

- Gene name
- GO term
- GO identifier
- Subontology

You can view the results in a table and download the information in CSV format.

![Search](https://drive.google.com/uc?export=view&id=15vNQHMb7bvMVI-z0SfMvtOPGSIsxsSOn)
![ResultsTable](https://drive.google.com/uc?export=view&id=11jXCfuxlOxRUHK1Z8bT6iqrGkQYab9Fk)

### Images

In the **Images** section, you can visualize the relationships between genes in a subgraph.

![GeneNetwork](https://drive.google.com/uc?export=view&id=1mqAYFMtLl4Xs_K5wZ-u4-cHAtg0rdaJp)

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Python, Django 5.1 |
| Database | PostgreSQL (accessed with `psycopg2`) |
| Graph analysis | NetworkX |
| Graph visualization | vis-network (Vis.js) |
| Static/media hosting | Cloudinary |
| Configuration | `python-dotenv`, `dj-database-url` |

---

## Project Structure

```
tomasearch/
├── convert_graph_to_pickle.py     # Clean a GraphML graph and convert it to a pickled NetworkX graph
├── upload_graph.py                # Upload the pickled graph to Cloudinary and print its URL
├── LICENSE
└── tomasearch/
    ├── manage.py
    ├── tomasearch/                # Django project (settings, URLs, WSGI/ASGI)
    └── myapp/                     # Main Django application
        ├── models.py              # Functions, Subgraph and Enrichment models
        ├── views.py               # Search, images and CSV download views
        ├── graph_loader.py        # Downloads and loads the graph at startup
        ├── templates/myapp/       # HTML templates (home, search, images, ...)
        └── templatetags/          # Custom template filters
```

---

## Getting Started

Because the production database is private, the steps below describe how to run the application locally against **your own database**, provided it matches the expected schema (see [Data model](#data-model)).

### Prerequisites

- Python 3.x
- PostgreSQL (or access to a PostgreSQL-compatible database)
- A Cloudinary account (only needed if you want to host the graph file yourself)

### 1. Clone the repository

```bash
git clone https://github.com/manaves/tomasearch.git
cd tomasearch
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install django==5.1.6 dj-database-url python-dotenv cloudinary psycopg2-binary networkx requests django-debug-toolbar
```

### 4. Configure environment variables

Create a `.env` file in the repository root (it is already ignored by `.gitignore`):

```dotenv
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Cloudinary credentials (either CLOUDINARY_URL or the three individual variables)
CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>

# URL of the pickled NetworkX graph the app downloads on startup
GRAPH_FILE_URL=https://res.cloudinary.com/<cloud_name>/raw/upload/<path>/graph.pkl
```

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Django secret key. **Required** — the app refuses to start without it. |
| `DEBUG` | Enables debug mode and the Django Debug Toolbar. Defaults to `False`. |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts. |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL connection settings. |
| `CLOUDINARY_URL` | Cloudinary credentials. Alternatively, set `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET`. |
| `GRAPH_FILE_URL` | Public URL of the pickled NetworkX graph loaded in `myapp/graph_loader.py`. |

### 5. Prepare the graph file

The **Images** section relies on a pickled NetworkX graph downloaded from `GRAPH_FILE_URL`. To generate and host your own graph:

```bash
# Place your graph as tomasearch/tomasearch/myapp/graphs/graph.graphml first
python convert_graph_to_pickle.py   # produces .../graphs/graph.pkl
python upload_graph.py              # uploads it to Cloudinary and prints GRAPH_FILE_URL
```

### 6. Run the development server

```bash
cd tomasearch
python manage.py runserver
```

Then open <http://127.0.0.1:8000/>.

---

## Data Model

The application expects three tables. If you connect your own database, use the same table and column names.

| Model | Table | Key columns |
| --- | --- | --- |
| `Functions` | `genes_and_go_terms` | `gene`, `go_identifier`, `go_term`, `subontology` |
| `Subgraph` | `genes_and_subgraph` | `gene`, `subgraph` |
| `Enrichment` | `go_terms_and_enrichment` | `go_identifier`, `subgraph`, `enrichment`, `p_value` |

---

## Data & Methodology

The RNA-seq data were obtained from the Sequence Read Archive (SRA) and belong to tomato (*Solanum lycopersicum*), sequenced on the Illumina platform across 310 samples and multiple tissues. The processing and analysis pipeline uses:

- **FastP** – read trimming and quality filtering.
- **HISAT2** – alignment to the tomato reference genome.
- **SAMtools** – alignment file manipulation.
- **Tablet** – visual inspection of alignments.
- **StringTie** – transcript assembly and quantification.
- **Cluster 3.0** – expression filtering, normalization, and clustering.
- **Python** (NumPy, Pandas, Matplotlib, Seaborn, NetworkX, GOAtools, SciPy) – data handling, visualization, graph analysis, and enrichment.
- **Statistics** – Fisher's exact test with Bonferroni correction.

Co-expression subgraphs are derived from an adjacency matrix filtered by Pearson correlation ≥ 0.9. Enrichment results are shown with a p-value threshold of `2.601457e-05`.

For the full description, see the **Information** page inside the application.

---

## License

Released under the [MIT License](LICENSE).
