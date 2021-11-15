import matplotlib.pyplot as plt
from random import randint,choices ##### choices is a function available from python 3.6 onwards


PARITY_CHECK_M = [[0,0,1],[0,1,0],[0,1,1],[1,0,0],[1,0,1],[1,1,0],[1,1,1]]
LEN = 10000
NUM_OF_CODEWORDS = 16
NUM_OF_MESSAGE_BITS = 4
N = 7
CODE_WORDS = []

"""
define helper functions here
"""
def convert_int_to_bin(i):
    res = ''
    while i != 0:
        res += str(i%2)
        i //= 2

    if len(res) < NUM_OF_MESSAGE_BITS:
        return (NUM_OF_MESSAGE_BITS - len(res)) * '0' + res[::-1]
    return res[::-1]



#### Converts a 4 bit message to the appropriate codeword
def convert_message_to_codeword(message):
    assert(len(message) == NUM_OF_MESSAGE_BITS)
    p1 = (int(message[1]) + int(message[2]) + int(message[3])) % 2
    p2 = (int(message[0]) + int(message[2]) + int(message[3])) % 2
    p3 = (int(message[0]) + int(message[1]) + int(message[3])) % 2
    return message + str(p1) + str(p2) + str(p3)



### Initializes the CODE_WORDS list based on 4 bit message
def init_codewords():
    for i in range(NUM_OF_CODEWORDS):
        message = convert_int_to_bin(i)
        CODE_WORDS.append(convert_message_to_codeword(message))


### calculates the distance between 7 bit words
def code_word_distance(word1,word2):
    assert(len(word1) == N and len(word2)== N)
    distance = 0
    for j in range(N):
        if word1[j] != word2[j]:
            distance += 1
    return distance








    
    



class Hamming_743(object):
    '''
    To model the binary symmetric channel I will use the function choices from random module
    (requires > python 3.6)
    for all the 7 bits , choose the bit with probability 1-p or flip it with probability p
    '''
    def bin_symmetric_channel(self,p,transm_word):
        received_word = ''
        assert(len(transm_word) == N)
        assert (0 <= p <= 1)
        
        for j in range(N):
            proper_bit,flipped_bit = int(transm_word[j]),1-int(transm_word[j])
            received_word += str(choices([proper_bit,flipped_bit],[(1-p),p])[0])
        return received_word

    '''
    Given a received word , it will return the codeword with the smallest distance 
    If the received word has no error or  1 error, this decoder corrects it otherwise it doesn't
    '''
    def decoder(self,received_word):
        assert(len(received_word) == N)
        distance_list = []
        assert(len(CODE_WORDS) == NUM_OF_CODEWORDS) ### has to be initialized properly before indexing

        for i in range(NUM_OF_CODEWORDS):
            distance_list.append(code_word_distance(received_word,CODE_WORDS[i]))
        return CODE_WORDS[distance_list.index(min(distance_list))]


    '''
    generates a message using 7 4 Hamming code

    It picks a code word from the given CODE_WORDS list
    The caller function will make sure that the codewords are 
    picked uniformly
    '''
    def codeword_from_message(self,index):
        assert(0 <= index <= NUM_OF_CODEWORDS - 1)
        assert(len(CODE_WORDS) == NUM_OF_CODEWORDS)
        return CODE_WORDS[index]
    
    '''
    calculates the probability of the undetected error
    of The 7 4 Hamming code
    according to the formula derived earlier
    '''
    def Pu(self,p):
        assert (0 <= p <= 1)
        weight_3_prob = N * (p ** (N - NUM_OF_MESSAGE_BITS)) * ((1 - p) ** NUM_OF_MESSAGE_BITS)
        weight_4_prob = N * (p ** NUM_OF_MESSAGE_BITS) * ((1 - p) ** (N - NUM_OF_MESSAGE_BITS))
        weight_7_prob = p ** N
        return weight_3_prob + weight_4_prob + weight_7_prob
    
    '''
    UNIFORMLY takes a codeword corresponding to a message
    and sends it through binary symmetric channel

    if received and transmitted words are different and received word is a codeword
    it will be undetected
    the probability will be calculated by dividing the count by 10000
    '''
    def empirical_undetected(self,p):
        assert (0 <= p <= 1)
        assert(len(CODE_WORDS) == NUM_OF_CODEWORDS)
        i = 0
        count = 0

        for _ in range(LEN):
            transm_word = self.codeword_from_message(i)
            received_word = self.bin_symmetric_channel(p,transm_word)
            
            if (received_word != transm_word and received_word in CODE_WORDS):
                count += 1
            i = (i + 1) % NUM_OF_CODEWORDS
        return count / LEN
    
    '''
    calculates the probability of detected and corrected
    according to the formula derived earlier
    '''
    
    def Pdc(self,p):
        return N * p * ((1-p) ** (N - 1))

    '''
    UNIFORMLY takes a codeword corresponding to a message
    and sends it through binary symmetric channel
    if the distance between the transmitted word and the received word is 1
    it will be detected and corrected
    the probability will be calculated by dividing the count by 10000
    '''

    def empirical_detected_corrected(self,p):
        assert (0 <= p <= 1)
        assert(len(CODE_WORDS) == NUM_OF_CODEWORDS)
        i = 0
        count = 0

        for _ in range(LEN):
            transm_word = self.codeword_from_message(i)
            received_word = self.bin_symmetric_channel(p,transm_word)
            
            if (code_word_distance(transm_word,received_word) == 1): ### if the word distance between transmitted and received is 1
                count += 1
            i = (i + 1) % NUM_OF_CODEWORDS
        return count / LEN
    
    '''
    calculates the probability of detected but  uncorrected
    according to the formula derived earlier
    '''
    def Pdu(self,p):
        return 1 - self.Pdc(p) - self.Pu(p) - ((1 - p)**7)

    '''
    UNIFORMLY takes a codeword corresponding to a message
    and sends it through binary symmetric channel
    and then decodes it
    if the estimated word and transmitted word are different and
    received word is not in the code words 
    it will be detected and uncorrected
    the probability will be calculated by dividing the count by 10000
    '''

    def empirical_detect_uncorrect(self,p):
        assert (0 <= p <= 1)
        assert(len(CODE_WORDS) == NUM_OF_CODEWORDS)
        i = 0
        count = 0

        for _ in range(LEN):
            transm_word = self.codeword_from_message(i)
            received_word = self.bin_symmetric_channel(p,transm_word)
            estimated_word = self.decoder(received_word)
            
            if ((estimated_word != transm_word) and (received_word not in CODE_WORDS) ): 
                count += 1
            i = (i + 1) % NUM_OF_CODEWORDS
        return count / LEN
    





