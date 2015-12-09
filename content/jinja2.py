from content.models import CategoryContent, Category


def get_content_by_categories(categories, limit, random=False):
    # convert to objects
    try:
        cats = [x.strip() for x in categories.split(',')]
        categories = []
        for cat in cats:
            try:
                sel_categories = Category.get_category_for_path(cat)
            except:
                sel_categories = Category.objects.get(pk=int(cat))
            categories.append(sel_categories)
    except:
        pass

    if categories is None or categories == []:
        return None
    try:
        query = CategoryContent.published.all()
        if categories is not None and categories != []:
            query = query.filter(categories__in=categories)

        ordering = '-date_modified'
        if random:
            ordering = '?'
        query = query.order_by(ordering)
        if limit == -1:
            return query.all()
        else:
            return query.all()[:limit]
        if limit == 1:
            return query[0]
    except:
        return None
