from django.shortcuts import render
from .models import Sportsman, Tournaments, BattlePair, WeightCategory, ResultsBattle, Statistics, SettingsSelections
from .forms import SportsmanForm
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.db.models import Q


def account_index(request, sportsman_name):
    account = get_object_or_404(Sportsman, slug=sportsman_name)
    context = {
        'account': account,
    }

    return render(request, 'account/about_ac.html', context)


def account_edit(request, sportsman_name):
    context = {}
    if request.method == 'POST':
        account = Sportsman.objects.get(slug=sportsman_name)
        form = SportsmanForm(request.POST, request.FILES, instance=account)
        if form.is_valid():
            context['success'] = True
            form.save()
    else:
        account = Sportsman.objects.get(slug=sportsman_name)
        form = SportsmanForm(instance=account)

    account = Sportsman.objects.get(slug=sportsman_name)
    context['account'] = account
    context['form'] = form

    return render(request, 'account/edit_ac.html', context)


def account_tournaments(request):
    try:
        id = request.GET['tournam_id']
        print("ID извлекли")
        tournament = Tournaments.objects.filter(id=id)[0]
        all_tournaments = Tournaments.objects.exclude(Q(id=tournament.id) | Q(is_build=False))
        print("НЕ КРАШНУЛОСЬ")
    except:
        print("КРАШНУЛОСЬ")
        tournament = Tournaments.objects.filter(is_build=True).first()
        all_tournaments = Tournaments.objects.exclude(Q(id=tournament.id) | Q(is_build=False))
    user = get_object_or_404(User, username=request.user.username)
    account = get_object_or_404(Sportsman, name=user)
    winners = {}
    weight_category = WeightCategory.objects.all()
    pairs = BattlePair.objects.filter(tournament=tournament)
    result = {}

    # формируем словарь с результатами пара(весовая)=значение(словарь типа 'стадия': [пары])
    if pairs.exists():
        for weight in weight_category:
            result[weight.weight_category] = {}
            for STAGE in BattlePair.STAGES:
                pairs_of_stage = BattlePair.objects.filter(tournament=tournament, weight_category=weight,
                                                           stage=STAGE[0])
                if len(pairs_of_stage) == 0:
                    continue

                result[weight.weight_category][STAGE[0]] = []
                for element in pairs_of_stage:
                    result[weight.weight_category][STAGE[0]].append(element)
            # отдельный словарь победителей (ключ - весова. Победитель - оъект класса спортсменов
            winners[weight.weight_category] = ''

    # удаляем из словаря ключ-значение, где значение пустое
    for key in list(result.keys()):  # list необходим для принудительного создания копии ключей,
        # чтобы можно было удалять на ходу. Иначе - ошибка.
        if not bool(result[key]):
            result.pop(key, None)
    print('#point: {0}'.format(result))

    weight_keys = list(result.keys())
    print("Весовые: {0}".format(weight_keys))
    for w_key in weight_keys:  # получаем ключи весовых. Например '56-60кг', '61-66кг'
        stages_dict = result[w_key]  # получаем словарь для конкретного ключа, например для '1/2'

        # получаем ключи в виде списка
        st_keys = list(stages_dict.keys())
        i = 0
        while i < len(BattlePair.STAGES):
            if BattlePair.STAGES[i][0] in st_keys:
                st_keys.append(BattlePair.STAGES[i][0])
            i += 1
        st_keys = st_keys[int(len(st_keys) / 2):]
        st_keys.reverse()
        print("Ключи в нужной последовательности: {0}".format(st_keys))

        # начинаем сортировку
        limit = len(st_keys)  # - например limit = 2
        i = 0
        print(" #point-limit1: {0}".format(limit))

        while i < limit - 1:  # - если выполняется это условие, то считается, что цикл дошел до
            # самых ранних этапов, которые уже должны были отсортироваться
            list_pairs = stages_dict[st_keys[i]]  # list_pairs - список пар определенного этапа
            new_prev_list_pairs = []  # новый отсортированный список, который заменит предыдущий этап
            for pair in list_pairs:
                sportsman1 = pair.sportsman1
                sportsman2 = pair.sportsman2
                # print('Пара: {0}'.format(pair))
                # print('Спортсмен 1: {0}'.format(sportsman1))
                # print('Спортсмен 2: {0}'.format(sportsman2))

                prev_list_pairs = stages_dict[st_keys[i + 1]]
                for prev_pair in prev_list_pairs:
                    if sportsman1 == prev_pair.sportsman1 or sportsman1 == prev_pair.sportsman2:
                        new_prev_list_pairs.append(prev_pair)
                        break
                for prev_pair in prev_list_pairs:
                    if sportsman2 == prev_pair.sportsman1 or sportsman2 == prev_pair.sportsman2:
                        new_prev_list_pairs.append(prev_pair)
                        break
            stages_dict[st_keys[i + 1]] = new_prev_list_pairs
            print(" #new-prev-list: {0}".format(stages_dict[st_keys[i + 1]]))

            # print()
            # print("Новый список для добавления:")
            # print(new_prev_list_pairs)
            # print()

            i += 1

    print("#point1 Результат: {0}".format(result))

    # наполняем словарь победителей
    # keys_winners = list(winners.keys())
    for pair in pairs:
        if pair.stage == "Финал":
            res = ResultsBattle.objects.filter(stage=pair.stage, tournament=tournament)
            if res.exists():
                if res[0].summ_points > res[1].summ_points:
                    winners[pair.weight_category.weight_category] = res[0].sportsman
                elif res[0].summ_points < res[1].summ_points:
                    winners[pair.weight_category.weight_category] = res[1].sportsman
                else:
                    winners[pair.weight_category.weight_category] = 'Ничья'
            else:
                winners[pair.weight_category.weight_category] = 'Неизвестно'
            print("")
            print("Результаты боя")
            print(winners)

    # print()
    # print("Результат")
    # print(result)
    print("Победители")
    print(winners)
    # print("Ключи победителей")
    # print(keys_winners)
    print("#point2 Результат: {0}".format(result))
    context = {
        'tournament': tournament,
        'account': account,
        'tournaments': result,
        'winners': winners,
        'all_tournaments': all_tournaments,
    }

    return render(request, 'account/tournaments_ac.html', context)


