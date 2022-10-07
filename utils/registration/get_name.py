import random


def get_name_lastname_agent(male):
    if male == 'man':
        with open('data/names_man.txt', 'r', encoding='utf-8') as f:
            arr_name = f.read().split('\n')
        with open('data/lastname_man.txt', 'r', encoding='utf-8') as f:
            arr_last_name = f.read().split('\n')

    else:
        with open('data/names_woman.txt', 'r', encoding='utf-8') as f:
            arr_name = f.read().split('\n')
        with open('data/lastname_woman.txt', 'r', encoding='utf-8') as f:
            arr_last_name = f.read().split('\n')
    with open('data/user_agents.txt', 'r', encoding='utf-8') as f:
        arr_agents = f.read().split('\n')
    return arr_name[random.randint(0, len(arr_name) - 1)], arr_last_name[random.randint(0, len(arr_last_name) - 1)], arr_agents[random.randint(0, len(arr_agents) - 1)]