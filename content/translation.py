from modeltranslation.translator import translator, TranslationOptions
from content.models import Content, CategoryContent


class ContentTranslationOptions(TranslationOptions):
    fields = ('title', 'body', 'slug')

translator.register(Content, ContentTranslationOptions)


class CategoryContentTranslationOptions(TranslationOptions):
    pass

translator.register(CategoryContent, CategoryContentTranslationOptions)
