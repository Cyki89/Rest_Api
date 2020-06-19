# Udemy_Courses_Rest_Api

## Overview
The goal of this project is to build ML system available with REST API. For building the ML service I used <i>Django</i> and <i>Django Rest Framework</i>.This machine learning web service system is designed to predict the number of subscribers of a online course after a specified time based on parameters such as:
- keywords in course title
- course price 
- course level
- number of lectures
- content duration

I trained several ML models (with tuning hyperparameters) and placed them on a web server:
- LinearRegression
- RidgeRegression
- LassoRegression
- SVR with RBF kernel
- KNeighborsRegressor
- RandomForestRegressor
- GradientBoostingRegressor

## Data
Data come from [https://www.kaggle.com/andrewmvd/udemy-courses/](https://www.kaggle.com/andrewmvd/udemy-courses/). Dataset cointains 3600+ Udemy Course come from 4 categories:
- Business Finance
- Graphic Design 
- Musical Instruments
- Web Development

## Requirements
* python 3.7
* django 2.2.7
* djangorestframework 3.11.0
* pandas
* numpy
* nltk
* scikit-learn
* plotly

## Data
Data come from [https://grouplens.org/datasets/movielens/](https://grouplens.org/datasets/movielens/). I used <i>100K</i> movie ratings dataset from <i>2018</i> year.

## Scope of work
* Create RDD of movie similarities
* Set similarity thresholds for movie ratings, category and co occurrence
* Reduce RDD of movie similarities based on similarity thresholds
* Set the rules for the recommendation system
* Create test cases
* Evaluate the recommendation system based on test cases
* Discuss the results
* Create a Movie Recommendation System Console Application 

## Content
* <i>Movie_Recommendation_System_Notebook.ipynb</i> - notebook with calculations and descriptions
* <i>Movie_Recommendation_System_Notebook.py</i> - console application to run in the terminal
* <i>MoviePairSimilarities</i> - folder contains serialized movie pair similarities RDD
* <i>movieNameDict.pickle</i> - serialized lookup table of movie names
* <i>movieList.pickle</i> - serialized list of avaiable movie to rate in console application
* <i>extract_available_movies.py</i> - script to create list of available movies to rate
* <i>ml-latest-small</i> - folder contains datasets
