import fire


def new(type='note'):
    from datetime import datetime, timezone
    from yaml import dump as yaml_dump
    from os import linesep, path, makedirs
    from zoneinfo import ZoneInfo

    published = datetime.now(tz=ZoneInfo('Europe/Brussels'))
    year = str(published.year)
    published = published.isoformat(timespec='seconds')

    if not path.exists('content/') or not path.exists('content/' + year):
        makedirs('content/' + year)

    with open('content/' + year + '/' + published + '.md', 'w') as out_file:
        meta = {
            'published': published,
            'last_updated': published,
            'permalink': year + '.html#' + published
        }

        if type == 'article':
            meta['title'] = ''

        out_file.write('---')
        out_file.write(linesep)
        out_file.write(yaml_dump(meta))
        out_file.write('---')
        out_file.write(linesep)


def make():
    from jinja2 import Environment, PackageLoader
    from glob import glob
    from yaml import safe_load_all as yaml_safe_load_all
    from os import linesep, path, mkdir
    from shutil import rmtree
    from markdown import markdown
    from markdown.extensions.toc import TocExtension

    env = Environment(
        loader=PackageLoader('bloglines')
    )

    if path.exists('output/'):
        rmtree('output/')
    mkdir('output/')

    years = [int(i.replace('content/', '')) for i in glob('content/*')]
    current_year = 0

    for year in years:
        if year > current_year:
            current_year = year

        content_files = glob('content/' + str(year) + '/*')
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

            if 'title' in item_details.keys():
                print('Article : ' + content_file)
                template = env.get_template('article.html')

                items.append(template.render(
                    title=item_details['title'],
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

        with open('output/' + str(year) + '.html', 'w') as out_file:
            template = env.get_template('index.html')
            out_file.write(template.render(items=items, years=years))

    if current_year > 0:
        with open('output/' + str(current_year) + '.html', 'r') as in_file:
            with open('output/index.html', 'w') as out_file:
                out_file.write(in_file.read())
    else:
        with open('output/index.html', 'w') as out_file:
            template = env.get_template('index.html')
            out_file.write(template.render(items=[], years=[]))

    with open('style.css', 'r') as in_file:
        with open('output/style.css', 'w') as out_file:
            out_file.write(in_file.read())


if __name__ == '__main__':
    fire.Fire()
