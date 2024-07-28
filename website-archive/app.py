from flask import Flask, render_template_string
import os
from rdflib import Graph, URIRef
from jinja2 import Environment, FileSystemLoader
import rdflib

app = Flask(__name__)

class Philosopher:
    def __init__(self, stammdaten, biographie, bibliographie):
        self.stammdaten = stammdaten
        self.biographie = biographie
        self.bibliographie = bibliographie

def parse_turtle(file_path):
    g = Graph()
    g.parse(file_path, format="ttl")
    return g

def extract_stammdaten(graph, philosopher_name):
    stammdaten = {}
    subject = URIRef(f"http://www.exiled-philosophers.org/{philosopher_name.replace(' ', '_')}")
    for predicate, obj in graph.predicate_objects(subject=subject):
        pred_str = str(predicate)
        obj_str = str(obj)

        if pred_str == "http://www.w3.org/2002/07/owl#sameAs":
            stammdaten["sameAs"] = obj_str
        elif pred_str == "http://purl.org/dc/terms/name":
            stammdaten["name"] = obj_str
        elif pred_str == "http://xmlns.com/foaf/0.1/birthDate":
            stammdaten["birthDate"] = obj_str
        elif pred_str == "http://xmlns.com/foaf/0.1/birthPlace":
            stammdaten["birthPlace"] = obj_str
        elif pred_str == "http://xmlns.com/foaf/0.1/deathDate":
            stammdaten["deathDate"] = obj_str
        elif pred_str == "http://xmlns.com/foaf/0.1/deathPlace":
            stammdaten["deathPlace"] = obj_str
        elif pred_str == "http://xmlns.com/foaf/0.1/nationality":
            stammdaten["nationality"] = obj_str
        elif pred_str == "http://purl.org/dc/terms/description":
            stammdaten["description"] = obj_str
        elif pred_str == "http://purl.org/dc/terms/subject":
            if "subjects" not in stammdaten:
                stammdaten["subjects"] = []
            stammdaten["subjects"].append(obj_str)
        # Add more predicates as needed
    
    return stammdaten

def extract_biographie(graph, philosopher_name):
    biographie = []
    subject = URIRef(f"http://www.exiled-philosophers.org/{philosopher_name.replace(' ', '_')}")
    
    for predicate, obj in graph.predicate_objects(subject=subject):
        if str(predicate) == "http://purl.org/vocab/bio/0.1/event":
            event_details = extract_event_details(graph, obj)
            biographie.append(event_details)
    
    biographie.sort(key=lambda x: x.get("date", ""))
    return biographie

def extract_event_details(graph, event):
    event_details = {}
    for predicate, obj in graph.predicate_objects(subject=event):
        event_details[str(predicate)] = str(obj)
    return event_details

def extract_bibliographie(graph):
    bibliographie = []
    
    for subject, predicate, obj in graph.triples((None, rdflib.RDF.type, URIRef("http://purl.org/ontology/bibo/Book"))):
        book_details = extract_book_details(graph, subject)
        bibliographie.append(book_details)
    
    return bibliographie

def extract_book_details(graph, book):
    book_details = {}
    for predicate, obj in graph.predicate_objects(subject=book):
        book_details[str(predicate)] = str(obj)
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
    data_dir = 'data'
    philosophers = list_philosophers(data_dir)
    html_content = render_main_page(philosophers)
    return render_template_string(html_content)

@app.route('/philosopher/<name>')
def show_philosopher(name):
    file_path = os.path.join('data', f'{name}.ttl')
    g = parse_turtle(file_path)
    stammdaten = extract_stammdaten(g, name)
    biographie = extract_biographie(g, name)
    bibliographie = extract_bibliographie(g)
    philosopher = Philosopher(stammdaten, biographie, bibliographie)
    html_content = render_html(philosopher)
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run(debug=True)
