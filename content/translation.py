from modeltranslation.translator import translator, TranslationOptions
from content.models import Content


class ContentTranslationOptions(TranslationOptions):
    fields = ('title', 'body', 'slug')

translator.register(Content, ContentTranslationOptions)
