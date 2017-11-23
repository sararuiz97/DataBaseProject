# Hashtag based tweet analysis

This project is a project for the Advanced Database class at ITESM Campus Guadalajara. It provides a web interface in which a hashtag can be introduced to a form, and the application will make a request to the Twitter API to fetch tweets with that hashtag, save it to a Neo4j local database, and display the info in a network graph.

## Getting Started

To use, modify, or analysis of this project all that is needed is to download, or clone the repository and install all prerequisites.

### Prerequisites

This project needs a fair amount of software in order to work.
For this you will need to install the following:

First, make sure that you have Python 3 and pip3 installed in your computer. After that you should install various libraries using pip3

Flask for the Web interface

```
pip3 install Flask

```

py2neo to work with the Neo4j Database

```
pip3 install py2neo

```

Tweepy to connect with the Twitter API

```
pip3 install tweepy

```

WTForms for the usage of the forms on Flask

```
pip3 install wtforms

```

Also install neo4j in your environment and setup the user and password credentials.

```
apt install neo4j
```

### Installing

Start the Neo4j server

```
service neo4j start
```

In the twitter_api.py change the credentials to match they ones of your neo4j database.
After that, run wep_inter.py

```
python3 wep_inter.py
```
