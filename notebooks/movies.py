# Databricks notebook source
!pip install pandas
!pip install matplotlib
!pip install seaborn

# COMMAND ----------

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import seaborn as sns

# COMMAND ----------

movies = pd.read_csv('movies.csv')

# COMMAND ----------

print(movies.shape)

# COMMAND ----------

movies = movies[movies['startYear'] > 1931]
print(movies.describe())

# COMMAND ----------

# MAGIC %md
# MAGIC ## First things first
# MAGIC 
# MAGIC You'll see that I used `display(plt.show())` instead of `plt.show()` directly. To view `matplotlib` objects, we need to use the `display` command.
# MAGIC 
# MAGIC Reference [here](https://docs.databricks.com/user-guide/visualizations/matplotlib-and-ggplot.html)

# COMMAND ----------

# MAGIC %md
# MAGIC # Getting to the point

# COMMAND ----------

# clf to clear the plot before plotting again.
plt.clf()
plt.hist(movies['runtimeMinutes'], range=(40, 200), bins=16, ec='black')
plt.title('Movies length')
plt.xlabel('Minutes')
plt.ylabel('Number of movies')
display(plt.show())
                

# COMMAND ----------

statistics_grouped = movies['runtimeMinutes'].groupby(movies['startYear']).describe()

# COMMAND ----------

# statistics_grouped is a multi index Series. To grab statistics like mean and std, I needed to use the syntax below instead of just statistics_grouped['mean']
avg_runtime_by_year = statistics_grouped[:, 'mean'] # Mean
avg_runtime_lower_band = statistics_grouped[:, 'mean'] - statistics_grouped[:, 'std'] # Lower band of data created using standard deviation.
avg_runtime_upper_band = statistics_grouped[:, 'mean'] + statistics_grouped[:, 'std'] # Upper band of data

# COMMAND ----------

# Here, I took a quick look at the indexes of the statistics_grouped
statistics_grouped.index[:0]

# COMMAND ----------

# MAGIC %md
# MAGIC ## First adjustment needed
# MAGIC 
# MAGIC When I was trying to run the following code:
# MAGIC 
# MAGIC `ax1.fill_between(statistics_grouped.index, avg_runtime_lower_band, avg_runtime_upper_band, facecolor='aqua')  # Fill space between bands to create confidence interval.`
# MAGIC 
# MAGIC I was getting this error:
# MAGIC 
# MAGIC `ufunc 'isfinite' not supported for the input types`
# MAGIC 
# MAGIC In order to make this code work, the first argument needs the indexes (years) to be plotted. I then needed to adjust the way we retrieve the years from `statistics_grouped`.
# MAGIC 
# MAGIC Instead of:
# MAGIC   `statistics_grouped.index`
# MAGIC   
# MAGIC We need to use:
# MAGIC   `statistics_grouped[:, 'mean'].index`
# MAGIC   
# MAGIC It's because `statistics_grouped` is a MultiIndex Series and we need the years, which are part of the main index. If we refer to the index of the `statistics_grouped` itself, we would have a collection of indexes.

# COMMAND ----------

plt.clf()
fig, axl = plt.subplots(figsize=(10, 5))
axl.plot(avg_runtime_by_year, color="blue")
axl.plot(avg_runtime_lower_band, color="aqua")
axl.plot(avg_runtime_upper_band, color="aqua")
axl.fill_between(statistics_grouped[:, 'mean'].index, avg_runtime_lower_band, avg_runtime_upper_band, facecolor="aqua") # Fill space between bands to create confidence interval
axl.set_title('Movies runtime by year')
axl.set_ylabel('Minutes')
axl.set_xlabel('Release year')
axl.set_xlim(1931, 2018)
legend_sd = mpatches.Patch(color='aqua', label='Mean +/- standard deviation') # Used mpatches to create rectangular for a legend
legend_line = mlines.Line2D([], [], color='blue', label='Mean runtime')
axl.legend(handles=[legend_line, legend_sd]) # Nice legend with rectangular and line
display(plt.show())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Second adjustment needed
# MAGIC 
# MAGIC As a beginner level 100-200 for Data Science, I still did not figure out how to append an array to a Serie, in a particular level. What we wanted is something like:
# MAGIC 
# MAGIC ```
# MAGIC Out[0]: 
# MAGIC startYear                      
# MAGIC 1932.0     count                    48.000000
# MAGIC            mean                     80.750000
# MAGIC            std                      15.484378
# MAGIC            min                      55.000000
# MAGIC            25%                      68.750000
# MAGIC            50%                      79.500000
# MAGIC            75%                      88.000000
# MAGIC            max                     140.000000
# MAGIC            included_movies_perc    0.12345678
# MAGIC ```
# MAGIC 
# MAGIC Where `included_movies_perc` would be an index for the second level (level index 1). But I couldn't find a way to do that yet.
# MAGIC 
# MAGIC Then, even knowing that this is not the performatic way (the best way is to add the collection on a single `concat` operation), I added the percentage values along the loop, like you'll see below.
# MAGIC 
# MAGIC You'll see an entire cell commented, couple slots below. It was a try but it didn't generate what I was expecting. Reference [here](https://pandas.pydata.org/pandas-docs/stable/merging.html)

