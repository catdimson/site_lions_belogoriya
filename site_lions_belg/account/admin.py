from django.contrib import admin
from .models import BattlePair, Belts, WeightCategory, Sportsman, Statistics, Tournaments, ResultsBattle, SettingsSelections
from django.forms import ModelForm, ValidationError
from django import forms
from site_lions_belg.settings import COUNT_STAGES_RECORD
from django.db.models import Q
import math
from .rating_elo import rating_elo
from django.contrib import messages


# num - число, которое нужно проверить
def is_int(num, ideal_num):
    e = 0.00001
    return True if abs(num - ideal_num) < e else False


# получение лимита пар для этапа
def get_limit(stage):
    return COUNT_STAGES_RECORD[stage]


# получение предыдущего этапа по текущему. Если текущий крайний, то предыдущий - крайний (минимальный)
def get_prev_stage(stage):
    if stage == BattlePair.STAGES[0][0]:
        return BattlePair.STAGES[0][0]
    else:
        i = 1
        while i < len(BattlePair.STAGES):
            if BattlePair.STAGES[i][0] == stage:
                return BattlePair.STAGES[i - 1][0]
            else:
                i += 1


# получение последующего этапа по текущему. Если текущий крайний, то последующий - финал (максимальный)
def get_next_stage(stage):
    if stage == BattlePair.STAGES[len(BattlePair.STAGES) - 1][0]:
        return BattlePair.STAGES[len(BattlePair.STAGES) - 1][0]
    else:
        i = 0
        while i < len(BattlePair.STAGES):
            if BattlePair.STAGES[i][0] == stage:
                return BattlePair.STAGES[i + 1][0]
            else:
                i += 1


class BeltsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Belts._meta.fields]  # вывести все поля

    class Meta:
        model = Belts


class WeightCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WeightCategory._meta.fields]  # вывести все поля

    class Meta:
        model = WeightCategory


class SportsmanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Sportsman._meta.fields]  # вывести все поля
    list_display.remove('photo')  # cкрыть поле из списка объектов
    exclude = ['fake']  # скрыть из редактировнаия
    readonly_fields = ('slug', 'rating')  # нельзя редактировать

    class Meta:
        model = Sportsman


