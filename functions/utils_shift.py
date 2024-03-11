# This is a function defined to do hypothetical load shift

def shift(threshold, df):

    # Chiller 30% setpoint reset
    potential_power = []
    i = 0
    deposit = 0
    deposit_list = []
    activation = 0

    df = df.reset_index(drop=True)
    while i < len(df):
        if df['moer'][i] <= threshold:
            potential_power.append(df["predicted_power"][i] * 1.5)
            deposit = deposit - df["predicted_power"][i] * 0.5
            activation = activation + 1
            deposit_list.append(deposit)
        elif df['moer'][i] > threshold and deposit < 0:
            if deposit <= -df["predicted_power"][i] * 0.3:
                potential_power.append(df["predicted_power"][i] * 0.7)
                deposit = deposit + df["predicted_power"][i] * 0.3
                deposit_list.append(deposit)
            else:
                potential_power.append(df["predicted_power"][i] + deposit)
                deposit = 0
                deposit_list.append(deposit)
        else:
            potential_power.append(df["predicted_power"][i])
            deposit_list.append(deposit)
        i = i + 1

    potential_emissions = potential_power * df['moer'] / 1000

    return potential_power, potential_emissions, deposit_list, activation