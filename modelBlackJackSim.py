import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import seaborn as sns
from ModelDesision import model_decision
import tensorflow as tf
new_model = tf.keras.models.load_model('basic_model_highlow.keras')

def modelBlackJackSim(num_decks = 6, num_players = 4, num_chips = 100):
    card_types = ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']
    card_counting_dict = {'A': -1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 0, 8: 0, 9: 0, 10: -1, "J": -1, "Q": -1, "K": -1}

    def make_shoe(num_decks, card_types):
        new_shoe = []
        for i in range(num_decks):
            for j in range(4):
                new_shoe.extend(card_types)
        #Shuffle the cards
        random.shuffle(new_shoe)
        return new_shoe

    def calculateCount(cards_delt):
        current_count = 0
        num_cards_taken = 0
        total_decks = num_decks
        for key in cards_delt:
            current_count += card_counting_dict[key] * cards_delt[key]
            num_cards_taken += cards_delt[key]
        num_decks_left = (total_decks - (num_cards_taken // 52))
        return current_count // num_decks_left 
    
    def find_total(hand):
        face_cards = ['J', 'Q', 'K']
        aces = 0
        hand_value = 0
        # a card will either be a face card, an ace, or an int
        #for a face card add 10, for an int add the int value, for ace count it
        # and determine its impact on the hand value at the end
        for card in hand:
            if card == 'A':
                aces += 1
            elif card in face_cards:
                hand_value += 10
            else: 
                hand_value += card
        # at this point we can determine the value in the hand with the aces
        if aces == 0:
            return hand_value
        else:
            hand_value += aces
            if hand_value + 10 < 22:
                return (hand_value + 10)
            else:
                return hand_value
            
    def play_hand(dealer_hand, player_hands, curr_player_results, shoe, card_count, player_chips):
        dealer_bust = []
        #first, check if the dealer has blackjack.  that can only happen if the dealer has a total of 21, logically, and 
        #the game will be over before it really gets started...the players cannot hit
        if (len(dealer_hand) == 2) and (find_total(dealer_hand) == 21):
            for player in range(num_players):
                #check if any of the players also have blackjack, if so, they tie, and if not, they lose
                if (len(player_hands[player]) == 2) and (find_total(player_hands[player]) == 21):
                    curr_player_results[0, player] = 0
                else:
                    curr_player_results[0, player] = -1    
        
        #now each player can make their decisions...first, they should check if they have blackjack
        #for this player strategy, the decision to hit or stay is random if the total value is less than 12...
        #so it is somewhat unrelated to the cards they actually have been dealt (and is conservative), and ignores the card 
        #that the dealer has.  We will use this strategy to generate training data for a neural network.  
        #your job will be to improve this strategy, incorporate the dealer's revealed card, train a new neural
        #network based on that simulated data, and then compare the results of your neural network to the baseline
        #model generated from this training data.
        else:
            for player in range(num_players):
                #the default is that they do not hit
                num_hits = 0
                current_count = calculateCount(card_count)
                
                #check for blackjack so that the player wins
                if (len(player_hands[player]) == 2) and (find_total(player_hands[player]) == 21):
                    curr_player_results[0, player] = 1

                else:
                   # Can input different simualtions into this while loop
                    while model_decision(new_model, find_total([dealer_hand[1]]), find_total(player_hands[player]), current_count, num_hits) :
                        #deal a card
                        player_hands[player].append(shoe.pop(0))
                        
                        #update our dictionary to include the new card
                        card_count[player_hands[player][-1]] += 1
                        
                        #note that the player decided to hit
                        num_hits += 1
                        #get the new value of the current hand regardless of if they bust or are still in the game
                        #we will track the value of the hand during play...it was initially set up in the section below,
                        #and we are just updating it if the player decides to hit, so that it changes
                        live_total.append(find_total(player_hands[player]))                      
                            
                        #if the player goes bust, we need to stop this nonsense and enter the loss...
                        #we will record their hand value outside of the while loop once we know the player is done
                        if find_total(player_hands[player]) > 21:
                            curr_player_results[0, player] = -1
                            break
                        
        #next, the dealer takes their turn based on the rules
        #first, the dealer will turn over their card, so we can count it and update our dictionary; this is the FIRST card they were dealt
        card_count[dealer_hand[0]] += 1
        
        while find_total(dealer_hand) < 17:
            #the dealer takes a card
            dealer_hand.append(shoe.pop(0))    
            
            #update our dictionary for counting cards
            card_count[dealer_hand[-1]] += 1
        
        
        #this round is now complete, so we can determine the outcome...first, determine if the dealer went bust
        if  find_total(dealer_hand) > 21:
            
            #the dealer went bust, so we can append that to our tracking of when the dealer goes bust
            #we'll have to track the player outcomes differently, because if the dealer goes bust, a player
            #doesn't necessarily win or lose
            dealer_bust.append(1)
            
            #every player that has not busted wins
            for player in range(num_players):
                if curr_player_results[0, player] != -1:
                    curr_player_results[0, player] = 1
        else:
            #the dealer did not bust
            dealer_bust.append(0)
            
            #check if a player has a higher hand value than the dealer...if so, they win, and if not, they lose
            #ties result in a 0; for our neural network, we may want to lump ties with wins if we want a binary outcome
            for player in range(num_players):
                if find_total(player_hands[player]) > find_total(dealer_hand):
                    if find_total(player_hands[player]) < 22:
                        curr_player_results[0, player] = 1
                elif find_total(player_hands[player]) == find_total(dealer_hand):
                    curr_player_results[0, player] = 0
                else:
                    curr_player_results[0, player] = -1    
        
        #the hand is now complete, so we can return the results
        #we will return the results for each player
        return curr_player_results, card_count
#######################################################################################################
    player_chips = []

    player_num_hands = []
    final_player_num_hands=[]
    for i in range(num_players):
        player_chips.append(num_chips)
        player_num_hands.append(0) 
    
    while len(player_chips):
        #Make the shoe of cards
        shoe = make_shoe(num_decks, card_types)
        #Make the dictonary for the card count
        card_count = {'A':0, 2:0, 3:0, 4:0, 5:0, 6:0,7:0, 8:0, 9:0, 10:0, 'J':0, 'Q':0, 'K':0}
        while len(shoe) > 40:
            if not len(player_chips):
                break

            curr_player_results = np.zeros((1, num_players))
            
            #create the lists for the dealer and player hands
            dealer_hand = []
            player_hands = [ [] for player in range(num_players)]
            live_total = []

            #deal the FIRST card to all players and update our card counting dictionary
            for player, hand in enumerate(player_hands):
                player_hands[player].append(shoe.pop(0))
                card_count[player_hands[player][-1]] += 1
                
            #dealer gets a card, and the card counting dictionary is NOT updated
            dealer_hand.append(shoe.pop(0))
            card_count[dealer_hand[-1]] += 1
            
            #deal the SECOND card to all players and update our card counting dictionary
            for player, hand in enumerate(player_hands):
                player_hands[player].append(shoe.pop(0))
                card_count[player_hands[player][-1]] += 1
                
            #the dealer gets a card, and our card counter will be updated with the card that is showing
            dealer_hand.append(shoe.pop(0))
            card_count[dealer_hand[-1]] += 1

            live_total.append(find_total(player_hands[player]))
            player_results, card_count = play_hand(dealer_hand, player_hands, curr_player_results, shoe, card_count, player_chips)

            for i in range(num_players):
                if player_results[0,i] == -1:
                    player_chips[i] -= 1
                elif player_results[0, i] == 1:
                    player_chips[i] += 1

            deleted = []
            for i in range(len(player_chips)):
                if player_chips[i] != 0:
                    player_num_hands[i] += 1
                else:
                    final_player_num_hands.append(player_num_hands[i])
                    deleted.append(i)
                    num_players -= 1
            for i in deleted:
                player_chips.pop(i)
                player_num_hands.pop(i)
                    
                
            print(player_num_hands)
            print(player_chips)

    print(final_player_num_hands)

        

modelBlackJackSim(num_decks = 6, num_players = 4, num_chips = 20)