class TournamentsAdminForm(ModelForm):
    class Meta:
        model = Tournaments
        fields = '__all__'

    def clean(self):
        def is_validate_build_pairs(tournament):
            # получаем пары соответствующие каждой весовой категории
            wc = WeightCategory.objects.all()
            print(" # wc: {0}".format(wc))
            for w in wc:
                print(" #POINT-6 w: {0}".format(w))
                # получаем все пары данной весовой, данного турнира
                pairs_of_weight_category = BattlePair.objects.filter(tournament__name=tournament, weight_category=w)
                if pairs_of_weight_category.count() == 0:
                    print(" #POINT-9: для весовой {0} пар нет".format(w))
                    continue
                print(" #POINT-8")
                # пройдёмся по всем стадиям
                for i in range(len(BattlePair.STAGES)):
                    # получаем название стадии из кортежа ('Финал', '1/2' и тд)
                    stage = BattlePair.STAGES[len(BattlePair.STAGES) - i - 1][0]
                    quantity = pairs_of_weight_category.filter(stage=stage).count()
                    if quantity == 0:
                        for j in range(i + 1, len(BattlePair.STAGES)):
                            next_stage = BattlePair.STAGES[len(BattlePair.STAGES) - j - 1][0]
                            quantity_next = pairs_of_weight_category.filter(stage=next_stage).count()
                            if quantity_next != 0:
                                raise ValidationError("Сформировать пары пока нельзя. Заполните все пары на "
                                                      "требуемых стадиях")
                        break
                    print(" - - - - - ")
                    print(" #POINT-15: stage - {0}".format(stage))
                    print(" #POINT-12: quantity - {0}".format(quantity))
                    print(" #POINT-13: log2 - {0}".format(math.log2(quantity)))
                    print(" #POINT-16: log2_ideal - {0}".format(math.log2(COUNT_STAGES_RECORD[stage])))
                    print(" - - - - - ")
                    if not is_int(math.log2(quantity), math.log2(COUNT_STAGES_RECORD[stage])):
                        print(" #POINT-14: is_int - {0}".format(
                            is_int(math.log2(quantity), math.log2(COUNT_STAGES_RECORD[stage]))))
                        raise ValidationError("Сформировать пары пока нельзя. "
                                              "Не заполнена стадия {0} в весовой категории {1} "
                                              "данного турнира".format(stage, w))
                print(" #POINT-10: пары для весовой {0} успешно сформированы".format(w))

        def is_validate_full_results(tournament):
            print(" #POINT 130.0 - функция срабатывает, когда is_build-выполнено, а is_conduct - пытаемся провести")
            wc = WeightCategory.objects.all()
            print(" #POINT 130.1 - весовые  {0}".format(wc))
            for w in wc:
                print(" #POINT 130.2 - {0}".format(w))
                # получаем все пары данной весовой, данного турнира
                pairs_of_weight_category = BattlePair.objects.filter(tournament__name=tournament, weight_category=w)
                print(" #POINT 130.5 - пары весовой {0} : {1}".format(w, pairs_of_weight_category))
                if pairs_of_weight_category.count() == 0:
                    print(" #POINT 130.3 - для весовой {0} пар нет".format(w))
                    continue
                # пройдёмся по всем стадиям
                for i in range(len(BattlePair.STAGES)):
                    stage = BattlePair.STAGES[len(BattlePair.STAGES) - i - 1][0]
                    print(" #POINT 130.6 - проходимся по всем стадиям. stage: {0}".format(stage))
                    prev_stage = get_prev_stage(stage)
                    pairs_of_stage = pairs_of_weight_category.filter(stage=stage)
                    quantity = pairs_of_stage.count()
                    print(" #POINT 130.7 - проходимся по всем стадиям. prev_stage: {0}".format(prev_stage))
                    print(" #POINT 130.8 - проходимся по всем стадиям. pairs_of_stage: {0}".format(pairs_of_stage))
                    if quantity != 0:
                        results_of_stage = ResultsBattle.objects.filter(tournament__name=tournament,
                                                                        sportsman__weight_category=w,
                                                                        stage=stage)
                        print(" #POINT 130.9 - проходимся по всем стадиям. quantity: {0}".format(quantity))
                        print(" #POINT 130.10 - проходимся по всем стадиям. get_limit: {0}".format(get_limit(stage) * 2))
                        if results_of_stage.count() == quantity * 2:
                            print(" #POINT 130.4 - для стадии {0} кол-во результатов: {1}".format(stage,
                                                                                                  get_limit(stage) * 2))
                        else:
                            raise ValidationError("Для стадии {0} турнира {1} не занесены все результаты".format(
                                stage, tournament))

                        # ПРОВЕРКА КОРРЕКТНОСТИ результатов. Это условие означает, что мы находимся в самой ранней
                        # стадии и раньше него уже нет пар. На этом этапе мы знаем, что что пары уже заполнены до limit
                        # т.е. их кол-во либо == limit, либо 0.
                        if i != len(BattlePair.STAGES) - 1:
                            # т.к. этот if будет выполняться вплоть до предпоследней стадии, то чтобы не выйти за преде-
                            # лы кортежа - пары предыдущей стадии будем получать в этом условии
                            pairs_of_prev_stage = pairs_of_weight_category.filter(stage=prev_stage)
                            # если пары есть (а если и есть, то их кол-во только limit)
                            if pairs_of_prev_stage.count() == get_limit(prev_stage):
                                # то пройдемся по парам предыдущей стадии
                                for pair_ in pairs_of_prev_stage:
                                    winner = ''
                                    sp1 = pair_.sportsman1
                                    sp2 = pair_.sportsman2
                                    # получаем результаты пары из предыдущей стадии и далее определяем победителя
                                    res_sp1 = ResultsBattle.objects.get(tournament__name=tournament,
                                                                        stage=prev_stage,
                                                                        sportsman=sp1)
                                    res_sp2 = ResultsBattle.objects.get(tournament__name=tournament,
                                                                        stage=prev_stage,
                                                                        sportsman=sp2)
                                    # случай с отсутствием бойца
                                    if res_sp1.is_not or res_sp2.is_not:
                                        winner = sp1 if res_sp2.is_not else sp2
                                    if not winner:
                                        # случай с дисквалификацией
                                        if res_sp1.disqualification and res_sp2.disqualification:
                                            raise ValidationError("Не корректное заполнение результатов. Оба бойца "
                                                                  "не могут быть дисквалифицированы. ({0}, {1} турнир: {2})"
                                                                  "".format(res_sp1, res_sp2, tournament))
                                        if res_sp1.disqualification or res_sp2.disqualification:
                                            winner = sp1 if res_sp2.disqualification else sp2

                                        # случай с нокаутом
                                        if res_sp1.knockout and res_sp2.knockout:
                                            raise ValidationError("Не корректное заполнение результатов. У обоих бойцов "
                                                                  "проставлен нокаут в результатах. ({0}, {1} турнир: {2})"
                                                                  "".format(res_sp1, res_sp2, tournament))
                                        if not winner and (res_sp1.knockout or res_sp2.knockout):
                                            winner = sp1 if res_sp1.knockout else sp2

                                        # случай, когда один просто набрал больше очков, чем другой
                                        if not winner:
                                            if res_sp1.summ_points == res_sp2.summ_points:
                                                raise ValidationError(
                                                    "Не корректное заполнение результатов. Не может быть ничьи. "
                                                    "({0}, {1} турнир: {2})"
                                                    "".format(res_sp1, res_sp2, tournament))
                                            else:
                                                winner = sp1 if res_sp1.summ_points > res_sp2.summ_points else sp2

                                    # после этих условий мы определили победителя. Осталось проверить, есть ли он в
                                    # результатах текущей стадии. Если его нет - то результаты не правильно забиты.
                                    if not pairs_of_stage.filter(Q(sportsman1=winner) | Q(sportsman2=winner)).exists():
                                        raise ValidationError("Не корректное заполнение результатов. По заполненным результатам " \
                                              "выходит, что победителя этапа {0} ({1}) нет в следующем этапе {2}" \
                                              "".format(prev_stage, winner, stage))


                    # QuerySet всех результатов данного турнира, данной весовой, данной стадии
                    else:
                        break
            print(" #POINT 130.6 - для турнира {0} валидация по кол-ву прошла успешно".format(tournament))

        def calculation_rating(tournament, up=True):
            print(" #POINT 160.0 - функция расчёта рейтинга ВВЕРХ")
            wc = WeightCategory.objects.all()
            print(" #POINT 160.1 - весовые  {0}".format(wc))
            for w in wc:
                print(" #POINT 160.2 - конкретная весовая {0}".format(w))
                # получаем все пары данной весовой, данного турнира
                pairs_of_weight_category = BattlePair.objects.filter(tournament__name=tournament, weight_category=w)
                print(" #POINT 160.3 - пары весовой {0} : {1}".format(w, pairs_of_weight_category))
                if pairs_of_weight_category.count() == 0:
                    print(" #POINT 160.4 - для весовой {0} пар нет".format(w))
                    continue
                else:
                    results_of_weight_category = ResultsBattle.objects.filter(tournament__name=tournament,
                                                                              sportsman__weight_category=w)
                # пройдёмся по всем стадиям
                for i in range(len(BattlePair.STAGES)):
                    stage = BattlePair.STAGES[i][0]
                    print(" #POINT 160.5 - проходимся по всем стадиям. stage: {0}".format(stage))
                    pairs_of_stage = pairs_of_weight_category.filter(stage=stage)
                    quantity = pairs_of_stage.count()
                    # этим условием находим этап, с которого начали формироваться пары в данной весовой
                    if not quantity == 0:
                        results_of_stage = results_of_weight_category.filter(stage=stage)
                        print(" #POINT 160.6 - проходимся по стадии {0}: {1}".format(stage, pairs_of_stage))
                        # проходимся по парам стадии
                        for pair_ in pairs_of_stage:
                            # получаем спортсменов из пар, и находим результаты, которые им соответствуют
                            sp1 = pair_.sportsman1
                            sp2 = pair_.sportsman2
                            winner = ''
                            # ЭТА ВЕТВЬ ВЫПОЛНИТСЯ, ЕСЛИ ПРОВОДИМ ТУРНИР, И НУЖНО РАССЧИТАТЬ НОВЫЙ РЕЙТИНГ
                            if up:
                                res_sp1 = results_of_stage.get(sportsman=sp1)
                                res_sp2 = results_of_stage.get(sportsman=sp2)
                                # если кто-то отсутствовал, то пропускаем пару и рейтинг не перерасчитываем
                                if res_sp1.is_not or res_sp2.is_not:
                                    print(" #POINT 160.7 - есть отсутствующий")
                                    continue
                                else:
                                    # т.к. это финал, то победителя нужно будет определить ручками по результатам
                                    if i == len(BattlePair.STAGES) - 1:
                                        print(" #POINT 160.8 - работаем с финишной парой")

                                        # случай с дисквалификацией
                                        if res_sp1.disqualification or res_sp2.disqualification:
                                            winner = sp1 if res_sp2.disqualification else sp2

                                        # случай с нокаутом
                                        if not winner and (res_sp1.knockout or res_sp2.knockout):
                                            winner = sp1 if res_sp1.knockout else sp2

                                        # случай, когда один просто набрал больше очков, чем другой
                                        if not winner:
                                            winner = sp1 if res_sp1.summ_points > res_sp2.summ_points else sp2
                                        print(' #POINT 160.10 - winner: {0}'.format(winner))
                                        print(' #POINT - rating elo - 160.12 - пара: {0}'.format(pair_))
                                        delta1, delta2 = rating_elo(winner, pair_)
                                        pair_.sportsman1.rating += delta1
                                        pair_.sportsman2.rating += delta2
                                        pair_.delta_rating_sportsman1 = delta1
                                        pair_.delta_rating_sportsman2 = delta2
                                        pair_.sportsman2.save(), pair_.sportsman1.save(), pair_.save()

                                    # если не финал, то победитель определяется по наличию спортсмена в следующем этапе
                                    else:
                                        print(" #POINT 160.9 - этап: НЕ финал")
                                        pairs_of_next_stage = pairs_of_weight_category.filter(stage=BattlePair.STAGES[i + 1][0])
                                        for p in pairs_of_next_stage:
                                            if p.sportsman1 == sp1 or p.sportsman2 == sp1:
                                                winner = sp1
                                                break
                                        if not winner:
                                            winner = sp2
                                        print(' #POINT 160.11 - winner: {0}'.format(winner))
                                        print(' #POINT - rating elo - 160.12 - пара: {0}'.format(pair_))
                                        delta1, delta2 = rating_elo(winner, pair_)
                                        pair_.sportsman1.rating += delta1
                                        pair_.sportsman2.rating += delta2
                                        pair_.delta_rating_sportsman1 = delta1
                                        pair_.delta_rating_sportsman2 = delta2
                                        pair_.sportsman2.save(), pair_.sportsman1.save(), pair_.save()

                            # ЭТА ВЕТВЬ ВЫПОЛНЯЕТСЯ, КОГДА ОТМЕНЯЕТСЯ ПРОВЕДЕНИЕ ТУРНИРА И НУЖНО ОТКАТИТЬ РЕЙТИНГ НАЗАД
                            else:
                                pair_.sportsman1.rating -= pair_.delta_rating_sportsman1
                                pair_.sportsman2.rating -= pair_.delta_rating_sportsman2
                                pair_.delta_rating_sportsman1 = 0
                                pair_.delta_rating_sportsman2 = 0
                                pair_.sportsman2.save(), pair_.sportsman1.save(), pair_.save()

        def is_conduct_tournaments_after(id, date):
            all_tournaments = Tournaments.objects.filter(~Q(id=id), Q(date__gt=date) | Q(date=date), is_conduct=True)
            if all_tournaments.exists():
                print(' #POINT 150 - проверка наличия проведенных позднее турниров')
                print(' #POINT 150.1 - поздние турниры: {0}'.format(all_tournaments))
                return True

        def is_change_data(cleaned_data, obj):
            if not (cleaned_data.get('date') == obj.date and cleaned_data.get('name') == obj.name and
                    cleaned_data.get('judge1') == obj.judge1 and cleaned_data.get('judge2') == obj.judge2 and
                    cleaned_data.get('judge3') == obj.judge3 and cleaned_data.get('judge4') == obj.judge4):
                return True

        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        is_build, is_conduct = cleaned_data.get('is_build'), cleaned_data.get('is_conduct')
        # ищем такой турнир в базе
        obj = Tournaments.objects.filter(name=name)
        # если ЕСТЬ такой турнир
        if obj:
            # если сохраняемый объект, и объект из БД не один и тот же объект
            if obj[0].id != self.instance.id:
                raise ValidationError("Такой турнир уже зарегестрирован в базе данных")
            # если один и тот же
            else:
                obj_is_build, obj_is_conduct = self.instance.is_build, self.instance.is_conduct
                # не установлена галочка сформированных пар
                if not obj_is_build:
                    # не установлена галочка проведения турнира
                    if not obj_is_conduct:
                        if is_build and is_conduct:
                            raise ValidationError("Перед проведением должны быть заполнены все результаты боёв."
                                                  " Сначала происходит добавление пар Домой>Аккаунты>Пары, потом их "
                                                  "построение (устанавливает галочка). После - "
                                                  "заполняются результаты Домой>Аккаунты>Результаты боёв и в самую "
                                                  "последнюю очередь - проведение (устанавливает галочка)")
                        elif is_build and not is_conduct:
                            print(" #POINT-8: название турнира: {0}".format(name))
                            is_validate_build_pairs(name)                                                               # 1) ЕСТЬ - проверка заполнения пар пар
                        elif not is_build and not is_conduct:
                            pass  # -
                        else:
                            raise ValidationError("Вы не можете провести турнир, без построенных пар")
                    # установленной галочки проведений турнира быть не могло

                # если была установлена галочка сформированных пар
                else:
                    # если не была установлена галочка проведения турнира
                    if not obj_is_conduct:
                        if not is_build and not is_conduct:
                            pass  # -
                        elif is_build and not is_conduct:
                            pass  # -
                        elif is_build and is_conduct:
                            # проверить, нет ли проведенного турнира, который после текущего (по времени). Если есть -
                            # провести нельзя
                            if is_conduct_tournaments_after(self.instance.id, cleaned_data.get('date')):
                                raise ValidationError('Нельзя проводить турнир, если есть турнир, который проведен '
                                                      'позднее. Тогда рейтинг будет рассчитан не верно')
                            is_validate_full_results(name)
                            calculation_rating(name, True)
                            pass  # проверка на заполненность результатов и расчёт рейтинга                             2) +    3) -
                        else:
                            raise ValidationError("Должны быть сформированы пары, чтобы провеси турнир")
                    # если была установлена галочка проведения турнира
                    else:
                        if is_build and is_conduct:
                            # если турнир сформирован, то запретить измение каких-либо данных
                            if is_change_data(cleaned_data, obj[0]):
                                raise ValidationError('Нельзя изменять данные турнира, который проведен')
                            pass
                        elif is_build and not is_conduct:
                            # проверить, нет ли проведенного турнира, который после текущего (по времени). Если есть -
                            # провести нельзя
                            if is_conduct_tournaments_after(self.instance.id, self.instance.date):
                                raise ValidationError('Нельзя отменить проведение турнира, потому есть турнир, '
                                                      'который проведен позднее. Для отмены проведения текущего турнира '
                                                      'нужно отменить проведение всех последующих турниров в обратном '
                                                      'порядке.')
                            calculation_rating(name, False) # перерасчёт рейтинга в обратную сторону                    4) -
                        elif not is_build and not is_conduct:
                            raise ValidationError("Нельзя отменить проведение вместе с построением пар. Ведь в базе "
                                                  "уже хранятся результаты для пар. Если необходимо выполнить это, то "
                                                  "сначала уберите проведение турнира (галочку), затем вручную удалите "
                                                  "результаты пар турнира Домой>Аккаунты>Результаты боёв, а после "
                                                  "отмените построение пар (галочку)")
                        else:
                            raise ValidationError("Нельзя провести турнир без сформированных пар")

                print("Сейчас 'Построены пары': {0}".format(is_build))
                print("Сейчас 'Проведен': {0}".format(is_conduct))
                print("Было 'Построены пары': {0}".format(obj_is_build))
                print("Было 'Проведен': {0}".format(obj_is_conduct))


        # если НЕТ такого турнира
        else:
            if is_build:
                raise ValidationError("Вновь созданный турнир не может быть построен, потому что ему не назначены пары")
            if is_conduct:
                raise ValidationError("Вновь созданный турнир не может быть проведен, потому что не назначены пары, а"
                                      " результаты не присвоены")


