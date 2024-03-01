"""An example of writing an API to scrape hacker news once, and then enabling usage everywhere"""
import izi
import requests


@izi.local()
@izi.cli()
@izi.get()
def top_post(section: izi.types.one_of(('news', 'newest', 'show'))='news'):
    """Returns the top post from the provided section"""
    content = requests.get('https://news.ycombinator.com/{0}'.format(section)).content
    text = content.decode('utf-8')
    return text.split('<tr class=\'athing\'>')[1].split("<a href")[1].split(">")[1].split("<")[0]
