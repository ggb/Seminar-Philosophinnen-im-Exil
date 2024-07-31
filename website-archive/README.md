# Philosophers in Exile

This project creates a website for displaying information about philosophers in exile using data from Turtle files.

## Features

- Displays detailed information about philosophers including their biography and bibliography.
- Responsive design with a sidebar for easy navigation.
- Automatically formats and links RDF data.

## Prerequisites

- Python 3.x
- Git

## Setup

1. **Clone the repository**:

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. **Run the setup script to create a virtual environment and install dependencies**:

    ```bash
    ./setup.sh
    ```

3. **Activate the virtual environment**:

    ```bash
    source venv/bin/activate
    ```

4. **Ensure the Turtle files are located in the `turtle_files` directory one level above the project directory**. Your project structure should look like this:

    ```plaintext
    project_directory/
    ├── setup.sh
    ├── app.py
    ├── config.json
    ├── requirements.txt
    ├── templates/
    │   ├── index.html
    │   └── philosopher.html
    └── ../turtle_files/
        ├── ayn_rand.ttl
        └── other_philosophers.ttl
    ```

5. **Run the Flask application**:

    ```bash
    python app.py
    ```

6. **Open your web browser and go to**:

    ```
    http://127.0.0.1:5000/
    ```

## Project Structure

- `app.py`: Main application script.
- `templates/`: Directory containing HTML templates.
  - `index.html`: Template for the homepage.
  - `philosopher.html`: Template for displaying philosopher details.
- `config.json`: Configuration file containing RDF predicates mappings.
- `requirements.txt`: List of Python dependencies.
- `setup.sh`: Shell script to set up the environment and install dependencies.
- `README.md`: This file.

## Configuration

The `config.json` file contains the mappings for RDF predicates to the corresponding fields in the application. You can adjust these mappings based on the data in your Turtle files.

### Example `config.json`

```json
{
    "stammdaten_predicates": {
        "http://www.w3.org/2002/07/owl#sameAs": "sameAs",
        "http://xmlns.com/foaf/0.1/name": "name",
        "http://xmlns.com/foaf/0.1/givenName": "givenName",
        "http://xmlns.com/foaf/0.1/familyName": "familyName",
        "http://xmlns.com/foaf/0.1/nick": "nick",
        "http://xmlns.com/foaf/0.1/birthDate": "birthDate",
        "http://xmlns.com/foaf/0.1/deathDate": "deathDate",
        "http://xmlns.com/foaf/0.1/birthPlace": "birthPlace",
        "http://xmlns.com/foaf/0.1/deathPlace": "deathPlace",
        "http://dbpedia.org/ontology/nationality": "nationality",
        "http://dbpedia.org/ontology/occupation": "occupation"
    }
}

## WARNING

This project is aimed to work with standardized turtle files that follow a certain guide.
If the turtle file is similar to this example, it should be parsed and displayed just fine:

```ttl
@prefix ex: <http://www.exiled-philosophers.org/> . 

@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dbo: <http://dbpedia.org/ontology/> .
@prefix dbr: <http://dbpedia.org/resource/> . 
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix dcterms: <http://purl.org/dc/terms/> .

@prefix bio: <http://purl.org/vocab/bio/0.1/> .
@prefix bibo: <http://purl.org/ontology/bibo/> .

ex:Hannah_Arendt a foaf:Person 
    ; foaf:name "Hannah Arendt"
    ; owl:sameAs dbr:Hannah_Arendt
    ; owl:sameAs <https://explore.gnd.network/gnd/11850391X>
    ; dbo:birthName "Hannah Arendt"
    ; dbo:birthDate "1906-10-14"^^xsd:date
    ; dbo:birthPlace dbr:Linden-Limmer
    ; dbo:deathDate "1975-12-04"^^xsd:date
    ; dbo:influencedBy dbr:Karl_Jaspers, dbr:Martin_Heidegger, dbr:Walter_Benjamin
    ; dbo:influenced dbr:Giorgio_Agamben, dbr:Judith_N._Shklar 
    ; bio:event _:emigrationParis, _:emigrationNewYork, _:marriageAnders, _:marriageBlücher, _:graduation
    ; dbo:author _:vitaActiva, _:ursprünge .

_:emigrationParis a bio:Emigration 
    ; bio:date "1933"^^xsd:gYear 
    ; bio:place dbr:Berlin, dbr:Paris
    ; rdfs:label "Nachdem sie von der Gestapo verhaftet wurde, beschließt Arendt Deutschland zu verlassen. Sie flieht über Karlsbad, Genua und Genf nach Paris." .

_:emigrationNewYork a bio:Emigration
    ; bio:date "1941"^^xsd:gYear 
    ; bio:place dbr:Paris, dbr:New_York 
    ; rdfs:label "Nach einer abenteuerlichen Flucht aus dem Lager Gurs gelingt Arendt zusammen mit ihrem zweiten Mann Heinrich Blücher die Flucht über Spanien und Portugal nach New York." .

_:marriageAnders a bio:Marriage 
    ; bio:partner dbr:Günther_Anders
    ; rdfs:label "Arendt heiratet Günther Anders-Stern 1929, die Ehe wird bereits 1937 geschieden. Anders hilft ihr und ihrem zweiten Ehemann bei der Flucht in die USA. Beide bleiben lebenslang in Kontakt, s. Briefwechsel."
    ; dcterms:references _:briefwechselArendtAnders
    ; bio:date "1929"^^xsd:gYear 
    ; bio:place dbr:Nowawes
    ; bio:event [
        a bio:Divorce 
        ; bio:date "1937"^^xsd:date
    ] .

_:marriageBlücher a bio:Marriage 
    ; bio:partner dbr:Heinrich_Blücher
    ; bio:date "1940"^^xsd:gYear 
    ; bio:place dbr:Paris .

_:graduation a bio:Graduation 
    ; bio:date "1928"^^xsd:gYear 
    ; bio:place dbr:Heidelberg 
    ; bio:participant dbr:Karl_Jaspers
    ; rdfs:label "Arendt promoviert bei Karl Jaspers in Heidelberg mit einer Arbeit mit dem Titel 'Der Liebesbegriff bei Augustin'." .

_:vitaActiva a bibo:Book
    ; dcterms:title "Vita Activa" 
    ; dcterms:creator ex:Hannah_Arendt, dbr:Hannah_Arendt 
    ; dcterms:issued "1958"^^xsd:gYear 
    ; bibo:isbn "9783406648364" 
    ; dcterms:publisher "Piper" 
    ; dcterms:language "de" 
    ; dcterms:subject "Political theory", "Philosophy of history" .

_:ursprünge a bibo:Book 
    ; dcterms:title "Elemente und Ursprünge totaler Herrschaft" 
    ; dcterms:creator ex:Hannah_Arendt, dbr:Hannah_Arendt 
    ; dcterms:issued "1951"^^xsd:gYear 
    ; bibo:isbn "9783596294311" 
    ; dcterms:publisher "Piper" 
    ; dcterms:language "de" 
    ; dcterms:subject "Totalitarianism", "Political theory" .

_:briefwechselArendtAnders a bibo:Book
    ; dcterms:title "Schreib doch mal ,hard facts' über dich. Briefe 1939-1975" 
    ; dcterms:creator ex:Hannah_Arendt, dbr:Hannah_Arendt, dbr:Günther_Anders 
    ; dcterms:issued "1993"^^xsd:gYear 
    ; bibo:isbn "9783492311724" 
    ; dcterms:publisher "Piper" 
    ; dcterms:language "de" 
    ; dcterms:subject "Correspondence", "Philosophy", "Political theory" .
```