class TournamentsAdmin(admin.ModelAdmin):
    form = TournamentsAdminForm
    list_display = ['name', 'date', 'judge1', 'judge2', 'judge3', 'judge4', 'is_build', 'is_conduct']
    list_display_links = ('name',)

    class Meta:
        model = Tournaments

    def get_actions(self, request):
        actions = super(TournamentsAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        if obj and (obj.is_build or obj.is_conduct):
            return False
        return True


class StatisticsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Statistics._meta.fields]  # вывести все поля

    class Meta:
        model = Statistics

    readonly_fields = list_display

    def has_add_permission(self, request):  # запрещает добавлять элементы (убираем кнопку добавить)
        if not request.user.is_superuser:
            return False
        else:
            return True

    def has_change_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_superuser:
            print("Да, супер пользователь")
            return False
        else:
            return True


# --- СТАТИЧЕСКИЕ МЕТОДЫ ---
# метод для проверки правильности заполненных весовых категорий
def validate_weights(w_cat, w_cat1, w_cat2):
    print("--- def validate_weights(w, w1, w2) ---")
    if w_cat1 != w_cat:
        raise forms.ValidationError('Разные весовые категории бойцов')
    if (w_cat != w_cat1) or (w_cat != w_cat2):
        raise forms.ValidationError('Выберите весовую, соответсвующую весовым категориям бойцов')


