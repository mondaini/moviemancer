from recommendation.models import Movie, User, List, Rating, Rate, MovieList
import collections
from recommendation.queries import *
from math import sqrt
import tmdbsimple as tmdb

def getFacebookFriends(user_id):
    pass

def getSimilarProfiles(user_id):
    oneGenreSimilarity = User.objects.raw("SELECT user.user_ID FROM user INNER JOIN profile ON profile.user_id = user.user_id INNER JOIN profile_genre ON profile.profile_id = profile_genre.profile_id AND (profile_genre.genre_id = '1' OR profile_genre.genre_id = '5' OR profile_genre.genre_id = '13')")

    usersList = []
    similarUsers = []

    for user in oneGenreSimilarity:
        usersList.append(user.user_id)

    for item, count in collections.Counter(usersList).items():
        if count > 1:
            similarUsers.append(item)
            
    return similarUsers

def pearson_correlation(person1,person2):
    
	# To get both rated items
	both_rated = {}
	for item in get_movie_by_user(person1):
		if item in get_movie_by_user(person2):
			both_rated[item] = 1

	number_of_ratings = len(both_rated)		
	
	# Checking for number of ratings in common
	if number_of_ratings == 0:
		return 0

	# Add up all the preferences of each user
	person1_preferences_sum = sum([get_rates_by_movie(item, person1) for item in both_rated])
	person2_preferences_sum = sum([get_rates_by_movie(item, person2) for item in both_rated])

	# Sum up the squares of preferences of each user
	person1_square_preferences_sum = sum([pow(get_rates_by_movie(item, person1),2) for item in both_rated])
	person2_square_preferences_sum = sum([pow(get_rates_by_movie(item, person2),2) for item in both_rated])

	# Sum up the product value of both preferences for each item
	product_sum_of_both_users = sum([get_rates_by_movie(item, person1) * get_rates_by_movie(item, person2) for item in both_rated])

	# Calculate the pearson score
	numerator_value = product_sum_of_both_users - (person1_preferences_sum*person2_preferences_sum/number_of_ratings)
	denominator_value = sqrt((person1_square_preferences_sum - pow(person1_preferences_sum,2)/number_of_ratings) * (person2_square_preferences_sum -pow(person2_preferences_sum,2)/number_of_ratings))
	if denominator_value == 0:
		return 0
	else:
		r = numerator_value/denominator_value
		return r 

def most_similar_users(person,number_of_users):
	# returns the number_of_users (similar persons) for a given specific person.
	dataset = getSimilarProfiles(person)
	scores = [(pearson_correlation(person,other_person),other_person) for other_person in dataset if  other_person != person ]
	
	# Sort the similar persons so that highest scores person will appear at the first
	scores.sort()
	scores.reverse()
	return scores[0:number_of_users]

def user_reommendations(person):
	dataset = getSimilarProfiles(person)
	# Gets recommendations for a person by using a weighted average of every other user's rankings
	totals = {}
	simSums = {}
	rankings_list =[]
	for other in dataset:
		# don't compare me to myself
		if other == person:
			continue
		sim = pearson_correlation(person,other)

		# ignore scores of zero or lower
		if sim <=0: 
			continue
		for item in get_movie_by_user(other):

			# only score movies i haven't seen yet
			if item not in get_movie_by_user(person):

			# Similrity * score
				totals.setdefault(item,0)
				totals[item] += get_rates_by_movie(item, other)* sim
				# sum of similarities
				simSums.setdefault(item,0)
				simSums[item]+= sim

		# Create the normalized list

	rankings = [(total/simSums[item],item) for item,total in totals.items()]
	rankings.sort()
	rankings.reverse()
	# returns the recommended items
	recommendataions_list = [recommend_item for score,recommend_item in rankings]
	return recommendataions_list

def get_similar_movies(tmdb_movie_id):
    pass

def add_similar_movies_to_recommendation (movies):
    pass

def add_recommentation_to_database(user):
	recommendation = user_reommendations(user)
	list_id = get_list_by_user(user, 1)

	movies =[]

	for item in movie_by_user_list(user,'recommendation'):
		movies.append(item.movie_id)
   
	for item in recommendation:
		if item not in movies:
			reco = MovieList(movie_id=item, list_id=list_id)
			reco.save()