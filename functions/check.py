def duplicate(count, previous_net_profit, current_net_profit):
    is_duplicate = False
    try:
        if (count > 10) and (previous_net_profit == current_net_profit):
            print("\nDuplicate Values - The previous net profit is the same as the current net profit.\nNo "
                  "need to continue script.\nPrinting Results.")
            is_duplicate = True
    except (KeyError, TypeError, UnboundLocalError):
        pass
    return is_duplicate