def validate_sportsmans(sp1, sp2):
    if sp1 == sp2:
        raise forms.ValidationError('Выберите второго бойца')


# получить количество пар данного данного этапа
def get_count_stages_in_queryset(queryset, stage):
    count = 0
    for pair in queryset:
        if pair.stage == stage:
            count += 1
    return count


# проверяем, присутствуют ли бойцы из вставляемой пары в предущем этапе
def validate_move_pair(prev_pairs_of_stage, sp1, sp2):
    sp1_in_prev_pairs, sp2_in_prev_pairs = False, False
    print("SP1: {0}".format(sp1))
    print("SP2: {0}".format(sp2))
    print("---- ЦИКЛ ----")
    for pair in prev_pairs_of_stage:
        print("Ц SP1: {0}".format(pair.sportsman1))
        print("Ц SP2: {0}".format(pair.sportsman2))
        if pair.sportsman1 == sp1 or pair.sportsman2 == sp1:
            sp1_in_prev_pairs = True
        if pair.sportsman1 == sp2 or pair.sportsman2 == sp2:
            sp2_in_prev_pairs = True

    if not (sp1_in_prev_pairs and sp2_in_prev_pairs):
        raise ValidationError('Бойцы, которых вы указали не учавствовали в предыдущем этапе. '
                              'Если пары на предыдущем этапе не созданы, то создайте их')


def validate_pair_vs_prev_pairs(tournament, weight_category, stage, prev_stage, sp1, sp2, id=False):
    def is_sportsman_in_next_stage(next_pairs, sp):
        for pair in next_pairs:
            if sp == pair.sportsman1 or sp == pair.sportsman2:
                return True
        return False

    winner = False
    name_looser = ''
    prev_pairs_of_stage = BattlePair.objects.filter(tournament=tournament,
                                                    weight_category=weight_category,
                                                    stage=prev_stage)
    if id:
        current_pairs = BattlePair.objects.filter(~Q(id=id), tournament=tournament, weight_category=weight_category,
                                                  stage=stage)
    else:
        current_pairs = BattlePair.objects.filter(tournament=tournament, weight_category=weight_category,
                                                  stage=stage)
    print(" #POINT 110.0 - stage: {0}".format(stage))
    print(" #POINT 110.1 - prev_stage: {0}".format(prev_stage))
    print(" #POINT 110.2 - prev_pairs_of_stage: {0}".format(prev_pairs_of_stage))
    if prev_pairs_of_stage.exists():
        sp1_in_prev_pairs, sp2_in_prev_pairs = False, False
        for pair in prev_pairs_of_stage:

            if pair.sportsman1 == sp1:
                sp1_in_prev_pairs = True
                winner = is_sportsman_in_next_stage(current_pairs, pair.sportsman2)
                if winner:
                    name_looser = sp1
            elif pair.sportsman2 == sp1:
                sp1_in_prev_pairs = True
                winner = is_sportsman_in_next_stage(current_pairs, pair.sportsman1)
                if winner:
                    name_looser = sp1
            if pair.sportsman1 == sp2:
                sp2_in_prev_pairs = True
                winner = is_sportsman_in_next_stage(current_pairs, pair.sportsman2)
                if winner:
                    name_looser = sp2
            elif pair.sportsman2 == sp2:
                sp2_in_prev_pairs = True
                winner = is_sportsman_in_next_stage(current_pairs, pair.sportsman1)
                if winner:
                    name_looser = sp2

            if sp1_in_prev_pairs and sp2_in_prev_pairs:
                break
            if winner:
                raise ValidationError('Выбран игрок ({0}), который считается проигравшим в '
                                      'предыдущем этапе, т.к. его оппонент уже учавствует в этом '
                                      'этапе'.format(name_looser))
        if not (sp1_in_prev_pairs and sp2_in_prev_pairs):
            raise ValidationError('Бойцы, которых вы указали не учавствовали в предыдущем этапе. '
                                  'Если пары на предыдущем этапе не созданы, то создайте их')


# если в след этапе есть боец из текущей пары, то ошибки не будет
def validate_move_pair_to_up(next_pairs_of_stage, sp1, sp2):
    sp_in_next_pairs = False
    print("SP1: {0}".format(sp1))
    print("SP2: {0}".format(sp2))
    print("---- ЦИКЛ ----")
    for pair in next_pairs_of_stage:
        print("Ц SP1: {0}".format(pair.sportsman1))
        print("Ц SP2: {0}".format(pair.sportsman2))
        if pair.sportsman1 == sp1 or pair.sportsman2 == sp1:
            sp_in_next_pairs = True
            break
        if pair.sportsman1 == sp2 or pair.sportsman2 == sp2:
            sp_in_next_pairs = True
            break
    if not sp_in_next_pairs:
        raise ValidationError('Т.к. в следующем этапе уже есть пары, то в этой паре должен присутсвовать'
                              ' боец из следующего этапа')