# COMMAND ----------

percentage_of_included_movies = []
for year in statistics_grouped[:, 'mean'].index:
  movies_from_year = movies[movies['startYear'] == year]
  avg_runtime_low = avg_runtime_lower_band[int(year)]
  avg_runtime_up = avg_runtime_upper_band[int(year)]
  movies_included = movies_from_year[movies_from_year['runtimeMinutes'] > avg_runtime_low][movies_from_year['runtimeMinutes'] < avg_runtime_up]
  percentage_of_included_movies.append(len(movies_included)/len(movies_from_year))
  # Needed to add the value this way because the way it was doing on the blog post was not working
  # I'm still trying to figure out how to add the array on a single concat, which would be way more performatic than the add inside a loop
  statistics_grouped[year, 'included_movies_perc'] = len(movies_included)/len(movies_from_year)

# COMMAND ----------

#index = statistics_grouped.index.get_level_values(0)
#index = index.drop_duplicates()
#percentage_df = pd.DataFrame(percentage_of_included_movies, index=index)
#statistics_joined = statistics_grouped.to_frame()
#statistics_grouped = statistics_joined.join(percentage_df, how='inner')

# COMMAND ----------

statistics_grouped[:, 'included_movies_perc'].describe()

# COMMAND ----------

# Data
plt.clf()
fig, axl = plt.subplots(figsize=(10, 5))
axl.plot(avg_runtime_by_year, color="blue")
axl.plot(avg_runtime_lower_band, color="aqua")
axl.plot(avg_runtime_upper_band, color="aqua")
axl.fill_between(statistics_grouped[:, 'mean'].index, avg_runtime_lower_band, avg_runtime_upper_band, facecolor="aqua") # Fill space between bands to create confidence interval
axl.set_title('Movies runtime by year')
axl.set_ylabel('Minutes')
axl.set_xlabel('Release year')
axl.set_xlim(1931, 2018)

# Plot with proportions
ax2 = axl.twinx()
ax2.plot(statistics_grouped[:, 'included_movies_perc'], color='olive')
ax2.set_ylabel('Proportion')
plt.axhline(y=0.70, color='red', linestyle='dashed') # Add line at 0.70
legend_sd = mpatches.Patch(color='aqua', label='Mean +/- standard deviation') # Used mpatches to create rectangular for a legend
legend_line = mlines.Line2D([], [], color='blue', label='Mean runtime')
legend_line_2 = mlines.Line2D([], [], color='olive', label='Proportion included in CI')
dashed_line = mlines.Line2D([], [], color='red', label='Proportion = 0.7', linestyle='dashed')
axl.legend(handles=[legend_line, legend_sd, legend_line_2, dashed_line]) # Nice legend with rectangular and line
display(plt.show())

# COMMAND ----------

plt.clf()
# Data
avg_runtime_by_year = statistics_grouped[:, '50%']
avg_runtime_lower_band = statistics_grouped[:, '25%']
avg_runtime_upper_band = statistics_grouped[:, '75%']

# Plot
fig, axl = plt.subplots(figsize=(10, 5))
axl.plot(avg_runtime_by_year, color="blue")
axl.plot(avg_runtime_lower_band, color="aqua")
axl.plot(avg_runtime_upper_band, color="aqua")
axl.fill_between(statistics_grouped[:, 'mean'].index, avg_runtime_lower_band, avg_runtime_upper_band, facecolor="aqua")
axl.set_title('Movies runtime by year')
axl.set_ylabel('Minutes')
axl.set_xlabel('Release year')
axl.set_xlim(1931, 2018)

legend_sd = mpatches.Patch(color='aqua', label='Interquantile range')
legend_line = mlines.Line2D([], [], color='blue', label='Median runtime')
axl.legend(handles=[legend_line, legend_sd])
display(plt.show())

# COMMAND ----------

movies_since_1960 = movies[movies['startYear'] > 1960]

