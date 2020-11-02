# 1. Фактический результат
real_result = [0, 1]

# 2. Ожидаемый результат
expected_result = (
    (0, 0.5, 0.5),
    (25, 0.53, 0.47),
    (50, 0.57, 0.43),
    (100, 0.64, 0.36),
    (150, 0.70, 0.30),
    (200, 0.76, 0.24),
    (250, 0.81, 0.19),
    (300, 0.85, 0.15),
    (350, 0.89, 0.11),
    (400, 0.92, 0.08),
    (450, 0.94, 0.06),
    (500, 0.96, 0.04),
    (735, 0.99, 0.01),
)


def rating_elo(winner, pair_):
    looser_real_res = real_result[0]
    winner_real_res = real_result[1]
    winner_expected_res, looser_expected_res = get_exprected_result(
        abs(pair_.freeze_rating_sportsman1 - pair_.freeze_rating_sportsman2))
    if pair_.sportsman1 == winner:
        # спортсмен 1 победитель
        delta1 = delta_elo(get_K(pair_.freeze_rating_sportsman1), winner_real_res,
                                                  winner_expected_res)
        # спортсмен 2 победитель
        delta2 = delta_elo(get_K(pair_.freeze_rating_sportsman2), looser_real_res,
                                                  looser_expected_res)
    else:
        # спортсмен 2 победитель
        delta1 = delta_elo(get_K(pair_.freeze_rating_sportsman1), looser_real_res,
                                                  looser_expected_res)
        # спортсмен 1 победитель
        delta2 = delta_elo(get_K(pair_.freeze_rating_sportsman2), winner_real_res,
                                                  winner_expected_res)

    print(" ТИП pair_.sportsman1.rating: {0}".format(type(pair_.sportsman1.rating)))
    print(" ТИП pair_.sportsman2.rating: {0}".format(type(pair_.sportsman2.rating)))
    print(" ТИП pair_.delta_rating_sportsman1: {0}".format(type(pair_.delta_rating_sportsman1)))
    print(" ТИП pair_.delta_rating_sportsman2: {0}".format(type(pair_.delta_rating_sportsman2)))
    print(""
          "**********************************************************************"
          "*"
          " # POINT 200 - расчёт рейтинга\n"
          "* переданный winner: {0}\n"
          "* пара: {1}\n"
          "* rr_loos, rr_win: {2}, {3}\n"
          "* freez1, freez2: {4}, {5}\n"
          "* delta1, delta2: {6}, {7}\n"
          "* new_rating1, new_rating2: {8}, {9}\n".format(
        winner, pair_, looser_real_res, winner_real_res, pair_.freeze_rating_sportsman1, pair_.freeze_rating_sportsman2,
        pair_.delta_rating_sportsman1, pair_.delta_rating_sportsman2, pair_.sportsman1.rating, pair_.sportsman2.rating
    ))
    return delta1, delta2


def delta_elo(K, real_result, expected_result):
    return K * (real_result - expected_result)


def get_exprected_result(contrast):
    # если их разница > 735
    if contrast > expected_result[len(expected_result) - 1][0]:
        return 1, 0
    # если не > 735, то ищем промежуточное значение, либо точное совпадение
    for i in range(len(expected_result) - 1):
        # если точное совпадение
        if contrast == expected_result[i][0]:
            return expected_result[i][1], expected_result[i][2]
        # если нет, то ищем значения через интерполяцию
        else:
            if expected_result[i][0] < contrast < expected_result[i + 1][0]:
                return interpolation(contrast,
                                     expected_result[i][0], expected_result[i + 1][0],
                                     expected_result[i][1], expected_result[i + 1][1],
                                     expected_result[i][2], expected_result[i + 1][2])


def get_K(freeze_rating):
    if freeze_rating >= 2400:
        return 10
    elif 1000 < freeze_rating < 2400:
        return 15
    else:
        return 25


def interpolation(r, r1, r2, win_val1, win_val2, loos_val1, loos_val2):
    win_val = win_val1 + ((r-r1)/(r2-r1)) * (win_val2 - win_val1)
    loos_val = loos_val1 + ((r-r1)/(r2-r1)) * (loos_val2 - loos_val1)
    return round(win_val, 2), round(loos_val, 2)

