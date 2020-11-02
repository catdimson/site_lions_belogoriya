from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save, post_save, post_delete  # сигнал перед,после сохранения
from django.utils.text import slugify           # для создания слага
from transliterate import translit              # перевод из кириллицы в латиницу
from django.urls import reverse                 # для создания ссылок
import math
from datetime import date
from site_lions_belg.settings import STAGES
from django.contrib.auth.models import User


def get_STAGES():
    return STAGES


class Belts(models.Model):
    class Meta:
        verbose_name = 'Пояс'
        verbose_name_plural = 'Пояса'
        db_table = 'account_belts'

    color = models.CharField(max_length=20, blank=False, null=False, verbose_name='Цвет пояса')

    def __str__(self):
        return self.color


class WeightCategory(models.Model):
    class Meta:
        verbose_name = 'Весовая категория'
        verbose_name_plural = 'Весовые категории'
        db_table = 'account_weight_category'

    weight_category = models.CharField(max_length=10, blank=False, null=False, verbose_name='Весовая категория')

    def __str__(self):
        return self.weight_category


def photo_folder(instance, filename):
    filename = instance.name.username + '.' + filename.split('.')[1]   # slug + расширение
    return "{0}/{1}".format(instance.name.username, filename)          # где сохранится (создастся папка для этого)


class Sportsman(models.Model):
    class Meta:
        verbose_name = 'Спортсмен'
        verbose_name_plural = 'Спортсмены'
        db_table = 'account_sportsman'

    name = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                primary_key=True, verbose_name='Спортсмен')
    slug = models.SlugField(blank=True, verbose_name="Слаг")
    age = models.SmallIntegerField(blank=True, null=True, verbose_name='Возраст')
    phone = models.CharField(max_length=12, blank=True, null=True, verbose_name='Телефон')
    rating = models.FloatField(default=1000.00, verbose_name='Рейтинг')
    belt = models.ForeignKey(Belts, on_delete=models.SET_NULL, null=True, verbose_name='Пояс')
    weight_category = models.ForeignKey(WeightCategory, on_delete=models.SET_NULL, null=True,
                                        verbose_name='Весовая категория')
    photo = models.ImageField(upload_to=photo_folder, blank=True)
    # fake = models.BooleanField(default=False)

    # def save(self, *args, **kwargs):
    #     self.rating = round(self.rating, 2)
    #     super(Sportsman, self).save(*args, **kwargs)

    def __str__(self):
        return "{0} {1} ({2})".format(self.name.first_name, self.name.last_name, self.weight_category)

    def get_absolute_url(self):
        return reverse('account:account_index', kwargs={'sportsman_name': self.slug})

    def get_update_url(self):
        return reverse('account:account_edit', kwargs={'sportsman_name': self.slug})


def pre_save_sportsman_slug(sender, instance, *args, **kwargs):
    slug = slugify(translit(instance.name.username, 'ru', reversed=True))
    instance.slug = slug


def post_save_sportsman(sender, instance, *args, **kwargs):
    try:
        Statistics.objects.get(sportsman=instance)
        print("Есть такой в статистике")

    except:
        print("Нет такого в статистике")
        w = instance.weight_category.weight_category.replace(' ', '_')
        if not instance.name.username == 'Нет_бойца__{0}'.format(w):
            sportsman_statistic = Statistics(
                sportsman=instance,
                handstrikes=0,
                kicks=0,
                handstrikes_tohead=0,
                kicks_tohead=0,
                rotate_kicks=0,
                knockouts=0
            )
            sportsman_statistic.save()


pre_save.connect(pre_save_sportsman_slug, sender=Sportsman)
post_save.connect(post_save_sportsman, sender=Sportsman)


class Statistics(models.Model):
    class Meta:
        verbose_name = 'Статистика'
        verbose_name_plural = 'Статистика'
        db_table = 'account_statistics'

    sportsman = models.OneToOneField(Sportsman, on_delete=models.CASCADE, primary_key=True, verbose_name='Спортсмен')
    handstrikes = models.SmallIntegerField(blank=True, null=True, verbose_name='Руками в корпус')
    kicks = models.SmallIntegerField(blank=True, null=True, verbose_name='Ногами в корпус')
    handstrikes_tohead = models.SmallIntegerField(blank=True, null=True, verbose_name='Руками в голову')
    kicks_tohead = models.SmallIntegerField(blank=True, null=True, verbose_name='Ногами в голову')
    rotate_kicks = models.SmallIntegerField(blank=True, null=True, verbose_name='С разворота в голову')
    knockouts = models.SmallIntegerField(blank=True, null=True, verbose_name='Нокаутов')

    def __str__(self):
        return self.sportsman.name.username


