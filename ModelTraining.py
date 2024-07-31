

import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn.metrics as metrics
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense, LSTM, Flatten, Dropout



#Now we can train a neural net to play blackjack and evaluate the model
#let's load the csv file that we created in the last script
final_df = pd.read_csv('blackjackdata.csv')

#let's get an idea of what the dataframe looks like
print(final_df.info())

#first, determine the features to include.  i will include the dealer card that is showing, the 
#cards that the player has been dealt, and whether the player hit or not.  I will not include card
#counting, or an awareness of the number of players at the table or the number of decks of cards
#in the shoe.  That might be something that you include in your model.

feature_list = ['dealer_card','init_hand','hit', 'true_count']

#i need to address the problem of the dealer card being numberical and string data.
#i want the dealer card to be numerical in nature, so I'll use the replace method
#and do this in place.  If you wonder what that means, try not using that attribute
#or setting it to be False
final_df['dealer_card'].replace({'A':11, 'J':10, 'Q':10, 'K':10}, inplace=True)

#to build the model, i need to extract the information in my feature list (omitting 
#unnecessary features as well as the label, or the attribute that I want my model to predict
#make sure that the data is in a form that con be converted to a tensor...

#X_df = final_df[feature_list]
X_df = np.array(final_df[feature_list]).astype(np.float32)

#given the dealer card, the player's hand, and their action (hit or stay) was that the correct choice?
#for my model predition, i will default to my input being the dealer card, the player's hand, and they hit
#the question will be was it the correct decision.  if so, then cozmo should hit.  if not, then cozmo should stay.
#again, your reasoning might be different.  again, make sure that your data is in a form that can
#be converted to a tensor

#y_df = final_df['outcome']
y_df = np.array(final_df['outcome']).astype(np.float32).reshape(-1,1)

#next, break up the data into trining data and testing data...20% of the data will be used to evaluate
#the model, and 80% of the data will be used to train the model.  You can change these parameters
#to explore the impact.  we are using the train_test_split method we imported.
X_train, X_test, y_train, y_test = train_test_split(X_df, y_df, test_size = 0.2)


'''
we will set up a neural net with 5 layers, each layer will have a different number of nodes
again, play with these parameters to see if there is an impact on the accuracy of the model.
be curious about these parameters!  
  
https://keras.io/guides/sequential_model/

In a neural network, the activation function is responsible for transforming the summed weighted input 
from the node into the activation of the node or output for that input.

The rectified linear activation function or ReLU for short is a piecewise linear function that will output 
the input directly if it is positive, otherwise, it will output zero. It has become the default activation f
unction for many types of neural networks because a model that uses it is easier to train and often achieves better performance.

The sigmoid and hyperbolic tangent activation functions cannot be used in networks with many layers due to the vanishing gradient problem.
The rectified linear activation function overcomes the vanishing gradient problem, allowing models to learn faster and perform better.
The rectified linear activation is the default activation when developing multilayer Perceptron and convolutional neural networks.

play with the different activation functions.

An epoch is a single iteration through the training data.  The more epochs, the more the model is trained.  Be careful not to overfit
the data.  Of course, there are a finite number of dealer card/player hands to consider...so what would it mean to overfit the data?
'''

model = Sequential()
model.add(Dense(16, activation='relu'))
model.add(Dense(128))
model.add(Dense(32, activation='softmax'))
model.add(Dense(8))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='sgd')

#train the model
model.fit(X_train, y_train, epochs=20, batch_size=256, verbose=1)

#make some predictions based on the test data that we reserved
pred_Y_test = model.predict(X_test)
#also get the actual results so we can compare
actuals = y_test

#evaluate the model...check out the vaerious metrics used to evaluate a model...you can do your own search
#   https://neptune.ai/blog/performance-metrics-in-machine-learning-complete-guide

fpr, tpr, threshold = metrics.roc_curve(actuals, pred_Y_test)
roc_auc = metrics.auc(fpr, tpr)

fig, ax = plt.subplots(figsize=(10,8))
plt.plot(fpr, tpr, label = ('ROC AUC = %0.3f' % roc_auc))

plt.legend(loc = 'lower right')
plt.plot([0,1], [0,1], 'r--')
plt.xlim([0,1])
plt.ylim([0,1])
ax.set_xlabel('False Positive Rate', fontsize=16)
ax.set_ylabel('True Positive Rate', fontsize=16)
plt.setp(ax.get_legend().get_texts(), fontsize=16)
plt.tight_layout()
plt.savefig(fname='roc_curve_blackjack', dpi=150)
plt.show()

    # Assuming pred_Y_test contains continuous probabilities
thresholds = []
for i in range(35, 60):
    thresholds.append(i / 100)

accuracy_threshold = []  # Replace with your actual accuracy data
for thres in thresholds:
    binary_pred_Y_test = (pred_Y_test >= thres).astype(int)
        # Assuming actuals are binary (0 or 1)

        # Assuming actuals and binary_pred_Y_test are set correctly 
    accuracy = metrics.accuracy_score(actuals, binary_pred_Y_test) * 100
    accuracy_threshold.append(accuracy)

max_accuracy = max(accuracy_threshold)
min_accuracy = min(accuracy_threshold)

# Create an array of x values for the line plot
x = np.arange(len(thresholds))
# Create a line plot
plt.plot(x, accuracy_threshold, marker='o', linestyle='-', color='b')

# Set the x-axis labels
plt.xticks(x, thresholds)

# Set axis labels and chart title
plt.xlabel('Threshold')
plt.ylabel('Percent')
plt.ylim(min(accuracy_threshold) - 5, max(accuracy_threshold) + 5)
plt.title('Percent accurate')

# Add the maximum and minimum values as labels
plt.text(x[accuracy_threshold.index(max_accuracy)], max_accuracy + 1, f'{max_accuracy:.2f}%', ha='center', va='bottom')
plt.text(x[accuracy_threshold.index(min_accuracy)], min_accuracy - 1, f'{min_accuracy:.2f}%', ha='center', va='top')

plt.scatter(x[accuracy_threshold.index(max_accuracy)], max_accuracy, color='red', marker='*', s=100, label=f'Max: {max_accuracy:.2f}%')


plt.show()
max_index = accuracy_threshold.index(max(accuracy_threshold))
binary_pred_Y_test = (pred_Y_test >= thresholds[max_index]).astype(int)
conf_matrix = confusion_matrix(actuals, binary_pred_Y_test)

plt.figure(figsize=(6, 4))
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Reds", linewidths=.5)
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()

print(model.summary())

#we an save the model and then load it to continue where we left off
model.save('basic_model.keras')


#NEXT: use the model to determine cozmo's course of action
