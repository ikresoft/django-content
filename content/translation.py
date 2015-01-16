from modeltranslation.translator import translator, TranslationOptions
from content.models import Content, CategoryContent, Category


class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'slug')

translator.register(Category, CategoryTranslationOptions)


class ContentTranslationOptions(TranslationOptions):
    fields = ('title', 'body', 'slug')

translator.register(Content, ContentTranslationOptions)


class CategoryContentTranslationOptions(TranslationOptions):
    pass

translator.register(CategoryContent, CategoryContentTranslationOptions)