class SettingsSelections(models.Model):
    class Meta:
        verbose_name = 'Настройка подбора соперника'
        verbose_name_plural = 'Настройки подбора соперников'
        db_table = 'account_settings_selection'

    # заголовок
    title = models.CharField(max_length=30, blank=True, null=True, verbose_name='Название')
    # для соревнований
    border_x_top_left = models.FloatField(blank=False, null=False, verbose_name='Верхняя левая граница',
        help_text='Указывает верхнюю левую границу трапецевидной функции нечёткого множества. Её значение должно быть '
              'отрицательным и меньше нижней левой границы этой функции', default=-75)
    border_x_bottom_left = models.FloatField(blank=False, null=False, verbose_name='Нижняя левая граница',
        help_text='Указывает верхнюю левую границу трапецевидной функции нечёткого множества. Её значение должнго быть '
              'отрицательным и больше верхней границы этой функции', default=-150)
    border_x_top_right = models.FloatField(blank=False, null=False, verbose_name='Верхняя правая граница',
        help_text='Указывает верхнюю правую границу трапецевидной функции нечёткого множества. Её значение должно быть '
              'положительным и меньше нижней правой границы этой функции', default=150)
    border_x_bottom_right = models.FloatField(blank=False, null=False, verbose_name='Нижняя правая граница',
        help_text='Указывает верхнюю правую границу трапецевидной функции нечёткого множества. Её значение должнго быть '
              'положительным и больше нижней границы этой функции', default=225)
    # для рук
    border_hand_left = models.FloatField(blank=False, null=False, verbose_name='Левая граница',
        help_text='Находится в пределах от 0 до 100. Должна быть меньше правой границы', default=50)
    border_hand_right = models.FloatField(blank=False, null=False, verbose_name='Правая граница',
        help_text='Находится в пределах от 0 до 100. Должна быть больше левой границы', default=70)
    # для ног
    border_foot_left = models.FloatField(blank=False, null=False, verbose_name='Левая граница',
        help_text='Находится в пределах от 0 до 100. Должна быть меньше правой границы', default=30)
    border_foot_right = models.FloatField(blank=False, null=False, verbose_name='Правая граница',
        help_text='Находится в пределах от 0 до 100. Должна быть больше левой границы', default=50)
    # общее
    mu = models.FloatField(blank=False, null=False, verbose_name='μ',
        help_text='Находится в пределах от 0 до 1', default=0.5)
    active = models.BooleanField(blank=True, verbose_name='Активная')

    def __str__(self):
        return self.title


def post_delete_setting(sender, instance, *args, **kwargs):
    if instance.active == True:
        setting = SettingsSelections.objects.get(id=1)
        setting.active = True
        setting.save()


post_delete.connect(post_delete_setting, sender=SettingsSelections)


class Tournaments(models.Model):
    class Meta:
        verbose_name = 'Турнир'
        verbose_name_plural = 'Турниры'
        db_table = 'account_tournaments'

    name = models.CharField(max_length=80, verbose_name='Название турнира',
                            help_text='Не забудьте в названии турнира указать год проведения')
    date = models.DateField(blank=False, default=date.today)
    judge1 = models.CharField(max_length=100, verbose_name='Судья 1')
    judge2 = models.CharField(max_length=100, verbose_name='Судья 2')
    judge3 = models.CharField(max_length=100, verbose_name='Судья 3')
    judge4 = models.CharField(max_length=100, verbose_name='Судья 4')
    # Чекбоксы - is_build: построен, is_conduct - проведен
    is_build = models.BooleanField(default=False, verbose_name="Пары сформированы",
                                   help_text="Это поле позволяет отрисовывать турнирную сетку в личном кабинете"
                                             " спортсмена. Необходимо, чтобы перед установкой были корректно "
                                             "сформированы все пары весовых категорий")
    is_conduct = models.BooleanField(default=False, verbose_name="Турнир проведен",
                                     help_text="Необходмо, чтобы перед установкой пары были сформированы")

    def __str__(self):
        return "{0}".format(self.name)