# COMMAND ----------

def top_n_movies(data, n):
  top_n_movies_per_year = data.groupby('startYear').head(n)
  stats = top_n_movies_per_year['runtimeMinutes'].groupby(top_n_movies_per_year['startYear']).describe()
  return stats

# COMMAND ----------

plt.clf()
statistics_grouped_50 = top_n_movies(movies_since_1960, 50)

# Data
avg_runtime_by_year = statistics_grouped_50[:, 'mean']
avg_runtime_lower_band = statistics_grouped_50[:, 'mean'] - statistics_grouped_50[:, 'std']
avg_runtime_upper_band = statistics_grouped_50[:, 'mean'] + statistics_grouped_50[:, 'std']

# COMMAND ----------

# Plot
fig, axl = plt.subplots(figsize=(10, 5))
axl.plot(avg_runtime_by_year, color="blue")
axl.plot(avg_runtime_lower_band, color="aqua")
axl.plot(avg_runtime_upper_band, color="aqua")
axl.fill_between(statistics_grouped_50[:, 'mean'].index, avg_runtime_lower_band, avg_runtime_upper_band, facecolor='aqua')
axl.set_ylabel('Runtime of 50 most popular movies by year')
axl.set_xlabel('Minutes')
axl.set_xlim(1960, 2018)
legend_sd = mpatches.Patch(color='aqua', label='Mean +/- standard deviation')
legend_line = mlines.Line2D([], [], color='blue', label='Mean runtime')
axl.legend(handles=[legend_line, legend_sd])
display(plt.show())

# COMMAND ----------

# Data
mean_10 = top_n_movies(movies_since_1960, 10)[:, 'mean']
mean_30 = top_n_movies(movies_since_1960, 30)[:, 'mean']
mean_50 = top_n_movies(movies_since_1960, 50)[:, 'mean']
mean_100 = top_n_movies(movies_since_1960, 100)[:, 'mean']
mean_all = top_n_movies(movies_since_1960, len(movies_since_1960))[:, 'mean']

# COMMAND ----------

plt.clf()
# Chart
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(mean_10, color='black')
ax.plot(mean_30, color='blue')
ax.plot(mean_50, color='red')
ax.plot(mean_100, color='green')
ax.plot(mean_all, color='purple')

ax.set_title('Movies runtime by year')
ax.set_ylabel('Minutes')
ax.set_xlabel('Release year')
ax.set_xlim(1960, 2018)
ax.legend(labels=['10 most popular movies', '30 most popular movies', '50 most popular movies', '100 most popular movies', 'All popular movies'])
display(plt.show())

# COMMAND ----------

total_mean = pd.Series()
mean_list = [mean_10, mean_30, mean_50, mean_100, mean_all]
index_list = ['top_10', 'top_30', 'top_50', 'top_100', 'all']
for i in range(0, 5):
  mean_n = pd.Series([mean_list[i].mean()], index=[index_list[i]])
  total_mean = total_mean.append(mean_n)
  
print(total_mean)

# COMMAND ----------

plt.clf()
# Plotting movies by decade
movies_by_decade = movies.copy()
movies_by_decade['startYear'] = ((movies_by_decade['startYear'] // 10) * 10).astype('int64')
sns.boxplot(x="startYear", y="runtimeMinutes", data=movies_by_decade, color='lightskyblue', showfliers=False)
plt.ylim(40, 180)
plt.title('MOvies runtime by decade')
plt.xlabel('Decade')
plt.ylabel('Minutes')
display(plt.show())

# COMMAND ----------

# This code is not working. It is returning 48 (?)
start_year = 0  # This will be starting year of the data.
# Create data frame with year as first column and movie count as second.
movies_per_year = movies['startYear'].value_counts().sort_index()  # The year is an index, we need it as a column.
movies_per_year_df = pd.DataFrame({'year': movies_per_year.index, 'movie_count': movies_per_year.values})

for i in range(0, len(movies_per_year_df)):
    year = movies_per_year_df.iloc[i, 0]
    movie_count = movies_per_year_df.iloc[i, 1]
    # Check if in a given year there were more than 30 movies.
    if movie_count > 30:
        movies_per_year_df = movies_per_year_df.iloc[i:, :]  # Drop years before current one in the loop
        # Check whether the rest of years have movie count above 30, if not, the loop continues.
        # If every year left has movie count above 30, the loop breaks and we have the answer.
        if sum(movies_per_year_df['movie_count'] < 30) == 0:
            start_year = year
            break

print(start_year) # There's something wrong here, we need to check