class BattlePairAdminForm(ModelForm):
    class Meta:
        model = BattlePair
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()

        # извлекаем чисты данные из формы
        weight_category = cleaned_data.get('weight_category')
        weight_category_sportsman1 = cleaned_data.get('sportsman1').weight_category
        weight_category_sportsman2 = cleaned_data.get('sportsman2').weight_category
        stage = cleaned_data.get('stage')
        tournament = cleaned_data.get('tournament')
        sp1 = cleaned_data.get('sportsman1')
        sp2 = cleaned_data.get('sportsman2')

        # проверка на то, проведен турнир уже или нет (пересохранение без изменений выдаст такое же исключение)
        if tournament.is_build:
            raise ValidationError("Нельзя сохранять/изменять пару в этом турнире, т.к. все его пары уже сформированы. "
                                  "Чтобы была возможность вносить изменения - уберите галочку в Домой>Аккаунты>Турниры "
                                  "(Сформированы пары)")
        try:
            if self.instance.id and self.instance.tournament != tournament and self.instance.is_build:
                raise ValidationError(
                    "Нельзя перемещать пару из этого турнира, т.к. его пары уже сформированы. Чтобы была "
                    "возможность переносить - уберите галочку в Домой>Аккаунты>Турниры "
                    "(Сформированы пары)")
        except:
            pass

        # закидываем в валидацию по весовым
        validate_weights(weight_category, weight_category_sportsman1, weight_category_sportsman2)
        # получаем заглушку-объект для бойца
        # sp_virt = get_void_sportsman(weight_category)

        # получаем все пары: турнир + весовая категория. Если таких нет, то считается, что будет создан
        # первая пара этого турнира этой весовой
        all_pairs_tournament = BattlePair.objects.filter(tournament=tournament, weight_category=weight_category)
        if all_pairs_tournament.exists():
            if all_pairs_tournament.count() == 1:
                if all_pairs_tournament[0].id == self.instance.id:
                    pass
                else:
                    if all_pairs_tournament[0].stage == BattlePair.STAGES[len(BattlePair.STAGES) - 1][0] == stage:
                        raise ValidationError("Финальная пара уже назначена для этого турнира этой весовой категории")
                    else:
                        # если стадии равны, то пусть добавляется. Это будет корректно всегда.
                        # если не равны - то значит сохраняем не туда, куда нужно (count = 1, а это может быть
                        if stage == all_pairs_tournament[0].stage:
                            pass
                        else:
                            # print(COUNT_STAGES_RECORD)
                            # print('key1: {0}'.format(stage))
                            # print('key2: {0}'.format(all_pairs_tournament[0].stage)) # значение тем больше,
                            # чем раньше этап
                            # print('left: {0}'.format(COUNT_STAGES_RECORD[stage]))
                            # print('right: {0}'.format(COUNT_STAGES_RECORD[all_pairs_tournament[0].stage]))
                            if COUNT_STAGES_RECORD[stage] < COUNT_STAGES_RECORD[all_pairs_tournament[0].stage]:
                                raise ValidationError("Еще не заполнена пара более раннего этапа")
                            else:
                                raise ValidationError("Уже заполнена пара более позднего этапа. Наполнение должно "
                                                      "вестись от более раннего этапа к более позднему")
            else:

                # пара которую изменяем находился в ТОМ ЖЕ ТУРНИРЕ или нет?
                obj_in_base = False
                for pair in all_pairs_tournament:
                    if pair.id == self.instance.id:
                        obj_in_base = pair
                        break

                # если в том же турнире эта пара (ДА)
                if obj_in_base:
                    # если пересохраняем в другой этап
                    if obj_in_base.stage != stage:
                        # если хотим прыгнуть в более высокую категорию
                        if COUNT_STAGES_RECORD[stage] < COUNT_STAGES_RECORD[obj_in_base.stage]:
                            # print("#point1")
                            raise ValidationError("Вы не можете перенести пару в более поздний этап, "
                                                  "т.к. предыдущий этап будет заполнен не до конца")
                        # если хотим прыгнуть в более низкую категорию. Например, если пара была удалена
                        else:
                            # print("#point2")
                            raise ValidationError("Вы не можете перенести пару в более ранний этап. "
                                                  "При необходимости создайте новую пару, которая будет относиться к "
                                                  "более раннему этапу")
                    # если остаемся в пределах данного этапа
                    else:
                        validate_pair_vs_prev_pairs(tournament, weight_category, stage, get_prev_stage(stage),
                                                    sp1, sp2, id=self.instance.id)
                        pass

                # если пара создается заново или переносится из другого турнира (НЕТ)
                else:

                    # проверяем, это пара была создана ранее или создается только что
                    pair_alien = BattlePair.objects.filter(id=self.instance.id)

                    # создана ранее
                    if pair_alien.exists():
                        # print("#point3: пара решила перекочевать из другого турнира")
                        pair_alien = pair_alien[0]

                        # проверяем последующий этап, т.к. пар в этом этапе = limit
                        if BattlePair.objects.filter(stage=pair_alien.stage,
                                                     tournament=pair_alien.tournament).count() == get_limit(
                            pair_alien.stage):

                            # если это финал, то переносить можно, т.к. это не влияет на предыдущие пары
                            if pair_alien.stage == BattlePair.STAGES[len(BattlePair.STAGES) - 1][0]:
                                # проверив - есть ли такие бойцы в предыдущих этапах
                                prev_pairs_of_stage = BattlePair.objects.filter(tournament=tournament,
                                                                                weight_category=weight_category,
                                                                                stage=get_prev_stage(stage))
                                if prev_pairs_of_stage.exists():
                                    validate_move_pair(prev_pairs_of_stage, sp1, sp2)
                            else:
                                next_stage = get_next_stage(pair_alien.stage)
                                pairs_next_stage = BattlePair.objects.filter(stage=next_stage,
                                                                             tournament=pair_alien.tournament)
                                if pairs_next_stage.exists():
                                    raise ValidationError("Вы не можете перенести эту пару из данного турнира, т.к."
                                                          " заполнен последующий этап")
                                # проверив - есть ли такие бойцы в предыдущих этапах
                        else:
                            validate_pair_vs_prev_pairs(tournament, weight_category, stage, get_prev_stage(stage),
                                                        sp1, sp2)

                    # создается заново
                    else:
                        # проверяем предыдущий этап
                        validate_pair_vs_prev_pairs(tournament, weight_category, stage, get_prev_stage(stage),
                                                    sp1, sp2)
                        next_pairs_of_stage = BattlePair.objects.filter(tournament=tournament,
                                                                        weight_category=weight_category,
                                                                        stage=get_next_stage(stage))
                        # проверяем последующий этап
                        if next_pairs_of_stage.exists():
                            validate_move_pair_to_up(next_pairs_of_stage, sp1, sp2)
        else:
            pass
            # ветвь создания новой пары
            # СОЗДАЙВАЙ, КАК ДУША ВЕЛИТ ТЕБЕ!

        # проверка того, что спортсмен уже учавствовал в этапе этого уровня и того, что выбраны разные бойцы
        sportsman1 = cleaned_data.get('sportsman1')
        sportsman2 = cleaned_data.get('sportsman2')
        count_stages = COUNT_STAGES_RECORD[stage]
        validate_sportsmans(sportsman1, sportsman2)

        # 1. Если такая пара уже есть в БД - значит редактируем текущую: edit_object  = True
        # иначе - создается новая пара и: edit_object = False
        edit_object = False
        try:
            if BattlePair.objects.get(pk=self.instance.pk):
                edit_object = True
        except:
            pass

        # работаем с имеющейся записью
        if edit_object:
            print("Редактируем")
            s1, s2 = '', ''
            pair_, sp_ = '', ''
            limit_pairs = False
            double_pairs = False
            double_sp_in_stage_1 = False
            double_sp_in_stage_2 = False
            try:
                # кол-во записей с таким же этапом в этом турнире + весовой + этапа
                stages_in_base = BattlePair.objects.filter(stage=stage, weight_category=weight_category,
                                                           tournament=tournament).count()
                # сравниваем максимально доступное кол-во записей и текущее
                if count_stages >= stages_in_base:
                    # если текущий объект и хранящийся в базе - есть один и тот же объект
                    if (BattlePair.objects.filter(Q(sportsman1=sportsman1) & Q(sportsman2=sportsman2),
                                                  pk=self.instance.pk).exists() or
                            (BattlePair.objects.filter(Q(sportsman1=sportsman2) & Q(sportsman2=sportsman1),
                                                       pk=self.instance.pk).exists())):

                        if stage == BattlePair.objects.get(pk=self.instance.pk).stage:  # проверка верна

                            if tournament != BattlePair.objects.get(pk=self.instance.pk).tournament:
                                # это значит что мы просто переносим в другой турнир
                                if count_stages == stages_in_base:
                                    limit_pairs = True
                                    print("ОШИБКА 2 ГЕНЕРИТСЯ")
                                    raise
                                else:
                                    print("#POINT 95.0 - тот же этап, но не тот турнир")
                                    # исключаем наличие целевой пары
                                    pair_ = BattlePair.objects.filter(
                                        (Q(sportsman1=sportsman1) & Q(sportsman2=sportsman2)) |
                                        (Q(sportsman2=sportsman1) & Q(sportsman1=sportsman2)),
                                        tournament=tournament)
                                    if pair_.exists():
                                        print(
                                            " #POINT 95.1 - ветвь редактирования. Исключаем возможность повторной пары".format(
                                                pair_))
                                        double_pairs = True
                                        raise

                                    # исключаем возможность повторного участия одного и того же бойца в одном и том же этапе
                                    sp_ = BattlePair.objects.filter(Q(sportsman1=sportsman1) | Q(sportsman2=sportsman1),
                                                                    tournament=tournament, stage=stage)
                                    if sp_.exists():
                                        print(
                                            " #POINT 95.2 - ветвь редактирования пары. Исключаем возможность повторного участия "
                                            "одного и того же бойца в одном и том же этапе. sp_ = {0}".format(sp_))
                                        double_sp_in_stage_1 = True
                                        raise

                                    sp_ = BattlePair.objects.filter(Q(sportsman1=sportsman2) | Q(sportsman2=sportsman2),
                                                                    tournament=tournament, stage=stage)
                                    if sp_.exists():
                                        print(
                                            " #POINT 95.3 - ветвь редактирования пары. Исключаем возможность повторного участия "
                                            "одного и того же бойца в одном и том же этапе. sp_ = {0}".format(sp_))
                                        double_sp_in_stage_2 = True
                                        raise

                            else:
                                print(" #POINT 96.0 - абсолютно не изменившаяся пара")
                                pass
                        else:  # проверка верна
                            print(" #POINT 97.0")
                            # исключаем возможность повторного участия одного и того же бойца в одном и том же этапе
                            sp_ = BattlePair.objects.filter(~Q(pk=self.instance.pk), Q(sportsman1=sportsman1) |
                                                            Q(sportsman2=sportsman1), tournament=tournament,
                                                            stage=stage)
                            if sp_.exists():
                                if COUNT_STAGES_RECORD[sp_[0].stage] == count_stages:
                                    double_sp_in_stage_1 = True
                                    raise

                            sp_ = BattlePair.objects.filter(~Q(pk=self.instance.pk), Q(sportsman1=sportsman2) |
                                                            Q(sportsman2=sportsman2), tournament=tournament,
                                                            stage=stage)
                            if sp_.exists():
                                if COUNT_STAGES_RECORD[sp_[0].stage] == count_stages:
                                    double_sp_in_stage_2 = True
                                    raise

                            if count_stages == stages_in_base:
                                limit_pairs = True
                                raise

                    else:
                        print(" #POINT 98.0")
                        # исключаем участие одной и той же пары в разных этапах
                        pair_ = BattlePair.objects.filter((Q(sportsman1=sportsman1) & Q(sportsman2=sportsman2)) |
                                                          (Q(sportsman2=sportsman1) & Q(sportsman1=sportsman2)),
                                                          tournament=tournament)
                        print(" #POINT 98.1 - pair_ = {0}".format(pair_))
                        if pair_.exists():
                            double_pairs = True
                            raise

                        sp_ = BattlePair.objects.filter(~Q(pk=self.instance.pk), (Q(sportsman1=sportsman1) |
                                                                                  Q(sportsman2=sportsman1)),
                                                        tournament=tournament, stage=stage)
                        print(" #POINT 98.2 - sp_ = {0}".format(sp_))
                        if sp_.exists():
                            if sp_[0].stage == stage:
                                double_sp_in_stage_1 = True
                                raise

                        sp_ = BattlePair.objects.filter(~Q(pk=self.instance.pk), (Q(sportsman1=sportsman2) |
                                                                                  Q(sportsman2=sportsman2)),
                                                        tournament=tournament, stage=stage)
                        print(" #POINT 98.3 - sp_ = {0}".format(sp_))
                        if sp_.exists():
                            if sp_[0].stage == stage:
                                double_sp_in_stage_2 = True
                                raise


            except:
                print(" #POINT 99")
                if limit_pairs:
                    raise ValidationError(
                        "Эта пара не может учавствовать в этапе {0}, т.к. лимит пар({1}) для этого турнира - "
                        " исчерпан. Возможно эта пара относится к другому этапу".format(stage, count_stages))
                if double_pairs:
                    print("Ошибка double_pair")
                    if pair_.exists():
                        raise ValidationError(
                            "Эта пара уже учавствовала в {0} этапе на этом турнире".format(pair_[0].stage))

                if double_sp_in_stage_1:
                    if sp_.exists():
                        raise ValidationError(
                            "{0} {1} уже учавствовал в другой паре на этом этапе в этом турнире".format(
                                sportsman1.name.first_name, sportsman1.name.last_name))

                if double_sp_in_stage_2:
                    if sp_.exists():
                        raise ValidationError(
                            "{0} {1} уже учавствовал в другой паре на этом этапе в этом турнире".format(
                                sportsman2.name.first_name, sportsman2.name.last_name))

        # работаем с вновь создаваемой записью
        else:
            print(" #POINT 100 - ветвь создания новой пары")
            # исключаем участие одной и той же пары в разных этапах
            pair_ = BattlePair.objects.filter((Q(sportsman1=sportsman1) & Q(sportsman2=sportsman2)) |
                                              (Q(sportsman2=sportsman1) & Q(sportsman1=sportsman2)),
                                              tournament=tournament)
            print(" #POINT 100.1 - ветвь создания новой пары. pair_ = {0}".format(pair_))
            if pair_.exists():
                raise ValidationError(
                    " Эта пара уже учавствовала в {0} этапе на этом турнире".format(pair_[0].stage))

            # исключаем возможность повторного участия одного и того же бойца в одном и том же этапе
            sp_ = BattlePair.objects.filter(Q(sportsman1=sportsman1) | Q(sportsman2=sportsman1),
                                            tournament=tournament, stage=stage)
            print(" #POINT 100.2 - ветвь создания новой пары. исключаем возможность повторного участия одного и того же"
                  "бойца в одном и том же этапе. sp_ = {0}".format(sp_))
            if sp_.exists() and sp_[0].stage == stage:
                raise ValidationError(
                    "{0} {1} уже учавствовал в другой паре на этом этапе в этом турнире".format(
                        sportsman1.name.first_name,
                        sportsman1.name.last_name))

            sp_ = BattlePair.objects.filter(Q(sportsman1=sportsman2) & Q(sportsman2=sportsman2),
                                            tournament=tournament, stage=stage)
            print(" #POINT 100.3 - ветвь создания новой пары. Исключаем возможность повторного участия одного и того же"
                  "бойца в одном и том же этапе. sp_ = {0}".format(sp_))
            if sp_.exists() and sp_[0].stage == stage:
                raise ValidationError("{0} {1} уже учавствовал в другой паре".format(
                    sportsman2.name.first_name,
                    sportsman2.name.last_name))

            # проверка на то, чтобы не было создано этапов больше установленного количества для play-off. Максимальное
            # количество этапов хранится в settings.COUNT_STAGES_RECORD. Так же должна учитываться категория бойцов
            if count_stages <= BattlePair.objects.filter(stage=stage, weight_category=weight_category,
                                                         tournament=tournament).count():
                print(" #POINT 100.4 - ветвь создания новой пары. исключаем возможность повторного участия одного и "
                      "того же бойца в одном и том же этапе")
                raise ValidationError(
                    "Эта пара не может учавствовать в этапе {0}, т.к. лимит пар({1}) для этого турнира - "
                    " исчерпан. Возможно эта пара относится к другому этапу".format(stage, count_stages))

        return cleaned_data


