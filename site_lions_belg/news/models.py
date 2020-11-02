from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save   # сигнал перед сохранением
from django.utils.text import slugify           # для создания слага
from transliterate import translit              # перевод из кирилицы в латиницу
from django.urls import reverse                 # для создания ссылок
from ckeditor.fields import RichTextField

# Create your models here.


class CategoryNews(models.Model):

    class Meta:
        verbose_name = "Название категории"
        verbose_name_plural = "Категории"
        db_table = "news_category_news"

    name = models.CharField(max_length=50, verbose_name="Категория")
    slug = models.SlugField(blank=True, help_text="Человекопонятный URL-адрес. Если поле не будет заполнено, то оно сгенерируется автоматически.", verbose_name="Слаг")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    edit_time = models.DateTimeField(auto_now=True, verbose_name="Дата редактирования")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('news:category_detail', kwargs={'category_slug': self.slug})


def pre_save_category_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        slug = slugify(translit(instance.name, 'ru', reversed=True))
        instance.slug = slug


pre_save.connect(pre_save_category_slug, sender=CategoryNews)


class TagNews(models.Model):

    class Meta:
        verbose_name = "Название тэга"
        verbose_name_plural = "Тэги"
        db_table = "news_category_tags"

    name = models.CharField(max_length=50, verbose_name="Тэг")
    slug = models.SlugField(blank=True, help_text="Человекопонятный URL-адрес. Если поле не будет заполнено, то оно сгенерируется автоматически.", verbose_name="Слаг")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    edit_time = models.DateTimeField(auto_now=True, verbose_name="Дата редактирования")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('news:tag_detail', kwargs={'tag_slug': self.slug})


def pre_save_tag_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        slug = slugify(translit(instance.name, 'ru', reversed=True))
        instance.slug = slug


pre_save.connect(pre_save_tag_slug, sender=TagNews)


def get_user(request):
    return request.user.username


def image_folder(instance, filename):
    filename = instance.slug + '.' + filename.split('.')[1]   # slug + расширение
    return "{0}/{1}".format(instance.slug, filename)          # где сохранится (создастся папка для этого)


class New(models.Model):

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        db_table = "news_category_new"

    category = models.ForeignKey(CategoryNews, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Категория")
    tag = models.ManyToManyField(TagNews, blank=True, verbose_name="Тэг", related_name="Тэги")
    # tag = models.ForeignKey(TagNews, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Тэг")
    title = models.CharField(max_length=150, verbose_name="Заголовок")
    slug = models.SlugField(blank=True, help_text="Человекопонятный URL-адрес. Если поле не будет заполнено, то оно сгенерируется автоматически.", verbose_name="Слаг")
    image = models.ImageField(upload_to=image_folder, verbose_name="Главное изображение")
    description = RichTextField(blank=True, null=True, verbose_name="Содержимое новости", help_text="Вы можете воспользоваться инстументами этого поля для задания форматирования текста")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    edit_time = models.DateTimeField(auto_now=True, verbose_name="Дата редактирования")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Автор публикации")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news:new_detail', kwargs={'new_slug': self.slug})


def pre_save_new(sender, instance, *args, **kwargs):
    if not instance.slug:
        slug = slugify(translit(instance.title, 'ru', reversed=True))
        instance.slug = slug


pre_save.connect(pre_save_new, sender=New)
