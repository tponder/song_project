'''
This file can be used to create topics models for the songs.

PLSA algorithm is used. Vanilla PLSA does not work well for
this task. Since we are interested in certain topics that
songs may be about, there are slight modificationsto the
vanilla PLSA to steer the algorithm towards topics.

This is done by defining pre-defining topics with words that
you believe will be correlated. The PLSA algorithm then
initializes topic models to start close to these distributions,
and extra word counts are injected into the model during the
M-step.

This article was used to help determine topics:
https://journals.sagepub.com/doi/full/10.1177/0305735617748205

The terms associated with topics were hand-picked.
'''

import numpy as np
import math
import metapy
import time


def normalize(input_matrix, sum_to=[]):
    """
    Normalizes the rows of a 2d input_matrix so they sum to X. With the sum_to
    variable, you can set X for each row (0<=X<=1).
    """

    row_sums = input_matrix.sum(axis=1)
    assert (np.count_nonzero(row_sums)==np.shape(row_sums)[0]) # no row should sum to zero
    if len(sum_to) == 0:
        sum_to = np.ones(np.shape(row_sums[:, np.newaxis]))
    new_matrix = input_matrix / row_sums[:, np.newaxis] * sum_to
    return new_matrix

       
class Model(object):

    """
    Model topics from song lyrics.
    """

    def __init__(self, songs=[]):
        self.documents = songs
        self.vocabulary = []
        self.vocabulary_ind = {}
        self.likelihoods = []
        self.term_doc_matrix = None 
        self.document_topic_prob = None  # P(z | d)
        self.topic_word_prob = None  # P(w | z)
        self.topic_prob = None  # P(z | d, w)

        love_topic = {'love':0.2, 'heart':0.05, 'hate':0.025}
        sex_topic = {'sex':0.1, 'ass':0.05, 'pussi':0.05, 'dick':0.05}
        fun_times_topic = {'fun':0.05, 'danc':0.05, 'smile':0.05}
        drugs_topic = {'drug':0.05, 'drink':0.05, 'smoke':0.05, 'beer':0.05, 'drunk':0.05, 'high':0.05}
        christmas_topic = {'christmas':0.25, 'santa':0.15, 'tree':0.05, 'winter':0.05}
        sports_topic = {'sport':0.1, 'basketbal':0.05, 'basebal':0.05, 'hoop':0.05, 'nba':0.05}
        religious_topic = {'god':0.2, 'bibl':0.1, 'heaven':0.05}
        wealth_topic = {'money':0.2, 'rich':0.1}
        free_topic = {'other':0.0}
        self.topic_names = ['Love', 'Sex', 'Fun', 'Drugs', 'Christmas', 'Sports', 'Religion', 'Wealth', 'Other']
        self.topic_priors = [love_topic,sex_topic,fun_times_topic,drugs_topic,christmas_topic,sports_topic,religious_topic,wealth_topic,free_topic]
        
        self.number_of_topics = len(self.topic_priors)
        self.number_of_documents = len(self.documents)
        self.vocabulary_size = 0


    def set_songs_from_file(self, documents_path):
        """
        Gathers lyrics from a file containing song lyrics.
        """
        
        f = open(documents_path,'r')
        lines = f.readlines()
        f.close()
        self.documents = [lines[x] for x in range(5, len(lines), 7)]
        self.number_of_documents = len(self.documents)
        

    def build_vocabulary(self):
        """
        Builds a vocabulary from all songs available.
        """
        
        i = 0
        ana = metapy.analyzers.load('config/config.toml')
        doc = metapy.index.Document()
        for document in self.documents:
            doc.content(document)
            words = ana.analyze(doc)
            for word in words:
                if not word in self.vocabulary_ind:
                    self.vocabulary_ind[word] = i
                    self.vocabulary.append(word)
                    i += 1
        self.vocabulary_size = len(self.vocabulary)


    def build_term_doc_matrix(self):
        """
        Construct the term-document matrix where each row represents a song, 
        and each column represents a vocabulary term.
        """
        
        self.number_of_documents = len(self.documents)

        ana = metapy.analyzers.load('config/config.toml')
        doc = metapy.index.Document()
        self.term_doc_matrix = np.zeros((self.number_of_documents, self.vocabulary_size))
        for i in range(self.number_of_documents):
            doc.content(self.documents[i])
            words = ana.analyze(doc)
            for word in words:
                self.term_doc_matrix[i][self.vocabulary_ind[word]] = words[word]
        

    def initialize(self, number_of_topics):
        """
        Initializes the model. Topics start closer to the priors.
        """
        
        self.document_topic_prob = np.random.random((self.number_of_documents, number_of_topics))
        self.document_topic_prob = normalize(self.document_topic_prob)
        
        prior_weights = []
        if self.topic_priors:
            for topic in self.topic_priors:
                prior_weights.append(1-sum(topic.values()))
        prior_weights = np.transpose(np.array([prior_weights]))*2
        if self.topic_priors:
            self.topic_word_prob = np.random.random((number_of_topics, len(self.vocabulary)))
            for i in range(len(self.topic_priors)):
                for word in self.topic_priors[i]:
                    self.topic_word_prob[i][self.vocabulary_ind[word]] += self.topic_priors[i][word]*1000
        else:
            self.topic_word_prob = np.random.random((number_of_topics, len(self.vocabulary)))

        self.topic_word_prob = normalize(self.topic_word_prob)
        

    def expectation_step(self):
        """ The E-step updates P(z | w, d)
        """
        
        self.topic_prob = np.zeros([self.number_of_documents, self.number_of_topics, self.vocabulary_size], dtype=np.float)
        for i in range(self.number_of_topics):
            a = np.transpose(np.array([self.document_topic_prob[:,i]]))
            b = np.array([self.topic_word_prob[i,:]])
            self.topic_prob[:,i,:] = np.matmul(a,b)
        row_sums = self.topic_prob.sum(axis=1)
        assert (np.count_nonzero(row_sums)==np.shape(row_sums)[0]*np.shape(row_sums)[1])
        self.topic_prob = self.topic_prob / row_sums[:,np.newaxis,:]
            

    def maximization_step(self, number_of_topics):
        """ The M-step updates P(w | z)
        """
        
        mat = np.zeros([self.number_of_documents, self.number_of_topics, self.vocabulary_size], dtype=np.float)
        for i in range(self.number_of_topics):
            mat[:,i,:] = np.multiply(self.topic_prob[:,i,:], self.term_doc_matrix)
        
        # update P(z | d)
        self.document_topic_prob = mat.sum(axis=2)
        self.document_topic_prob = normalize(self.document_topic_prob)
        
        # update P(w | z)
        self.topic_word_prob = mat.sum(axis=0)
        prior_weights = []
        if self.topic_priors:
            for topic in self.topic_priors:
                prior_weights.append(1-sum(topic.values()))
        prior_weights = np.transpose(np.array([prior_weights]))
        self.topic_word_prob = normalize(self.topic_word_prob, prior_weights)
        if self.topic_priors:
            for i in range(len(self.topic_priors)):
                for word in self.topic_priors[i]:
                    self.topic_word_prob[i][self.vocabulary_ind[word]] += self.topic_priors[i][word]
        

    def calculate_likelihood(self, number_of_topics):
        """
        Calculates the current log-likelihood of the model using
        the model's updated probability matrices
        """
        
        a = np.matmul(self.document_topic_prob, self.topic_word_prob)
        return sum(sum(np.multiply(np.log(a),self.term_doc_matrix)))


    def plsa(self, max_iter, epsilon, time_cutoff):
        """
        Model topics.
        """

        # build the vocabulary
        self.build_vocabulary()

        # build term-doc matrix
        self.build_term_doc_matrix()
        
        # Create the counter arrays.
        
        # P(z | d, w)
        self.topic_prob = np.zeros([self.number_of_documents, self.number_of_topics, self.vocabulary_size], dtype=np.float)

        # P(z | d) P(w | z)
        self.initialize(self.number_of_topics)

        # Run the EM algorithm
        current_likelihood = -float('inf')

        starttime = time.time()
        
        for iteration in range(max_iter):
            print("Iteration #" + str(iteration + 1) + "...")
            
            self.expectation_step()
            self.maximization_step(self.number_of_topics)
            old_likelihood = current_likelihood
            current_likelihood = self.calculate_likelihood(self.number_of_topics)
            if current_likelihood - old_likelihood < epsilon:
                break
            if time.time()-starttime > time_cutoff:
                break
    

    def load_model(self):
        pass


    def save_model(self,outfile):
        f = open(outfile, 'w')
        top_models = []
        for topic in self.topic_word_prob:
            model = list(zip(self.vocabulary, topic))
            model = sorted(model, key=lambda x: -x[1])
            top_models.append('; '.join([f'{x[0]}:{x[1]}' for x in model]))
        f.write('\n\n'.join(top_models))
        f.close()


    def songs_topics_strlist(self):
        docs_topics_list = []
        for doc in self.document_topic_prob:
            doc_topics = []
            for i in range(self.number_of_topics):
                if doc[i] > 0.2:
                    doc_topics.append(self.topic_names[i])
            doc_topics = '/'.join(doc_topics)
            if doc_topics == '':
                doc_topics = 'n/a'
            docs_topics_list.append(doc_topics)
        return docs_topics_list


    def topics_from_new_song(self):
        pass