### runs the first simulation

def run_undetected(sol):
    '''
      probability is from 10 ** -1 to  5 * 10 ** -1, with step 10 ** -1
    '''
    prob = [i*10**(-1) for i in range(1,6)] #### change this list to get different graphs
    undetected_p = []
    undetected_p_empirical = []
    
    for p in prob:
        undetected_p.append(sol.Pu(p))
        undetected_p_empirical.append(sol.empirical_undetected(p))

    plt.xscale("log")
    plt.yscale("log")
    plt.plot(prob,undetected_p)
    plt.plot(prob,undetected_p_empirical)
    plt.legend(["undetected prob to p", "undetected_empirical prob to p"])
    plt.show()


#### runs the second simulation
def run_detected_and_corrected(sol):
    '''
      probability is from 10 ** -1 to  5 * 10 ** -1, with step 10 ** -1
    '''
    prob = [ i*10**(-1) for i in range(1,6)] ### change these to get different graphs
    detected_corrected_p = []
    detected_corrected_empirical_p = []

    for p in prob:
        detected_corrected_p.append(sol.Pdc(p))
        detected_corrected_empirical_p.append(sol.empirical_detected_corrected(p))
    

    plt.xscale("log")
    plt.yscale("log")
    plt.plot(prob,detected_corrected_p)
    plt.plot(prob,detected_corrected_empirical_p)
    plt.legend(["detected and corrected prob to p", "detected_and corrected_empirical to p"])
    plt.show()



### run the third simulation
def run_detected_uncorrected(sol):
    '''
      probability is from 10 ** -1 to  5 * 10 ** -1, with step 10 ** -1
    '''
    prob = [ i*10**(-1) for i in range(1,6)] ### change these to get different graphs
    detected_uncorrected_p = []
    detected_uncorrected_empirical_p = []

    for p in prob:
        detected_uncorrected_p.append(sol.Pdu(p))
        detected_uncorrected_empirical_p.append(sol.empirical_detect_uncorrect(p))
    

    plt.xscale("log")
    plt.yscale("log")
    plt.plot(prob,detected_uncorrected_p)
    plt.plot(prob,detected_uncorrected_empirical_p)
    plt.legend(["detected and uncorrected prob to p", "detected_and uncorrected_empirical to p"])
    plt.show()

### run fourth simulation
def run_error_cases(sol):
    '''
      probability is from 10 ** -1 to  5 * 10 ** -1, with step 10 ** -1
    '''
    prob = [ i*10**(-1) for i in range(1,6)] ### change these to get different graphs
    error = []
    error_empirical_p = []

    for p in prob:
        error.append(sol.Pu(p) + sol.Pdu(p))
        error_empirical_p.append(sol.empirical_undetected(p) +  sol.empirical_detect_uncorrect(p))
    

    plt.xscale("log")
    plt.yscale("log")
    plt.plot(prob,error)
    plt.plot(prob,error_empirical_p)
    plt.legend(["error prob to p", "error empirical to p"])
    plt.show()



    



def main():
    init_codewords() ### initialize codewords at the end 
    sol = Hamming_743()
    #run_undetected(sol)
    #run_detected_and_corrected(sol)
    #run_detected_uncorrected(sol)
    run_error_cases(sol)




main()
