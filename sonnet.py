#
# Generate markov poems based on Shakespeare
#
# Inspired by http://www.codinghorror.com/blog/2008/06/markov-and-you.html
# Based on http://uswaretech.com/blog/2009/06/pseudo-random-text-markov-chains-python/
# Shakespeare Sonnet Source http://www.gutenberg.org/cache/epub/1041/pg1041.txt
#
import logging, math, random, sys

# Configure basic logging
logging.basicConfig(level=logging.WARNING)
log = logging.getLogger('markov')

def read_file(filename):
	"""Reads the specified filename and emits a list of words.

	This method keeps the newline at the ends of words intact 
	and skips lines unless they have more than one word on them.
	@param filename - the name of the file to read
	"""
	words = []
	with open(filename,'r') as f:
		for line in f.readlines():
			tmp = line.split()
			if len(tmp) > 1:
				tmp[-1] = tmp[-1] + '\n'
				words.extend(tmp)
	return words
		
def generate_chain(words, chain_length=3):
	"""Yields the chains based on word sequence.

		@param words - the list of words to examine
		@chain_length is the length of chain to consider
	"""
	# range over all words from 0...N-chain_length
	# offset by one to be inclusive for python range
	for i in range(len(words) - chain_length + 1):
		yield words[i:i+chain_length]

def create_database(words, chain_length=3):
	"""Creates the database for looking up next words based on chains
	
		@param words - the sequence of words to store
		@param chain_length - the length of the key chain to use
	"""
	db = {}
	for chain in generate_chain(words, chain_length):
		key = tuple(chain[:-1])
		if key in db:
			# append the next word in the sequence
			# duplicates just increase probability of selection
			# with this structure
			db[key].append(chain[-1])
		else:
			# start a new list for the key
			db[key] = [chain[-1]]
	return db

def do_markov(words, db, chain_length, size=13):
	"""Uses the word database generate a markov text.  This implementation
	uses number of line generated instead of number of words in order to
	give a more 'poemish' look to the output.
	
		@param words - the sequence of words	
		@param db - the chain sequence lookup dataabase
		@param chain_length - the size of chains in the database
		@param size - the number of lines to generate
	"""
	def random_word():
		"""Helper function for picking a random start point"""
		seed = random.randint(0,len(words)-chain_length)
		start = words[seed:seed + chain_length - 1]
		return start

	start = random_word()
	generated = []
	current = 0
	while current < size:
		log.debug("CURRENT LINE: %d" , current)
		log.debug("Start is : %s", start)

		generated.append(start[0])

		# We need this to handle scenarios where we reached the end
		# of an input sequence and could not find a matching chain.
		# We just select a new random starting point and continue
		# until we succeed.
		while True:
			try:
				next_word = random.choice(db[tuple(start)])
				break
			except KeyError:
				log.debug("Got key error with: %s",start)
				start = random_word()

		start = start[1:]
		start.append(next_word)
		if next_word.endswith('\n'):
			current += 1

	# Write out our last looked up word, then return everything
	# as a single string
	generated.append(next_word)
	return ' '.join(generated)


def db_stats(db):
	"""Calculate database statistics"""
	num_keys = len(db.keys())

	min_len = sys.maxint
	max_len = 0
	num_options = 0
	tmp_len = 0
	for key in db:
		tmp_len = len(db[key])
		num_options += tmp_len
		if tmp_len > max_len: max_len = tmp_len
		if tmp_len < min_len: min_len = tmp_len
	avg_options = float(num_options) / float(num_keys)

	sum_squares = 0.0
	for key in db:
		diff = (len(db[key]) - avg_options)**2
		sum_squares += diff

	print("Number of key tuples: %d" % num_keys)
	print("Mean Choices:         %f" % avg_options)
	print("Min Choices:          %d" % min_len)
	print("Max Choices:          %d" % max_len)
	print("Sum of Squares:       %f" % sum_squares)
	print("Standard Deviation:   %f" % math.sqrt(sum_squares))
		
if __name__ == '__main__':
	log.info("Starting Markov")
	#random.seed(1)
	chain_length = 3
	gensize = 13
	
	filename = 'shakespeare_sonnet.txt'

	# Read words from input file
	words = read_file('shakespeare_sonnet.txt')

	db = create_database(words, chain_length)

	for k in db:
		log.debug("[%s] : %s", k, db[k])

	# Generate text
	text = do_markov(words, db, chain_length, gensize)
	print("*"*40)
	print("Generated Text")
	print("*"*40)
	print(text)

	# Display Statistics
	db_stats(db)
	log.info("Finished Markov")
