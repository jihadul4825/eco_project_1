from . models import Category

def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)

##** after write this code go to settings.py **## 
##* and add this code in TEMPLATES

##* TEMPLATES = [
##*     {
##*         'BACKEND': '........................',
##*         'DIRS': [.................],
##*         'APP_DIRS': ........,
##*         'OPTIONS': {
##*             'context_processors': [
##*                 '..........................',
##*                 '..........................',
##*                 '..........................',
##*                 '..........................',
##*                 'category.context_processors.menu_links',  # <-- add this
##*             ],
##*         },
##*     },
##* ]