class BattlePair(models.Model):
    class Meta:
        verbose_name = 'Пара'
        verbose_name_plural = 'Пары'
        db_table = 'account_battle_pair'
        unique_together = ['stage', 'tournament', 'sportsman1', 'sportsman2']

    STAGES = get_STAGES()

    stage = models.CharField(max_length=9, choices=STAGES, default=STAGES[0], verbose_name='Этап')
    tournament = models.ForeignKey(Tournaments, on_delete=models.CASCADE, verbose_name='Турнир')
    weight_category = models.ForeignKey(WeightCategory, on_delete=models.SET_NULL, null=True, verbose_name='Весовая '
                                                                                                           'категория')
    sportsman1 = models.ForeignKey(Sportsman, on_delete=models.CASCADE, default="", verbose_name='1-ый спарингующийся',
                                   related_name='man1')
    sportsman2 = models.ForeignKey(Sportsman, on_delete=models.CASCADE, default="", verbose_name='2-ый спарингующийся',
                                   related_name='man2')
    old_sportsman1_hidden = models.ForeignKey(Sportsman, on_delete=models.SET_NULL, null=True,
                                              blank=True, related_name='man1_hidden')
    old_sportsman2_hidden = models.ForeignKey(Sportsman, on_delete=models.SET_NULL, null=True,
                                              blank=True, related_name='man2_hidden')
    freeze_rating_sportsman1 = models.FloatField(verbose_name='Рейтинт 1-го')
    freeze_rating_sportsman2 = models.FloatField(verbose_name='Рейтинт 2-го')
    delta_rating_sportsman1 = models.FloatField(verbose_name='Приращение 1-го', default=0.00)
    delta_rating_sportsman2 = models.FloatField(verbose_name='Приращение 2-го', default=0.00)

    def save(self, *args, **kwargs):
        self.freeze_rating_sportsman1 = round(self.freeze_rating_sportsman1, 2)
        self.freeze_rating_sportsman2 = round(self.freeze_rating_sportsman2, 2)
        self.delta_rating_sportsman1 = round(self.delta_rating_sportsman1, 2)
        self.delta_rating_sportsman2 = round(self.delta_rating_sportsman2, 2)
        super(BattlePair, self).save(*args, **kwargs)

    def __str__(self):
        return "{0} vs {1} ({2}). Этап: {3}. ({4})".format(self.sportsman1.name.last_name + " " +
        self.sportsman1.name.first_name, self.sportsman2.name.last_name + " " + self.sportsman2.name.first_name,
                                              self.sportsman1.weight_category, self.stage, self.tournament)


def pre_save_battle_pair(sender, instance, *args, **kwargs):
    try:
        BattlePair.objects.get(pk=instance.pk)
        # print("Есть такая пара.")
    except:
        instance.freeze_rating_sportsman1 = instance.sportsman1.rating
        instance.freeze_rating_sportsman2 = instance.sportsman2.rating
    instance.old_sportsman1_hidden = instance.sportsman1
    instance.old_sportsman2_hidden = instance.sportsman2
        # print("Нет такой пары. Но добавлена. Их рейтинг: " + str(instance.sportsman1.rating) + " и " + str(instance.sportsman2.rating))


pre_save.connect(pre_save_battle_pair, sender=BattlePair)


