from flask import Flask, render_template_string
import os
import json
from rdflib import Graph, URIRef
from jinja2 import Environment, FileSystemLoader
import rdflib
from datetime import datetime
import re

app = Flask(__name__)

# Load configuration file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Define a class to store philosopher's data
class Philosopher:
    def __init__(self, stammdaten, biographie, bibliographie):
        self.stammdaten = stammdaten
        self.biographie = biographie
        self.bibliographie = bibliographie

# Parse a Turtle (.ttl) file and return an RDF graph
def parse_turtle(file_path):
    g = Graph()
    g.parse(file_path, format="ttl")
    return g

# Convert a slug (URL-friendly string) to a readable format
def slug_to_readable(slug):
    return slug.replace('_', ' ').title()

# Format date strings into more readable formats
def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%B %d, %Y')
    except ValueError:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m')
            return date_obj.strftime('%B %Y')
        except ValueError:
            try:
                date_obj = datetime.strptime(date_str, '%Y')
                return date_obj.strftime('%Y')
            except ValueError:
                return date_str.strip()

# Format RDF labels to be more readable
def format_label(label):
    label = label.replace('_', ' ')
    label = re.sub(r'([a-z])([A-Z])', r'\1 \2', label)
    label = label.title()
    return label

# Format RDF objects into clickable links if they are URIs
def format_link(obj):
    if isinstance(obj, URIRef):
        slug = obj.split('/')[-1]
        return f"<a href='{obj}'>{slug_to_readable(slug)}</a>"
    return str(obj)

# Extract 'stammdaten' (basic data) from the RDF graph
def extract_stammdaten(graph, philosopher_name):
    stammdaten = {}
    subject = URIRef(f"http://www.exiled-philosophers.org/{philosopher_name.replace(' ', '_')}")
    for predicate, obj in graph.predicate_objects(subject=subject):
        pred_str = str(predicate)
        if pred_str in config["stammdaten_predicates"]:
            key = config["stammdaten_predicates"][pred_str]
            if key == "subjects":
                if key not in stammdaten:
                    stammdaten[key] = []
                stammdaten[key].append(format_link(obj))
            else:
                stammdaten[key] = format_date(str(obj)) if "date" in key.lower() else format_link(obj)
    formatted_stammdaten = {format_label(k): v for k, v in stammdaten.items()}
    return formatted_stammdaten

# Extract 'biographie' (biography) from the RDF graph
def extract_biographie(graph, philosopher_name):
    biographie = []
    subject = URIRef(f"http://www.exiled-philosophers.org/{philosopher_name.replace(' ', '_')}")
    for predicate, obj in graph.predicate_objects(subject=subject):
        if str(predicate).startswith("http://purl.org/vocab/bio/0.1/"):
            event_details = extract_event_details(graph, obj)
            if event_details:
                biographie.append(event_details)
    biographie.sort(key=lambda x: x.get("date", ""))
    return biographie

# Extract details of biography events from the RDF graph
def extract_event_details(graph, event):
    event_details = {}
    for predicate, obj in graph.predicate_objects(subject=event):
        pred_str = str(predicate)
        if pred_str == "http://purl.org/vocab/bio/0.1/date":
            event_details["date"] = format_date(str(obj))
        elif pred_str == "http://www.w3.org/2000/01/rdf-schema#label":
            event_details["description"] = str(obj)
        elif pred_str == "http://purl.org/vocab/bio/0.1/partner":
            event_details["partner"] = format_link(obj)
        elif pred_str == "http://purl.org/vocab/bio/0.1/place":
            event_details["place"] = format_link(obj)
    return event_details

# Extract 'bibliographie' (bibliography) from the RDF graph
def extract_bibliographie(graph, philosopher_name):
    bibliographie = []
    subject = URIRef(f"http://www.exiled-philosophers.org/{philosopher_name.replace(' ', '_')}")
    for predicate, obj in graph.predicate_objects(subject=subject):
        if str(predicate) == "http://dbpedia.org/ontology/author":
            book_details = extract_book_details(graph, obj)
            if book_details:
                bibliographie.append(book_details)
    return bibliographie

# Extract details of books from the RDF graph
def extract_book_details(graph, book):
    book_details = {}
    for predicate, obj in graph.predicate_objects(subject=book):
        pred_str = str(predicate)
        if pred_str == "http://purl.org/dc/terms/title":
            book_details["title"] = str(obj)
        elif pred_str == "http://purl.org/dc/terms/issued":
            book_details["year"] = format_date(str(obj))
        elif pred_str == "http://purl.org/ontology/bibo/isbn":
            book_details["isbn"] = str(obj)
        elif pred_str == "http://www.w3.org/2000/01/rdf-schema#label":
            book_details["label"] = str(obj)
        elif pred_str == "http://www.w3.org/2002/07/owl#sameAs":
            book_details["sameAs"] = format_link(obj)
    return book_details

# Render HTML for a philosopher's page using a Jinja2 template
def render_html(philosopher, template_path='templates'):
    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template('philosopher.html')
    return template.render(philosopher=philosopher)

# Render HTML for the main page listing all philosophers
def render_main_page(philosophers, template_path='templates'):
    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template('index.html')
    return template.render(philosophers=philosophers)

# List all philosophers based on available Turtle files in the data directory
def list_philosophers(data_dir):
    philosophers = [f.split('.')[0] for f in os.listdir(data_dir) if f.endswith('.ttl')]
    return philosophers

# Route for the main page displaying a list of philosophers
@app.route('/')
def index():
    data_dir = '../turtle_files'
    philosophers = list_philosophers(data_dir)
    html_content = render_main_page(philosophers)
    return render_template_string(html_content)