def account_rating(request):
    user = get_object_or_404(User, username=request.user.username)
    account = get_object_or_404(Sportsman, name=user)
    all_sp = Sportsman.objects.all()
    wc = WeightCategory.objects.all()
    sp_other_weight_list = []
    sp_current_weight = all_sp.filter(weight_category=account.weight_category)
    sp_other_weight = all_sp.exclude(weight_category=account.weight_category)

    print(" #POINT 200 - весовые: {0}".format(wc))
    for w in wc:
        print(" #POINT 200.1 - весовая: {0}".format(w))
        if w == account.weight_category:
            print(" #POINT 200.1.1 - весовую {0} пропускаем".format(w))
            continue
        pairs_of_weight = sp_other_weight.filter(weight_category=w)
        print(" #POINT 200.2 - пары весовой {0}: {1}".format(w, pairs_of_weight))
        if not pairs_of_weight.count() == 0:
            sp_other_weight_list.append(pairs_of_weight)

    print(" #POINT 203 - sp_other_weight_list {0}".format(sp_other_weight_list))

    context = {
        'account': account,
        'all_sp': all_sp,
        'sp_current_weight': sp_current_weight,
        'sp_other_weight_list': sp_other_weight_list
    }
    return render(request, 'account/rating_ac.html', context)


