import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import seaborn as sns

#number of players to help calculate stats
num_players = 4

# Read the CSV file into a DataFrame
df = pd.read_csv('blackjackdata.csv')

def turn_string_to_list(value):
    return value.replace("[", '').replace(']', '').split(',')

# a function to create the rows
def split_data_per_player(row, index):
    players_stats = []
    player_inital_value = turn_string_to_list(row['player_initial_value'])
    hit = turn_string_to_list(row['hit'])
    results = turn_string_to_list(row['results'])
    for i in range(len(results)):
        curr_dict = {'index': index,'dealer_card': row['dealer_card'],'dealer_value': row['dealer_value'],
                              'player_initial_value': int(player_inital_value[i]),
                               'hit': int(hit[i]),'dealer_bust': int(row['dealer_bust']),
                                'result': float(results[i])}
        if 'player_counts' in row.keys():
            player_counts = turn_string_to_list(row['player_counts'])
            curr_dict['player_count'] = int(player_counts[i])
        players_stats.append(curr_dict)
    return players_stats

def formatted_print_row(rows):
    for i in range(len(rows)):
        print(rows[i])

def find_winLossPush_stats():
    num_wins = 0
    num_losses = 0
    num_pushes = 0
    total_hands = df.shape[0] * num_players
    for index, row in df.iterrows():
        current_result_list = turn_string_to_list((row['results']))
        for i in range(num_players):
            current_result = float(current_result_list[i])
            if current_result == 1.0:
                num_wins += 1
            elif current_result == 0:
                num_pushes += 1
            else:
                num_losses += 1
    win_percent = round((num_wins/total_hands) * 100, 2)
    push_percent = round((num_pushes/total_hands) * 100, 2)
    loss_percent = round((num_losses/total_hands) * 100, 2)

    print(f"win percentage = {win_percent}, push percentage = {push_percent}, loss percentage = {loss_percent}")

def blackJack_stats():
    num_dealer_bj = 0
    num_player_bj = 0
    # Times by num players for each hand a player playes
    total_hands_players = df.shape[0] * num_players
    # just get the number of hands played as a dealer only gets one hand
    total_hands_dealer = df.shape[0]
    for index, row in df.iterrows():
        current_result_list = turn_string_to_list((row['player_initial_value']))
        dealer_value = int(row['dealer_value'])
        if dealer_value == 21:
            num_dealer_bj += 1
        for i in range(num_players):
            current_result = int(current_result_list[i])
            if current_result == 21:
                num_player_bj += 1
    player_bj_percent = (num_player_bj/total_hands_players) * 100
    dealer_bj_percent = (num_dealer_bj/total_hands_dealer) * 100
    print(f'The dealer got {num_dealer_bj} Black jacks with a percentage of {dealer_bj_percent}')
    print(f'The players had a {num_player_bj} Black Jacks with a percentage of {player_bj_percent}')

def player_stats_based_on_dealers_card():
    #Use a dictionary to keep tract of how the player does vs what a dealer's show card is
    # Each card has a list where in order the elements are the total/wins/losses/pushes
    dealer_card_dict = {'A': [0, 0, 0, 0], '2': [0, 0, 0, 0], '3': [0, 0, 0, 0], '4': [0, 0, 0, 0], '5': [0, 0, 0, 0], '6': [0, 0, 0, 0],
                        '7': [0, 0, 0, 0], '8': [0, 0, 0, 0], '9': [0, 0, 0, 0], '10': [0, 0, 0, 0], 'J': [0, 0, 0, 0], 'Q': [0, 0, 0, 0], 'K': [0, 0, 0, 0]}
    for index, row in df.iterrows():
        players_stats = split_data_per_player(row, index)
        for i in range(len(players_stats)): 
            current_player_result = players_stats[i]['result']
            current_dealer_card = players_stats[i]['dealer_card']
            if current_player_result == 1:
                dealer_card_dict[current_dealer_card][0] +=1
                dealer_card_dict[current_dealer_card][1] +=1
            elif current_player_result == -1:
                dealer_card_dict[current_dealer_card][0] +=1
                dealer_card_dict[current_dealer_card][2] +=1 
            else:
                dealer_card_dict[current_dealer_card][0] +=1
                dealer_card_dict[current_dealer_card][3] +=1
    for key in dealer_card_dict.keys():
        total = dealer_card_dict[key][0]
        wins = dealer_card_dict[key][1]
        loss = dealer_card_dict[key][2]
        push = dealer_card_dict[key][3]
        print(f'When the dealer has {key} the player wins {round((wins/total)*100, 2)} percent of hands, loses {round((loss/total) *100,2)} percent, and pushes {round((push/total) *100,2)} percent')

def player_stats_based_on_initial_hand_value():
    #Use a dictionary to keep tract of how the player does based on inital hand value
    # Each card has a list where in order the elements are the total/wins/losses/pushes
    initial_hand_dict = { 4: [0, 0, 0, 0], 5: [0, 0, 0, 0], 6: [0, 0, 0, 0], 7: [0, 0, 0, 0], 8: [0, 0, 0, 0], 9: [0, 0, 0, 0],
                        10: [0, 0, 0, 0], 11: [0, 0, 0, 0], 12: [0, 0, 0, 0], 13: [0, 0, 0, 0], 14: [0, 0, 0, 0], 15: [0, 0, 0, 0],
                        16: [0, 0, 0, 0], 17: [0, 0, 0, 0], 18: [0, 0, 0, 0], 19: [0, 0, 0, 0], 20: [0, 0, 0, 0], 21: [0, 0, 0, 0]}
    for index, row in df.iterrows():
        players_stats = split_data_per_player(row, index)
        for i in range(len(players_stats)): 
            current_player_result = players_stats[i]['result']
            current_dealer_card = players_stats[i]['player_initial_value']
            if current_player_result == 1:
                initial_hand_dict[current_dealer_card][0] +=1
                initial_hand_dict[current_dealer_card][1] +=1
            elif current_player_result == -1:
                initial_hand_dict[current_dealer_card][0] +=1
                initial_hand_dict[current_dealer_card][2] +=1 
            else:
                initial_hand_dict[current_dealer_card][0] +=1
                initial_hand_dict[current_dealer_card][3] +=1
    for key in initial_hand_dict.keys():
        total = initial_hand_dict[key][0]
        wins = initial_hand_dict[key][1]
        loss = initial_hand_dict[key][2]
        push = initial_hand_dict[key][3]

        if wins == 0:
            winPercent = 0
        else:
            winPercent = round((wins/total)*100, 2)
        if loss == 0:
            lossPercent = 0
        else:
            lossPercent = round((loss/total) *100,2)
        if push == 0:
            pushPercent = 0
        else: 
            pushPercent = round((push/total) *100,2)
        print(f'When the player has {key} the player wins {winPercent} percent of hands, loses {lossPercent} percent, and pushes {pushPercent} percent')
print('')
#blackJack_stats()
print('')
player_stats_based_on_initial_hand_value()
print('')
player_stats_based_on_dealers_card()
print('')
find_winLossPush_stats()

# Display the DataFrame
# print(df)