class BattlePairAdmin(admin.ModelAdmin):
    class Meta:
        model = BattlePair
        ordering = ['weight_category']

    form = BattlePairAdminForm
    list_display = ['tournament', 'stage', 'weight_category', 'sportsman1', 'sportsman2', 'freeze_rating_sportsman1',
                    'freeze_rating_sportsman2', 'delta_rating_sportsman1', 'delta_rating_sportsman2']
    exclude = ['old_sportsman1_hidden', 'old_sportsman2_hidden']
    readonly_fields = ('freeze_rating_sportsman1', 'freeze_rating_sportsman2',
                      'delta_rating_sportsman1', 'delta_rating_sportsman2')

    def get_actions(self, request):
        actions = super(BattlePairAdmin, self).get_actions(request)
        # print("SELF: {0}".format(self))
        # print("REQUEST: {0}".format(request))
        print("ACTIONS: {0}".format(actions))
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        # print("has_delete SELF: {0}".format(self))
        # print("ОБЪЕКТ: {0}".format(obj))
        if obj and obj.tournament.is_build:
            return False
        return True

    # def has_change_permission(self, request, obj=None):
    #     if obj and obj.tournament.is_build:
    #         return False
    #     return True


class ResultBattleAdminForm(ModelForm):
    class Meta:
        model = ResultsBattle
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()

        def is_sportsman_in_pair_stage(tournament, stage, sportsman):
            sp_ = BattlePair.objects.filter(Q(sportsman1=sportsman) | Q(sportsman2=sportsman),
                                            tournament=tournament, stage=stage)
            if not sp_:
                raise ValidationError("Спортсмен {0} еще не добавлен ни в одну пару".format(sportsman))

        tournament, stage, sportsman = cleaned_data.get('tournament'), cleaned_data.get('stage'), cleaned_data.get(
            'sportsman')
        # ищем объект с такими же полями
        obj = ResultsBattle.objects.filter(tournament=tournament, stage=stage, sportsman=sportsman)
        # если есть такой объект
        if obj.exists():
            # если сохраняемый и существующий один и тот же объект
            if self.instance.id == obj[0].id:
                # если пара создавалась ранее, её удалили (к которой относился результат)
                sp_ = is_sportsman_in_pair_stage(tournament, stage, sportsman)
            # если сохраняемый и существующий НЕ один и тот же объект
            else:
                raise ValidationError("Результат для: этого бойца, этого турнира, этого этапа - уже хранится в базе")

        # если НЕТ такого объекта
        else:
            # проверяем наличие такого спортспена в таком турнире, в такой паре
            is_sportsman_in_pair_stage(tournament, stage, sportsman)

        # проверка на то, проведен турнир уже или нет (пересохранение без изменений выдаст такое же исключение)
        if tournament.is_conduct:
            raise ValidationError(
                "Нельзя сохранять результат, т.к. он уже проведён. Чтобы была "
                "возможность вносить изменения - уберите галочку в Домой>Аккаунты>Турниры "
                "(Проведение турнира)")
        try:  # это не обязательно т.к. прав на изменение не будет при проведенном турнире
            if self.instance.id and self.instance.tournament != tournament and self.instance.is_conduct:
                raise ValidationError(
                    "Нельзя перемещать результат из этого турнира, т.к. он уже проведён. Чтобы была "
                    "возможность переносить - уберите галочку в Домой>Аккаунты>Турниры "
                    "(Проведение турнира)")
        except:
            pass

        # проверка на то, сформированы ли уже пары или нет в турнире, в который переносим
        if not tournament.is_build:
            raise ValidationError(
                "Нельзя сохранять результат, т.к. пары еще не сформированы")

        # # 17.05.20 - 17.57
        # # добавляем проверки:
        # # 1. Получаем предыдущую стадию, и проверяем заполнены ли пары предыдущего этапа. ПРАВКА - проверка эта не
        # # нужна, т.к.пары должны быть сформированы. Иначе мы бы не смогли вносить результаты
        # prev_stage = get_prev_stage(stage)
        # # 2. Проверить заполненность результатов предыдущей стадии. Если нет - то исключение. Чтобы проверить,
        # # пред.стадия есть или нет, нужно через exists() проверить наличие пары пред. стадии. Далее проверить кол-во
        # # записей о результатах, предыдущего этапа если exists() даст истину
        # prev_pairs = BattlePair.objects.filter(stage=prev_stage, tournament=tournament,
        #                                        weight_category=sportsman.weight_category)
        # print(" #POINT 120.0 - prev_stage: {0}".format(prev_stage))
        # print(" #POINT 120.1 - prev_pairs: {0}".format(prev_pairs))
        # if prev_pairs.exists():
        #     # всё таки проверим, чтобы пары пред.этапа были заполнены на максимум
        #     if prev_pairs.count() == COUNT_STAGES_RECORD[prev_stage]:
        #         print(" #POINT 120.2 - : {0}".format(prev_pairs))
        #         # проверим количество РЕЗУЛЬТАТОВ пред этапа, этого турнира, этой весовой
        #         results_prev_stage = ResultsBattle.objects.filter(tournament=tournament, stage=prev_stage,
        #                                                           sportsman__weight_category=sportsman.weight_category)
        #         # если кол-во результатов предыдущего этапа заполнено по максимуму
        #         if results_prev_stage.count() == COUNT_STAGES_RECORD[prev_stage] * 2:
        #             # то ищем пару из пред. этапа
        #             pair_ = prev_pairs.filter(Q(sportsman1=sportsman) | Q(sportsman2=sportsman))[0]
        #             # sp1, sp2 = pair_.sportsman1, pair_.sportsman2
        #             # if sp1 == sportsman:
        #             #     pass
        #         else:
        #             raise ValidationError("")
        #
        #     else:
        #         raise ValidationError("Пары на предыдущей стадии не заполнены. Отмените формирование пар, добавьте "
        #                               "необходимые пары, и снова сформируйте пары.")
        # else:
        #     pass