class ResultsBattle(models.Model):
    class Meta:
        verbose_name = 'Результат боя'
        verbose_name_plural = 'Результаты боёв'
        db_table = 'account_results_battle'

    STAGES = get_STAGES()

    tournament = models.ForeignKey(Tournaments, on_delete=models.CASCADE, verbose_name='Турнир')
    sportsman = models.ForeignKey(Sportsman, on_delete=models.CASCADE, verbose_name='Спортсмен')
    # pair = models.ForeignKey(BattlePair, on_delete=models.CASCADE, verbose_name='Пара')
    stage = models.CharField(max_length=9, choices=STAGES, default=STAGES[0][0], verbose_name='Этап')
    judge1_handstrike = models.SmallIntegerField(default=0, verbose_name='Руками в корпус (Судья №1)')
    judge1_kicks = models.SmallIntegerField(default=0, verbose_name='Ногами в корпус (Судья №1)')
    judge1_handstrikes_tohead = models.SmallIntegerField(default=0, verbose_name='Руками в голову (Судья №1)')
    judge1_kicks_tohead = models.SmallIntegerField(default=0, verbose_name='Ногами в голову (Судья №1)')
    judge1_rotate_kicks = models.SmallIntegerField(default=0, verbose_name='С разворота в голову (Судья №1)')
    judge2_handstrike = models.SmallIntegerField(default=0, verbose_name='Руками в корпус (Судья №2)')
    judge2_kicks = models.SmallIntegerField(default=0, verbose_name='Ногами в корпус (Судья №2)')
    judge2_handstrikes_tohead = models.SmallIntegerField(default=0, verbose_name='Руками в голову (Судья №2)')
    judge2_kicks_tohead = models.SmallIntegerField(default=0, verbose_name='Ногами в голову (Судья №2)')
    judge2_rotate_kicks = models.SmallIntegerField(default=0, verbose_name='С разворота в голову (Судья №2)')
    judge3_handstrike = models.SmallIntegerField(default=0, verbose_name='Руками в корпус (Судья №3)')
    judge3_kicks = models.SmallIntegerField(default=0, verbose_name='Ногами в корпус (Судья №3)')
    judge3_handstrikes_tohead = models.SmallIntegerField(default=0, verbose_name='Руками в голову (Судья №3)')
    judge3_kicks_tohead = models.SmallIntegerField(default=0, verbose_name='Ногами в голову (Судья №3)')
    judge3_rotate_kicks = models.SmallIntegerField(default=0, verbose_name='С разворота в голову (Судья №3)')
    judge4_handstrike = models.SmallIntegerField(default=0, verbose_name='Руками в корпус (Судья №4)')
    judge4_kicks = models.SmallIntegerField(default=0, verbose_name='КНогами в корпус (Судья №4)')
    judge4_handstrikes_tohead = models.SmallIntegerField(default=0, verbose_name='Руками в голову (Судья №4)')
    judge4_kicks_tohead = models.SmallIntegerField(default=0, verbose_name='Ногами в голову (Судья №4)')
    judge4_rotate_kicks = models.SmallIntegerField(default=0, verbose_name='С разворота в голову (Судья №4)')
    penalty_points = models.SmallIntegerField(default=0, verbose_name='Штрафные очки')

    start_handstrike = models.SmallIntegerField(default=0)
    start_kicks = models.SmallIntegerField(default=0)
    start_handstrikes_tohead = models.SmallIntegerField(default=0)
    start_kicks_tohead = models.SmallIntegerField(default=0)
    start_rotate_kicks = models.SmallIntegerField(default=0)
    start_knockout = models.SmallIntegerField(default=0)

    knockout = models.BooleanField(verbose_name='Нокаутировал')
    disqualification = models.BooleanField(verbose_name='Дискваливицирован')
    is_not = models.BooleanField(verbose_name='Болел/Отсутствовал',
                                 help_text='Наличие этого поля присвоит автопоражение спортсмену, но не '
                                           'повлияет на его рейтинг', default=False)
    summ_points = models.SmallIntegerField(blank=True, null=True, default=0, verbose_name='Итого очков')

    def __str__(self):
        return "Спортсмен: {0}. {1}".format(self.sportsman.name.first_name, self.stage)