# Route for displaying details of a specific philosopher
@app.route('/philosopher/<name>')
def show_philosopher(name):
    file_path = os.path.join('../turtle_files', f'{name}.ttl')
    g = parse_turtle(file_path)
    stammdaten = extract_stammdaten(g, name)
    biographie = extract_biographie(g, name)
    bibliographie = extract_bibliographie(g, name)
    philosopher = Philosopher(stammdaten, biographie, bibliographie)
    html_content = render_html(philosopher)
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run()

# Load configuration file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

class Philosopher:
    def __init__(self, stammdaten, biographie, bibliographie):
        self.stammdaten = stammdaten
        self.biographie = biographie
        self.bibliographie = bibliographie

def parse_turtle(file_path):
    g = Graph()
    g.parse(file_path, format="ttl")
    return g

def slug_to_readable(slug):
    return slug.replace('_', ' ').title()

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%B %d, %Y')
    except ValueError:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m')
            return date_obj.strftime('%B %Y')
        except ValueError:
            try:
                date_obj = datetime.strptime(date_str, '%Y')
                return date_obj.strftime('%Y')
            except ValueError:
                return date_str.strip()

def format_label(label):
    label = label.replace('_', ' ')
    label = re.sub(r'([a-z])([A-Z])', r'\1 \2', label)
    label = label.title()
    return label

def format_link(obj):
    if isinstance(obj, URIRef):
        slug = obj.split('/')[-1]
        return f"<a href='{obj}'>{slug_to_readable(slug)}</a>"
    return str(obj)

def extract_stammdaten(graph, philosopher_name):
    stammdaten = {}
    subject = URIRef(f"http://www.exiled-philosophers.org/{philosopher_name.replace(' ', '_')}")
    for predicate, obj in graph.predicate_objects(subject=subject):
        pred_str = str(predicate)
        if pred_str in config["stammdaten_predicates"]:
            key = config["stammdaten_predicates"][pred_str]
            if key == "subjects":
                if key not in stammdaten:
                    stammdaten[key] = []
                stammdaten[key].append(format_link(obj))
            else:
                stammdaten[key] = format_date(str(obj)) if "date" in key.lower() else format_link(obj)
    formatted_stammdaten = {format_label(k): v for k, v in stammdaten.items()}
    return formatted_stammdaten

def extract_biographie(graph, philosopher_name):
    biographie = []
    subject = URIRef(f"http://www.exiled-philosophers.org/{philosopher_name.replace(' ', '_')}")
    for predicate, obj in graph.predicate_objects(subject=subject):
        if str(predicate).startswith("http://purl.org/vocab/bio/0.1/"):
            event_details = extract_event_details(graph, obj)
            if event_details:
                biographie.append(event_details)
    biographie.sort(key=lambda x: x.get("date", ""))
    return biographie

def extract_event_details(graph, event):
    event_details = {}
    for predicate, obj in graph.predicate_objects(subject=event):
        pred_str = str(predicate)
        if pred_str == "http://purl.org/vocab/bio/0.1/date":
            event_details["date"] = format_date(str(obj))
        elif pred_str == "http://www.w3.org/2000/01/rdf-schema#label":
            event_details["description"] = str(obj)
        elif pred_str == "http://purl.org/vocab/bio/0.1/partner":
            event_details["partner"] = format_link(obj)
        elif pred_str == "http://purl.org/vocab/bio/0.1/place":
            event_details["place"] = format_link(obj)
    return event_details

def extract_bibliographie(graph, philosopher_name):
    bibliographie = []
    subject = URIRef(f"http://www.exiled-philosophers.org/{philosopher_name.replace(' ', '_')}")
    for predicate, obj in graph.predicate_objects(subject=subject):
        if str(predicate) == "http://dbpedia.org/ontology/author":
            book_details = extract_book_details(graph, obj)
            if book_details:
                bibliographie.append(book_details)
    return bibliographie

def extract_book_details(graph, book):
    book_details = {}
    for predicate, obj in graph.predicate_objects(subject=book):
        pred_str = str(predicate)
        if pred_str == "http://purl.org/dc/terms/title":
            book_details["title"] = str(obj)
        elif pred_str == "http://purl.org/dc/terms/issued":
            book_details["year"] = format_date(str(obj))
        elif pred_str == "http://purl.org/ontology/bibo/isbn":
            book_details["isbn"] = str(obj)
        elif pred_str == "http://www.w3.org/2000/01/rdf-schema#label":
            book_details["label"] = str(obj)
        elif pred_str == "http://www.w3.org/2002/07/owl#sameAs":
            book_details["sameAs"] = format_link(obj)
    return book_details

def render_html(philosopher, template_path='templates'):
    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template('philosopher.html')
    return template.render(philosopher=philosopher)

def render_main_page(philosophers, template_path='templates'):
    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template('index.html')
    return template.render(philosophers=philosophers)

def list_philosophers(data_dir):
    philosophers = [f.split('.')[0] for f in os.listdir(data_dir) if f.endswith('.ttl')]
    return philosophers

@app.route('/')
def index():
    data_dir = '../turtle_files'
    philosophers = list_philosophers(data_dir)
    html_content = render_main_page(philosophers)
    return render_template_string(html_content)

@app.route('/philosopher/<name>')
def show_philosopher(name):
    file_path = os.path.join('../turtle_files', f'{name}.ttl')
    g = parse_turtle(file_path)
    stammdaten = extract_stammdaten(g, name)
    biographie = extract_biographie(g, name)
    bibliographie = extract_bibliographie(g, name)
    philosopher = Philosopher(stammdaten, biographie, bibliographie)
    html_content = render_html(philosopher)
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run(debug=True)