class ResultsBattleAdmin(admin.ModelAdmin):
    class Meta:
        model = ResultsBattle

    def get_actions(self, request):
        actions = super(ResultsBattleAdmin, self).get_actions(request)
        # print("SELF: {0}".format(self))
        # print("REQUEST: {0}".format(request))
        print(" #POINT 135.1 ACTIONS: {0}".format(actions))
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        print(" #POINT 135.0 - obj: {0}".format(obj))
        if obj and obj.tournament.is_conduct:
            return False
        return True

    # def has_change_permission(self, request, obj=None):
    #     if obj and obj.tournament.is_conduct:
    #         return False
    #     return True

    form = ResultBattleAdminForm
    list_filter = ('stage', 'tournament',)
    list_display = ['tournament', 'sportsman', 'stage', 'pair',
                    'summ_points', 'penalty_points', 'knockout', 'disqualification']  # вывести все поля

    def pair(self, obj):
        print(" #POINT 135.2 - obj: {0}".format(obj))
        print(" #POINT 135.3 - self: {0}".format(self))
        pair = BattlePair.objects.get(Q(sportsman1=obj.sportsman) | Q(sportsman2=obj.sportsman),
                                         tournament=obj.tournament,
                                         stage=obj.stage)
        return pair
    pair.short_description = 'Пара'


    # list_display = ['sportsman', 'start_handstrike', 'start_kicks', 'start_handstrikes_tohead', 'start_kicks_tohead',
    # 'start_rotate_kicks']
    fieldsets = [
        (None, {'fields': [('tournament', 'sportsman', 'stage')]}),
        ('Судья 1', {'fields': [('judge1_handstrike', 'judge1_kicks', 'judge1_handstrikes_tohead',
                                 'judge1_kicks_tohead', 'judge1_rotate_kicks')]}),
        ('Судья 2', {'fields': [('judge2_handstrike', 'judge2_kicks', 'judge2_handstrikes_tohead',
                                 'judge2_kicks_tohead', 'judge2_rotate_kicks')]}),
        ('Судья 3', {'fields': [('judge3_handstrike', 'judge3_kicks', 'judge3_handstrikes_tohead',
                                 'judge3_kicks_tohead', 'judge3_rotate_kicks')]}),
        ('Судья 4', {'fields': [('judge4_handstrike', 'judge4_kicks', 'judge4_handstrikes_tohead',
                                 'judge4_kicks_tohead', 'judge4_rotate_kicks')]}),
        (None, {'fields': ['penalty_points']}),
        (None, {'fields': [('knockout', 'disqualification')]}),
        (None, {'fields': ['summ_points']}),
    ]

    readonly_fields = ('summ_points',)
    # exclude = ('start_handstrike', 'start_kicks', 'start_handstrikes_tohead', 'start_kicks_tohead',
    # 'start_rotate_kicks')
    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "tournament":
    #         kwargs["queryset"] = BattlePair.objects.filter(tournament=db_field)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SettingsSelectionsAdminForm(ModelForm):
    class Meta:
        model = ResultsBattle
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        # проверка настроек для подбора соперника
        # левых
        if cleaned_data.get('border_x_top_left') >= 0:
            raise ValidationError('\'Верхняя левая граница\' должна быть отрицательной')
        if cleaned_data.get('border_x_bottom_left') >= 0:
            raise ValidationError('\'Нижняя левая граница\' должна быть отрицательной')
        if cleaned_data.get('border_x_top_left') < cleaned_data.get('border_x_bottom_left'):
            raise ValidationError('\'Верхняя левая граница\' должна быть больше нижней левой')
        # правых
        if cleaned_data.get('border_x_top_right') <= 0:
            raise ValidationError('\'Верхняя правая граница\' должна быть положительной')
        if cleaned_data.get('border_x_bottom_right') <= 0:
            raise ValidationError('\'Нижняя правая граница\' должна быть положительной')
        if cleaned_data.get('border_x_top_right') > cleaned_data.get('border_x_bottom_right'):
            raise ValidationError('\'Верхняя правая граница\' должна быть меньше нижней правой')

        # проверка названия и мю
        if cleaned_data.get('title') == None:
            raise ValidationError('Введите название')
        if not (0 < cleaned_data.get('mu') < 1):
            raise ValidationError('M должно находиться в пределах от 0 до 1 (рекоммендуется 0.5 +- 0.1)')

        # проверка границ для прокачки рук
        if cleaned_data.get('border_hand_left') > cleaned_data.get('border_hand_right'):
            raise ValidationError('\'Левая граница должна быть меньше правой')
        if not (0 < (cleaned_data.get('border_hand_left') and cleaned_data.get('border_hand_right')) < 100):
            raise ValidationError('\'Левая граница\' и \'Правая граница\' должны находиться в пределах от 0 до 100')

        # проверка границ для прокачки ног
        if cleaned_data.get('border_foot_left') > cleaned_data.get('border_foot_right'):
            raise ValidationError('\'Левая граница должна быть меньше правой')
        if not (0 < (cleaned_data.get('border_foot_left') and cleaned_data.get('border_foot_right')) < 100):
            raise ValidationError('\'Левая граница\' и \'Правая граница\' должны находиться в пределах от 0 до 100')

        # проверка активации настройки
        setting = SettingsSelections.objects.filter(active=True)
        if cleaned_data.get('active'):
            print(' #point 310.1 ')
            if setting.exists():
                print(setting)
                el = setting[0]
                el.active = False
                # setting.update(active=False)      # обновляет все записи
                el.save()
                print(setting)
        else:
            if setting.exists():
                print(' #point 310.2 ')
                if self.instance.id == setting[0].id:
                    setting = SettingsSelections.objects.get(id=1)
                    setting.active = True
                    setting.save()
            else:
                print(' #point 310.3 ')
                setting = SettingsSelections.objects.get(id=1)
                setting.active = True
                setting.save()


