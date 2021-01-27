from database.profit import profits


def best_key():
    best_in_dict = max(profits, key=profits.get)
    return best_in_dict
