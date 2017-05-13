from operator import itemgetter
from kdtreematej import KDTree
from pymongo import MongoClient
import random


#CONSTANTS
NUM_OF_USERS = 20
NUM_OF_GENRES = 9
MAX_SHOWS = 10    		#Max amount of shows to recommend. And number of shows per user
NUM_OF_NEIGHBORS = 5    #Max amount of nearest neighbors




#This connects to the MongoDB client on the default host and port
client = MongoClient()

usersDatabase = client.test #Creates a database to store users
tvShowsDatabase = client.test #Creates a database to store TV Shows




#class RecommendationSystem():
#For some reason, when I added the class definition, my function calling was getting messed up.
#Same with the main.



#This method here defines the Singleton Design Pattern. It defines an instance of the class and returns it.
def instance(cls, *args, **kwgs):
	if not hasattr(cls, "_instance"):
 		cls._instance = cls(*args, **kwgs)
 	return cls._instance



#Reads a text file of user information separated by commas and posts it to the database
#Each line contains name, age, gender, occupation, userID, genrePreferences(dictionary), and tvShows(list)
def readUserFile():

	#I used "with" because that automatically closes the file after reading from it
	with open("userinformationrs.txt", "r") as userFile:
		for line in userFile:
 			userLine = line.split(",")		#splits every item by using a comma as the dilimeter. Stores it into a list called userLine

 			#Stores each portion of the line in a dictionary called 'user'
			user = {"name": userLine[0],
					"age": userLine[1],
					"gender": userLine[2],
					"occupation": userLine[3],
					"userID": userLine[4],
					"genrePreferences": {"Action": userLine[5], "Drama": userLine[6], "Comedy": userLine[7], "Thriller": userLine[8], "Horror": userLine[9], "Childrens": userLine[10], "Documentary": userLine[11], "News": userLine[12], "Reality": userLine[13]},
					"tvShows": [userLine[14], userLine[15], userLine[16], userLine[17], userLine[18], userLine[19], userLine[20], userLine[21], userLine[22], userLine[23]]
					}

			#inserts the user into the usersDatabase
			usersDatabase.theUsers.insert_one(user)



#Reads a text file of tv show information separated by commas and posts it to the database
#The information contains the title of the tv show followed by the genre
def readTVShowsFile():

	with open("tvshowsinformationrs.txt", "r") as tvShowFile:
		for line in tvShowFile:
			tvShowLine = line.split(",")

			#Stores each portion of the line in a dictionary called 'tvShow'
			tvShow = {"title": tvShowLine[0],
					  "genre": tvShowLine[1]}

			#inserts the TV Show into the tvShowsDatabase
			tvShowPost = tvShowsDatabase.theShows.insert_one(tvShow)



#This method creates the list of points to be used in the kd-tree. It takes in a list of points. Returns a two-dimensional list of points.
def createData(userPoints):

	data = []

	for d in range(NUM_OF_USERS):
		
		data.append(userPoints[d])


	return data



#This function creates a list of users from the list of points passed in
def findNearestNeigbors(nearestPoints):

	nearestNeighbors = list(xrange(NUM_OF_NEIGHBORS))

	#Iterates through the usersDatabase and finds the user with a matching userID from the list of points passed in
	for p in range(len(nearestPoints)):
		nearestNeighbors[p] = usersDatabase.theUsers.find_one({"userID": nearestPoints[p][3]})
	
	return nearestNeighbors



#This function checks the ratings of a chosen user's genre preferences (a dictionary that is passed in).
#If they are 3 or 2, then the genre is added to a list. That list is returned.
def findChosenUserGenrePreferences(genrePref):

	chosenGenres = list(xrange(NUM_OF_GENRES))
	g = 0

	for key in genrePref:
		if (genrePref[key] == 3) or (genrePref[key] == 2):
 			chosenGenres[g] = key
 			g = g + 1

	return chosenGenres