class SettingsSelectionsAdmin(admin.ModelAdmin):
    form = SettingsSelectionsAdminForm
    list_display = ['title', 'active']
    class Meta:
        model = SettingsSelections
        fields = '__all__'

    def get_actions(self, request):
        actions = super(SettingsSelectionsAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_change_permission(self, request, obj=None):
        if obj != None:
            if obj.id == 1:
                return False
            else:
                return True

    def has_delete_permission(self, request, obj=None):
        if obj != None:
            if obj.id == 1:
                return False
            else:
                return True

    fieldsets = [
        ('Подбор соперника для соревнований',
         {'fields': [('border_x_top_left', 'border_x_bottom_left', 'border_x_top_right', 'border_x_bottom_right')]}),
        ('Подбор соперника для работы руками',
         {'fields': [('border_hand_left', 'border_hand_right')]}),
        ('Подбор соперника для работы ногами',
         {'fields': [('border_foot_left', 'border_foot_right')]}),
        ('Общее',
         {'fields': ['title', 'mu', 'active']}),
    ]


admin.site.register(Belts, BeltsAdmin)
admin.site.register(WeightCategory, WeightCategoryAdmin)
admin.site.register(Sportsman, SportsmanAdmin)
admin.site.register(Tournaments, TournamentsAdmin)
admin.site.register(Statistics, StatisticsAdmin)
admin.site.register(BattlePair, BattlePairAdmin)
admin.site.register(ResultsBattle, ResultsBattleAdmin)
admin.site.register(SettingsSelections, SettingsSelectionsAdmin)
