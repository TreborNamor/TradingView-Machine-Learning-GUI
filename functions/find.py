from database.profit import profits


def best_stoploss():
    best_in_dict = max(profits, key=profits.get)
    return best_in_dict


def best_takeprofit():
    best_in_dict = max(profits, key=profits.get)
    return best_in_dict


def best_key_both():
    best_in_dict = max(profits)
    return best_in_dict