#This function creates points of users.
#Creates a kd-tree.
#Then finds shows to recommend and prints them out.
def recommendShows():

	c = 0
	m = 0
	r = 0
	i = 0

	#The list of TV Shows of the nearest neighbors.
	listOfNeighborTVShows = list(xrange(MAX_SHOWS))
		
	#The list of final shows to recommend.
	recommendedShows = list(xrange(MAX_SHOWS))

	#The list of genres that the chosen user rated a 3 or 2.
	listOfCandidateGenres = list(xrange(NUM_OF_GENRES))

	#The list of nearest neighbors
	nearestNeighbors = list(xrange(NUM_OF_NEIGHBORS))

	#The list of points to be put in the kd-tree. Taken from the userDatabase.
	userPoints = list(xrange(20))


 	
 	#The file reading functions are called.
 	readUserFile()
 	readTVShowsFile()


 	#Referencing usersDatabase.posts stores a big list of dictionaries of users that were inserted in the database. Same with tvShowDatabase.posts.
 	userPosts = usersDatabase.posts
 	tvShowPosts = tvShowsDatabase.posts


 	#This loop goes through all the userPosts and calls the find() method that is built into pymongo.
 	#This method finds all of the user dictionaries and places the values of each of the keys (age, gender, occupation, and userID) into the userPoints list.
 	for uPost in userPosts.find():
 		userPoints[a] = [ uPost["age"], uPost["gender"], uPost["occupation"], uPost["userID"] ] 	#puts a list of points in here based on the find() method of pymongo


 	#This calls the createData() function and passes in the userPoints. It is saved in a variable called treeData.
 	treeData = createData(userPoints)


 	#Chooes a random user from the treeData
	chosenUser = random.choice(treeData)

	#This creates a point of the chosen user.
	chosenUserPoint = [chosenUser[1],chosenUser[2], chosenUser[3], chosenUser[4]]


 	#This creates a tree from the tree data using the KDTree.construct_from_data() method.
	theTree = KDTree.construct_from_data(treeData)


	#This queries the tree for the nearest neighbors to the chosenUserPoint.
	#Returns a list of 5 points. These points represent the nearest neighbors.
	#It returns a list of points. That is saved to the variable called nearest.
	nearestPoints = theTree.query(chosenUserPoint, t=NUM_OF_NEIGHBORS)


	#This calls the findNearestNeighbors() method which returns a list of users with all attributes.
	nearestNeighbors = findNearestNeigbors(nearestPoints)


	#This calls the findChosenUserGenrePreferences() method. It passes in the chosenUser[5] because that is the index where the genrePreferences dictionaries are in each user.
	listOfCandidateGenres = findChosenUserGenrePreferences(chosenUser[5])
	
	

	#This prints the name of the Chosen User.
	#It uses the find() method again and searches for the name of the user whose userID is in the 4th index of the chosenUser variable.
 	print "Here are the Recommended Shows for %s:\n" % usersDatabase.theUsers.find( {"userID": chosenUser[4]}, {"name": 1, _id: 0})


	#This loop goes through each nearest neighbor and recommends shows whose genres match the chosen user's genre preferences.
 	for neighbor in nearestNeighbors:

 	  	#This for loop finds the tv shows of the nearest neighbor. This uses the find() method.
 	  	for i in range(MAX_SHOWS):
			listOfNeighborTVShows[i] = usersDatabae.theUsers.find( {"userID": neighbor[3]}, {"tvShows": 1})
 

		#This while loop compares the listOfCandidateGenres with the genres of the listOfNeighborTVShows. If the genres match, then the TV Show is added to the list of recommendedShows.
 	 	while (m < MAX_SHOWS):
 	 		for c in range(0, len(listOfCandidateGenres)):
 	 			if (listOfCandidateGenres[c] == tvShowPosts.find({"title": listOfNeighborTVShows[0][m]}, {"genre": 1})):
 	 				recommendedShows[r] = listOfNeighborTVShows[0][m]
 	 				print recommendedShows[r]
 	 				r = r + 1
 	 				break
 	 		m = m + 1



#This is the main method that calls the recommendShows method.
def main():
    recommendShows()