import fire

def new(type='note', content_dir='content/', media_dir = 'media/'):
    from datetime import datetime, timezone
    from yaml import dump as yaml_dump
    from os import linesep, path, makedirs
    from zoneinfo import ZoneInfo

    published = datetime.now(tz=ZoneInfo('Europe/Brussels'))
    year = str(published.year)
    published = published.isoformat(timespec='seconds')

    if not content_dir.endswith('/'):
        content_dir = content_dir + '/'

    if not media_dir.endswith('/'):
        media_dir = media_dir + '/'

    if not path.exists(content_dir) or not path.exists(content_dir + year):
        makedirs(content_dir + year)

    if not path.exists(media_dir):
        makedirs(media_dir)

    with open(content_dir + year + '/' + published + '.md', 'w') as out_file:
        meta = {
            'published': published,
            'last_updated': published,
            'permalink': year + '.html#' + published
        }

        if type == 'article':
            meta['title'] = ''
        elif type == 'photo' or type == 'photos':
            meta['photos'] = [{
                'uri': '',
                'alt': ''
            }]

        out_file.write('---')
        out_file.write(linesep)
        out_file.write(yaml_dump(meta))
        out_file.write('---')
        out_file.write(linesep)


def make(output_dir='output/', content_dir='content/', media_dir = 'media/'):
    from jinja2 import Environment, PackageLoader
    from glob import glob
    from yaml import safe_load_all as yaml_safe_load_all
    from os import linesep, path, mkdir
    from shutil import rmtree, copytree
    from markdown import markdown
    from markdown.extensions.toc import TocExtension

    env = Environment(
        loader=PackageLoader('bloglines')
    )

    if not output_dir.endswith('/'):
        output_dir = output_dir + '/'

    if not content_dir.endswith('/'):
        content_dir = content_dir + '/'

    if not media_dir.endswith('/'):
        media_dir = media_dir + '/'

    if path.exists(output_dir):
        rmtree(output_dir)
    mkdir(output_dir)

    if path.exists(media_dir):
        copytree(media_dir, output_dir + media_dir)

    if path.exists('node_modules/'):
        copytree('node_modules/', output_dir + 'node_modules/')

    years = [int(i.replace(content_dir, '')) for i in glob(content_dir + '*')]
    current_year = 0

    for year in years:
        if year > current_year:
            current_year = year

        content_files = glob(content_dir + str(year) + '/*')
        content_files.sort(reverse=True)

        items = []

        for content_file in content_files:
            with open(content_file, 'r') as in_file:
                meta = yaml_safe_load_all(in_file)

                for m in meta:
                    item_details = m
                    break

            with open(content_file, 'r') as in_file:
                lines = in_file.read().splitlines()
                parsed_lines = []

                dotted = 0
                for line in lines:
                    if '---' in line:
                        dotted += 1

                    if '---' not in line and dotted >= 2:
                        parsed_lines.append(line + linesep)
                parsed_lines = ''.join(parsed_lines)

            content = markdown(parsed_lines, extensions=['extra', TocExtension(title='Contents', baselevel=3), 'smarty', 'sane_lists'], output_format='html5')
            keys = item_details.keys()

            if 'title' in keys:
                print('Article : ' + content_file)
                template = env.get_template('article.html')

                items.append(template.render(
                    title=item_details['title'],
                    content=content,
                    published=item_details['published'],
                    last_updated=item_details['last_updated'],
                    permalink=item_details['permalink']
                ))
            elif 'photos' in keys:
                print('Photos: ' + content_file)
                template = env.get_template('photos.html')

                items.append(template.render(
                    media_dir=media_dir,
                    photos=item_details['photos'],
                    content=content,
                    published=item_details['published'],
                    last_updated=item_details['last_updated'],
                    permalink=item_details['permalink']
                ))
            else:
                print('Note : ' + content_file)
                template = env.get_template('note.html')

                items.append(template.render(
                    content=content,
                    published=item_details['published'],
                    last_updated=item_details['last_updated'],
                    permalink=item_details['permalink']
                ))

        with open(output_dir + str(year) + '.html', 'w') as out_file:
            template = env.get_template('index.html')
            out_file.write(template.render(items=items, years=years))

    if current_year > 0:
        with open(output_dir + str(current_year) + '.html', 'r') as in_file:
            with open(output_dir + 'index.html', 'w') as out_file:
                out_file.write(in_file.read())
    else:
        with open(output_dir + 'index.html', 'w') as out_file:
            template = env.get_template('index.html')
            out_file.write(template.render(items=[], years=[]))

    with open('style.css', 'r') as in_file:
        with open(output_dir + 'style.css', 'w') as out_file:
            out_file.write(in_file.read())

def upload(output_dir='output/'):
    def is_true(value):
        return value.lower() == 'true' or value == '1'


    from ftplib import FTP, FTP_TLS
    from glob import glob
    from os import getenv
    from dotenv import load_dotenv
    
    load_dotenv()

    if is_true(getenv('FTP_SECURE')):
        session = FTP_TLS(getenv('FTP_SERVER'),getenv('FTP_USERNAME'),getenv('FTP_PASSWORD'))
    else:
        session = ftplib.FTP(getenv('FTP_SERVER'),getenv('FTP_USERNAME'),getenv('FTP_PASSWORD'))
    
    for file_name in glob('output/*.*') + glob('output/**/*.*', True):
        with open(file_name,'rb') as file:
            file_name = file_name.removeprefix(output_dir)
            print(file_name)
            session.storbinary('STOR %s' % file_name, file)
    
    session.quit()

if __name__ == '__main__':
    fire.Fire()