def pre_save_result_battles_summ(sender, instance, *args, **kwargs):
    # считаем очки за удары
    handstrike = math.ceil((instance.judge1_handstrike + instance.judge2_handstrike +
                                   instance.judge3_handstrike + instance.judge4_handstrike) / 4)
    kicks = math.ceil((instance.judge1_kicks + instance.judge2_kicks + instance.judge3_kicks +
                               instance.judge4_kicks) / 4)
    handstrikes_tohead = math.ceil((instance.judge1_handstrikes_tohead + instance.judge2_handstrikes_tohead +
                                          instance.judge3_handstrikes_tohead + instance.judge4_handstrikes_tohead) / 4)
    kicks_tohead = math.ceil((instance.judge1_kicks_tohead + instance.judge2_kicks_tohead + instance.judge3_kicks_tohead +
                                        instance.judge4_kicks_tohead) / 4)
    rotate_kicks = math.ceil((instance.judge1_rotate_kicks + instance.judge2_rotate_kicks + instance.judge3_rotate_kicks +
                                    instance.judge4_rotate_kicks) / 4)
    knockout = int(instance.knockout)

    instance.summ_points = handstrike + kicks * 2 + handstrikes_tohead * 2 + \
                           kicks_tohead * 3 + rotate_kicks * 4 - instance.penalty_points

    try:
        # если объект уже был в базе
        ResultsBattle.objects.get(pk=instance.pk)

        statistic = Statistics.objects.get(sportsman=instance.sportsman)

        statistic.handstrikes = statistic.handstrikes - instance.start_handstrike + handstrike
        instance.start_handstrike = handstrike

        statistic.kicks = statistic.kicks - instance.start_kicks + kicks
        instance.start_kicks = kicks

        statistic.handstrikes_tohead = statistic.handstrikes_tohead - instance.start_handstrikes_tohead + handstrikes_tohead
        instance.start_handstrikes_tohead = handstrikes_tohead

        statistic.kicks_tohead = statistic.kicks_tohead - instance.start_kicks_tohead + kicks_tohead
        instance.start_kicks_tohead = kicks_tohead

        statistic.rotate_kicks = statistic.rotate_kicks - instance.start_rotate_kicks + rotate_kicks
        instance.start_rotate_kicks = rotate_kicks

        statistic.knockouts = statistic.knockouts - instance.start_knockout + knockout
        instance.start_knockout = knockout

        statistic.save()

    except:
        # если только создался объект
        # считаем удары
        instance.start_handstrike = math.ceil((instance.judge1_handstrike + instance.judge2_handstrike +
                                               instance.judge3_handstrike + instance.judge4_handstrike) / 4)
        instance.start_kicks = math.ceil((instance.judge1_kicks + instance.judge2_kicks + instance.judge3_kicks +
                                          instance.judge4_kicks) / 4)
        instance.start_handstrikes_tohead = math.ceil(
            (instance.judge1_handstrikes_tohead + instance.judge2_handstrikes_tohead +
             instance.judge3_handstrikes_tohead + instance.judge4_handstrikes_tohead) / 4)
        instance.start_kicks_tohead = math.ceil(
            (instance.judge1_kicks_tohead + instance.judge2_kicks_tohead + instance.judge3_kicks_tohead +
             instance.judge4_kicks_tohead) / 4)
        instance.start_rotate_kicks = math.ceil(
            (instance.judge1_rotate_kicks + instance.judge2_rotate_kicks + instance.judge3_rotate_kicks +
             instance.judge4_rotate_kicks) / 4)
        instance.start_knockout = int(instance.knockout)

        # и заноcим их в запись статистики
        statistic = Statistics.objects.get(sportsman=instance.sportsman)
        statistic.handstrikes += instance.start_handstrike
        statistic.kicks += instance.start_kicks
        statistic.handstrikes_tohead += instance.start_handstrikes_tohead
        statistic.kicks_tohead += instance.start_kicks_tohead
        statistic.rotate_kicks += instance.start_rotate_kicks
        statistic.knockouts += instance.start_knockout
        statistic.save()


def post_delete_result_battles(sender, instance, *args, **kwargs):
    # обновляем статистику, после удаления записи боя
    statistic = Statistics.objects.get(sportsman=instance.sportsman)

    statistic.handstrikes -= instance.start_handstrike
    statistic.kicks -= instance.start_kicks
    statistic.handstrikes_tohead -= instance.start_handstrikes_tohead
    statistic.kicks_tohead -= instance.start_kicks_tohead
    statistic.rotate_kicks -= instance.start_rotate_kicks
    statistic.knockouts -= instance.start_knockout

    statistic.save()


pre_save.connect(pre_save_result_battles_summ, sender=ResultsBattle)
post_delete.connect(post_delete_result_battles, sender=ResultsBattle)