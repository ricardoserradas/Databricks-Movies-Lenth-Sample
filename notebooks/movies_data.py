# Databricks notebook source
!pip install panda

# COMMAND ----------

import pandas as pd

# COMMAND ----------

movies = pd.read_csv('https://datasets.imdbws.com/title.basics.tsv.gz', compression='gzip', sep='\t')
print('"title.basics.tsv.gz" downloaded')
ratings = pd.read_csv('https://datasets.imdbws.com/title.ratings.tsv.gz', compression='gzip', sep='\t')
print('"title.ratings.tsv.gz" downloaded')

print('Movies and Ratings shapes')
print(movies.shape)
print(ratings.shape)

print('Movies and Ratings columns')
print(movies.columns)
print(ratings.columns)

# COMMAND ----------

# Merge data on tconst, which is unique id for any title and common between the two datasets.
# movies_ratings = pd.merge(movies, ratings, on='tconst')
movies = pd.merge(movies, ratings, on='tconst')
print('Movies shape after merge')
print(movies.shape)

print('Movies columns after merge')
print(movies.columns)

# COMMAND ----------

# MAGIC %md
# MAGIC # Getting rid of unnecessary data

# COMMAND ----------

# print(movies['titleType'].unique())
movies = movies[movies['titleType'].isin(['movie', 'tvMovie'])]

print(movies.shape)

# COMMAND ----------

genres = movies['genres'].unique()
print(len(genres))

#movies_ratings = movies_ratings[movies_ratings['genres'].str.contains('Documentary') == False]
#print(movies_ratings.shape)

# COMMAND ----------

# Removing the movies tagged as 'Documentary'
movies = movies[movies['genres'].str.contains('Documentary') == False]
print(len(movies))

# COMMAND ----------

# Transforming the data to have only what we need
movies = movies[['startYear', 'runtimeMinutes', 'numVotes']]
print(movies.shape)

for column in movies.columns.values.tolist():
  movies[column] = pd.to_numeric(movies[column], errors='coerce')
  
movies = movies.dropna()
print(movies.shape)

# COMMAND ----------

# Movies with less than 40 minutes are considered short film
movies = movies[movies['runtimeMinutes'] > 40]
print(movies.shape)
# Removing movies with less then 1000 votes
movies = movies[movies['numVotes'] >= 1000]
print(movies.shape)

# COMMAND ----------

print(movies.describe())

# COMMAND ----------

movies.to_csv('movies.csv', index=False)
print('Success!')