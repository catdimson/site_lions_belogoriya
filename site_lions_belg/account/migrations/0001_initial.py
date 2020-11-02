# Generated by Django 2.2.12 on 2020-05-12 18:03

import account.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Belts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=20, verbose_name='Цвет пояса')),
            ],
            options={
                'db_table': 'account_belts',
                'verbose_name': 'Пояс',
                'verbose_name_plural': 'Пояса',
            },
        ),
        migrations.CreateModel(
            name='Sportsman',
            fields=[
                ('name', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='Спортсмен')),
                ('slug', models.SlugField(blank=True, verbose_name='Слаг')),
                ('age', models.SmallIntegerField(blank=True, null=True, verbose_name='Возраст')),
                ('phone', models.CharField(blank=True, max_length=12, null=True, verbose_name='Телефон')),
                ('rating', models.IntegerField(default=1000, verbose_name='Рейтинг')),
                ('change_rating', models.IntegerField(default=0, verbose_name='Динамика рейтинга')),
                ('photo', models.ImageField(blank=True, upload_to=account.models.photo_folder)),
                ('belt', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.Belts', verbose_name='Пояс')),
            ],
            options={
                'db_table': 'account_sportsman',
                'verbose_name': 'Спортсмен',
                'verbose_name_plural': 'Спортсмены',
            },
        ),
        migrations.CreateModel(
            name='Tournaments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, verbose_name='Название турнира')),
                ('year', models.SmallIntegerField(verbose_name='Год')),
                ('judge1', models.CharField(max_length=100, verbose_name='Судья 1')),
                ('judge2', models.CharField(max_length=100, verbose_name='Судья 2')),
                ('judge3', models.CharField(max_length=100, verbose_name='Судья 3')),
                ('judge4', models.CharField(max_length=100, verbose_name='Судья 4')),
            ],
            options={
                'db_table': 'account_tournaments',
                'verbose_name': 'Турнир',
                'verbose_name_plural': 'Турниры',
            },
        ),
        migrations.CreateModel(
            name='WeightCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight_category', models.CharField(max_length=10, verbose_name='Весовая категория')),
            ],
            options={
                'db_table': 'account_weight_category',
                'verbose_name': 'Весовая категория',
                'verbose_name_plural': 'Весовые категории',
            },
        ),
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('sportsman', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='account.Sportsman', verbose_name='Спортсмен')),
                ('handstrikes', models.SmallIntegerField(blank=True, null=True, verbose_name='Руками в корпус')),
                ('kicks', models.SmallIntegerField(blank=True, null=True, verbose_name='Ногами в корпус')),
                ('handstrikes_tohead', models.SmallIntegerField(blank=True, null=True, verbose_name='Руками в голову')),
                ('kicks_tohead', models.SmallIntegerField(blank=True, null=True, verbose_name='Ногами в голову')),
                ('rotate_kicks', models.SmallIntegerField(blank=True, null=True, verbose_name='С разворота в голову')),
                ('knockouts', models.SmallIntegerField(blank=True, null=True, verbose_name='Нокаутов')),
            ],
            options={
                'db_table': 'account_statistics',
                'verbose_name': 'Статистика',
                'verbose_name_plural': 'Статистика',
            },
        ),
        migrations.AddField(
            model_name='sportsman',
            name='weight_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.WeightCategory', verbose_name='Весовая категория'),
        ),
        migrations.CreateModel(
            name='ResultsBattle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stage', models.CharField(choices=[('1/16', '1/16'), ('1/8', '1/8'), ('1/4', '1/4'), ('1/2', '1/2'), ('Финал', 'Финал')], default='1/16', max_length=9, verbose_name='Этап')),
                ('judge1_handstrike', models.SmallIntegerField(default=0, verbose_name='Руками в корпус (Судья №1)')),
                ('judge1_kicks', models.SmallIntegerField(default=0, verbose_name='Ногами в корпус (Судья №1)')),
                ('judge1_handstrikes_tohead', models.SmallIntegerField(default=0, verbose_name='Руками в голову (Судья №1)')),
                ('judge1_kicks_tohead', models.SmallIntegerField(default=0, verbose_name='Ногами в голову (Судья №1)')),
                ('judge1_rotate_kicks', models.SmallIntegerField(default=0, verbose_name='С разворота в голову (Судья №1)')),
                ('judge2_handstrike', models.SmallIntegerField(default=0, verbose_name='Руками в корпус (Судья №2)')),
                ('judge2_kicks', models.SmallIntegerField(default=0, verbose_name='Ногами в корпус (Судья №2)')),
                ('judge2_handstrikes_tohead', models.SmallIntegerField(default=0, verbose_name='Руками в голову (Судья №2)')),
                ('judge2_kicks_tohead', models.SmallIntegerField(default=0, verbose_name='Ногами в голову (Судья №2)')),
                ('judge2_rotate_kicks', models.SmallIntegerField(default=0, verbose_name='С разворота в голову (Судья №2)')),
                ('judge3_handstrike', models.SmallIntegerField(default=0, verbose_name='Руками в корпус (Судья №3)')),
                ('judge3_kicks', models.SmallIntegerField(default=0, verbose_name='Ногами в корпус (Судья №3)')),
                ('judge3_handstrikes_tohead', models.SmallIntegerField(default=0, verbose_name='Руками в голову (Судья №3)')),
                ('judge3_kicks_tohead', models.SmallIntegerField(default=0, verbose_name='Ногами в голову (Судья №3)')),
                ('judge3_rotate_kicks', models.SmallIntegerField(default=0, verbose_name='С разворота в голову (Судья №3)')),
                ('judge4_handstrike', models.SmallIntegerField(default=0, verbose_name='Руками в корпус (Судья №4)')),
                ('judge4_kicks', models.SmallIntegerField(default=0, verbose_name='КНогами в корпус (Судья №4)')),
                ('judge4_handstrikes_tohead', models.SmallIntegerField(default=0, verbose_name='Руками в голову (Судья №4)')),
                ('judge4_kicks_tohead', models.SmallIntegerField(default=0, verbose_name='Ногами в голову (Судья №4)')),
                ('judge4_rotate_kicks', models.SmallIntegerField(default=0, verbose_name='С разворота в голову (Судья №4)')),
                ('penalty_points', models.SmallIntegerField(default=0, verbose_name='Штрафные очки')),
                ('start_handstrike', models.SmallIntegerField(default=0)),
                ('start_kicks', models.SmallIntegerField(default=0)),
                ('start_handstrikes_tohead', models.SmallIntegerField(default=0)),
                ('start_kicks_tohead', models.SmallIntegerField(default=0)),
                ('start_rotate_kicks', models.SmallIntegerField(default=0)),
                ('start_knockout', models.SmallIntegerField(default=0)),
                ('knockout', models.BooleanField(verbose_name='Нокаутировал')),
                ('disqualification', models.BooleanField(verbose_name='Дискваливицирован')),
                ('summ_points', models.SmallIntegerField(blank=True, default=0, null=True, verbose_name='Итого очков')),
                ('sportsman', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.Sportsman', verbose_name='Спортсмен')),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.Tournaments', verbose_name='Турнир')),
            ],
            options={
                'db_table': 'account_results_battle',
                'verbose_name': 'Результат боя',
                'verbose_name_plural': 'Результаты боёв',
            },
        ),
        migrations.CreateModel(
            name='BattlePair',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stage', models.CharField(choices=[('1/16', '1/16'), ('1/8', '1/8'), ('1/4', '1/4'), ('1/2', '1/2'), ('Финал', 'Финал')], default=('1/16', '1/16'), max_length=9, verbose_name='Этап')),
                ('freeze_rating_sportsman1', models.SmallIntegerField(verbose_name='Рейтинт 1-го')),
                ('freeze_rating_sportsman2', models.SmallIntegerField(verbose_name='Рейтинт 2-го')),
                ('old_sportsman1_hidden', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='man1_hidden', to='account.Sportsman')),
                ('old_sportsman2_hidden', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='man2_hidden', to='account.Sportsman')),
                ('sportsman1', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='man1', to='account.Sportsman', verbose_name='1-ый спарингующийся')),
                ('sportsman2', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='man2', to='account.Sportsman', verbose_name='2-ый спарингующийся')),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.Tournaments', verbose_name='Турнир')),
                ('weight_category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.WeightCategory', verbose_name='Весовая категория')),
            ],
            options={
                'unique_together': {('stage', 'tournament', 'sportsman1', 'sportsman2')},
                'db_table': 'account_battle_pair',
                'verbose_name': 'Пара',
                'verbose_name_plural': 'Пары',
            },
        ),
    ]