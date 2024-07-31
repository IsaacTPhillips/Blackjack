#load a neural network model for blackjack

import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn.metrics as metrics
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense, LSTM, Flatten, Dropout
import tensorflow as tf


#let's load the model and continue our work...using the model to make cozmo's decisions
#your model_decision function should obviously include the features that you used to 
#determine the model output.  my feature list was relatively simple.

#first, load the model
new_model = tf.keras.models.load_model('basic_model.keras')

#we can verify that the model has the same summary info as the model that we saved previously.
print(new_model.summary())

#TODO: incorporate the model into the decision-making process for hitting/staying
def model_decision(model, player_value, dealer_card):
    #the output is what the correct decision should be (hit = 1, stay = 0)
    #we will feed in the dealer card, the player total, and that the player stays (hit = 0)...if it is
    #the right decision, the model should predict a value close to 0.  so, if the
    #model predicts a value higher than 0.5-ish, we should not stay...i.e. we should hit.
    #otherwise, we could have looked at things in terms of the player hitting...hit = 1:
    #if it the right decision then the model should also predict a value close to 1
    
    #we can allow for both actions (hit and stay) to get a better understanding the model's recommendations...
    #first, create a dictionary for our input information...the value in the key/value pairs are only
    #different for the action (hit or stay)...that's because I'm trying to explore what the predicted value
    #from the model means.
    
    d = {'dealer_card':[dealer_card], 'init_hand':[player_value], 'hit':[1]} 
    
    #now create a dataframe so we can run that information through our model... this is basically what
    #we will do when cozmo is playing...we need to get the information for the current round: the dealer's card,
    #what Cozmo has in its hand, and the two actions...hit or stay.  ideally we'll using just one action as the 
    #default (hit?) and base Cozmo's actions on the model's predicted output.
    input_df = pd.DataFrame(data=d)
    
    #run the data through the model
    prediction = model.predict(input_df)
    
    #at this stage, we want to know what the model predicted
    print(prediction)
    

    #now we can fine-tune our decision (hit or stay) based on the model's prediction
    if prediction > 0.54:
        return 1
    else:
        #we can be conservative here and just stay
        return 0
    
    return prediction

'''
d = {'dealer_card':[8, 10, 11], 'init_hand':[15, 12, 19], 'hit':[0,0,0]}   
input_df = pd.DataFrame(data=d)

predict_correct = new_model.predict(input_df)
print(predict_correct)
'''
action = ['stay', 'hit']
print(action[model_decision(new_model, 15, 8)])
print(action[model_decision(new_model, 17, 8)])
print(action[model_decision(new_model, 16, 10)])
print(action[model_decision(new_model, 11, 10)])