def account_selection(request):
    def get_borders_middle(a, b, c, d, mu):
        middle_left_border = b + (a - b) * (1 - mu)
        middle_right_border = c + (d - c) * (1 - mu)
        return middle_left_border, middle_right_border

    def get_borders_right(a, b, mu):
        return a + (b - a) * mu

    def get_percent(stat, hand=True):
        if hand is not False:
            if stat.handstrikes + stat.handstrikes_tohead == 0:
                return 0
            else:
                return ((stat.handstrikes + stat.handstrikes_tohead) / (stat.handstrikes + stat.handstrikes_tohead +
                                                               stat.kicks + stat.kicks_tohead + stat.rotate_kicks)) * 100
        else:
            if stat.kicks + stat.kicks_tohead + stat.rotate_kicks == 0:
                return 0
            else:
                return ((stat.kicks + stat.kicks_tohead + stat.rotate_kicks) / (stat.handstrikes + stat.handstrikes_tohead +
                                                               stat.kicks + stat.kicks_tohead + stat.rotate_kicks)) * 100

    user = get_object_or_404(User, username=request.user.username)
    account = Sportsman.objects.get(name=user)
    cur_w = account.weight_category.weight_category
    print(" #POINT 300 - подбор соперника")
    print(" #POINT 300.1 - текущая весовая: {0}, type: {1}".format(cur_w, type(cur_w)))
    wc = WeightCategory.objects.all()
    new_wc = []
    # сортируем список весовых
    for w in wc:
        if w.weight_category[0] != "<" and w.weight_category[0] != ">":
            new_wc.append(w.weight_category)
    new_wc.sort()
    for w in wc:
        if w.weight_category[0] == "<":
            new_wc.insert(0, w.weight_category)
        elif w.weight_category[0] == ">":
            new_wc.append(w.weight_category)
    print(" #POINT 300.2 - отсортированные весовые: {0}".format(new_wc))

    # откидываем лишние весовые
    index = new_wc.index(cur_w)
    if index == 0:
        new_wc = new_wc[0:2]
    elif index == len(new_wc) - 1:
        new_wc = new_wc[len(new_wc) - 2: len(new_wc)]
    else:
        new_wc = new_wc[index - 1:index + 2]
    print(" #POINT 300.3 - оставшиеся весовые: {0}".format(new_wc))

    # получим объекты весовых категорий
    print(" #POINT 300.6 - wc: {0}".format(wc))
    for w in wc:
        if w.weight_category in new_wc:
            # print(" #POINT 300.5 - есть такая весовая: {0}".format(type(w)))
            new_wc.append(w)
    new_wc = new_wc[int(len(new_wc)/2):]
    print(" #POINT 300.4 - оставшиеся весовые (объекты): {0}".format(new_wc))

    # получаем статистику нужных нам весовых
    if len(new_wc) == 3:
        statistic = Statistics.objects.filter(Q(sportsman__weight_category=new_wc[0]) |
                                              Q(sportsman__weight_category=new_wc[1]) |
                                              Q(sportsman__weight_category=new_wc[2]))
    elif len(new_wc) == 2:
        statistic = Statistics.objects.filter(Q(sportsman__weight_category=new_wc[0]) |
                                              Q(sportsman__weight_category=new_wc[1]))
    print(" #POINT 300.7 - статистика нужных нам весовых: {0}".format(statistic))


    # реализация нечеткой логики
    lvls = {
        'middle_rating_lvl': set(),
        'hand_high_lvl': set(),
        'foot_high_lvl': set(),
    }
    # получаем настройки и все границы функций
    setting = SettingsSelections.objects.get(active=True)
    middle_left_border, middle_right_border = get_borders_middle(setting.border_x_bottom_left, setting.border_x_top_left,
                                                                 setting.border_x_top_right, setting.border_x_bottom_right,
                                                                 setting.mu)
    middle_left_border += account.rating
    middle_right_border += account.rating
    hand_border = get_borders_right(setting.border_hand_left, setting.border_hand_right, setting.mu)
    foot_border = get_borders_right(setting.border_foot_left, setting.border_foot_right, setting.mu)
    print(" #POINT 400.1 - граница для рук {0}".format(hand_border))
    print(" #POINT 400.2 - граница для ног {0}".format(foot_border))
    # сортируем по множествам (lvls) спортсменов
    for stat in statistic:
        if stat.sportsman == account:
            continue
        # проверяем руки
        if get_percent(stat, hand=True) > hand_border:
            lvls['hand_high_lvl'].add(stat.sportsman)
        if get_percent(stat, hand=False) > foot_border:
            lvls['foot_high_lvl'].add(stat.sportsman)
        if middle_left_border < stat.sportsman.rating < middle_right_border:
            lvls['middle_rating_lvl'].add(stat.sportsman)
    print(" #POINT 401.0 - {0}".format(lvls))

    context = {
        'account': account,
        'statistic': statistic,
        'for_foots': lvls['foot_high_lvl'].intersection(lvls['middle_rating_lvl']),
        'for_hands': lvls['hand_high_lvl'].intersection(lvls['middle_rating_lvl']),
        'for_tournaments': lvls['middle_rating_lvl'],
    }
    return render(request, 'account/selection_ac.html', context)

