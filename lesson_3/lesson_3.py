import time
import datetime
import requests as req
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import model_gbblog

engine = create_engine('sqlite:///gb_blog.db')
model_gbblog.Base.metadata.create_all(bind=engine)
session_maker = sessionmaker(bind=engine)

class Parser_GBBlog:
    
    def __init__(self, start_url):
        self.start_url = start_url
        self.writers_id = {}

    def _get(self, url):
        while True:
            try:
                resp = req.get(url)
                if resp.status_code != 200:
                    raise Exception
                time.sleep(0.1)
                return BeautifulSoup(resp.text, 'lxml')
            except Exception:
                time.sleep(0.25)

    def run(self):
        url = self.start_url
        page_done = set()
        posts_page = self._get(url)
        next_page = {urljoin(url, el.get('href')) for el in posts_page.find('ul', class_="gb__pagination").findChildren('a') if el.has_attr('href') and
                 urljoin(url, el.get('href')) not in page_done.union(url)}
        while len(next_page) > 0:
            posts_page = self._get(url)
            self.parse(posts_page)
            page_done.add(url)
            pagination = posts_page.find('ul', class_="gb__pagination")
            next_page.update(
                {urljoin(url, el.get('href')) for el in pagination.findChildren('a') if el.has_attr('href') and
                 urljoin(url, el.get('href')) not in page_done.union(url)})
            url = next_page.pop()

    def parse(self, posts_page: BeautifulSoup):
        posts = dict()
        posts_url = [urljoin(self.start_url, el.find('a').get('href')) for el in
                        posts_page.find_all('div', class_='post-item event')]

        for i in posts_url:
            posts['url'] = i
            post = BeautifulSoup(req.get(i).text, 'lxml')
            posts['title'] = post.find('h1').text
            posts['image'] = post.find('img').get('src') if post.find('div',
                                                                  class_='blogpost-content').find('img') else None
            posts['date'] = datetime.datetime.strptime(post.find('time').get('datetime'), '%Y-%m-%dT%H:%M:%S%z')
            author = post.find('div', class_='col-md-5 col-sm-12 col-lg-8 col-xs-12 padder-v')
            posts['writer'] = author.find('div', attrs={'itemprop': 'author'}).text
            posts['writer_url'] = urljoin(i, author.find('a').get('href'))
            posts['tags'] = {el.text: urljoin(i, el.get('href')) for el in post.find_all('a', class_='small')}
            posts['comments'] = self.find_comments(post)
            self.save(posts)

    def find_comments(self, post: BeautifulSoup):
        post = post
        url_api = 'https://geekbrains.ru/api/v2/comments?commentable_type=Post&commentable_id=&order=desc'
        params = {'commentable_id': post.find('comments').get('commentable-id')}
        data = req.get(url_api, params).json()
        comments = [{'comment_author': comm["comment"].get("user").get("full_name"),
                                   'body': comm["comment"].get("body")} for comm in data]
        return comments

    def try_commit(self, session, table):
        try:
            session.add(table)
            session.commit()
        except Exception:
            session.rollback()

    def save(self, post_data):
        db = session_maker()

        writer_id = 0
        for key_url in self.writers_id:
            if key_url == post_data['writer_url']:
                writer_id = self.writers_id[key_url]

        if writer_id == 0:
            tmp_writer = model_gbblog.Writer(url=post_data['writer_url'], name=post_data['writer'])
            self.try_commit(db, tmp_writer)
            self.writers_id[tmp_writer.url] = tmp_writer.id
            writer_id = tmp_writer.id

        tags = []
        for key in post_data['tags'].keys():
            tmp_tag = db.query(model_gbblog.Tag).filter(model_gbblog.Tag.name == key).first()
            if not tmp_tag:
                tmp_tag = model_gbblog.Tag(url=post_data['tags'].get(key), name=key)
                self.try_commit(db, tmp_tag)
            tags.append(tmp_tag)

        tmp_post = model_gbblog.Post(url=post_data['url'], title=post_data['title'],
                                     image=post_data['image'], date=post_data['date'],
                                     writer_id=writer_id)
        tmp_post.tags.extend(tags)
        self.try_commit(db, tmp_post)

        for el in post_data['comments']:
            tmp_comments = model_gbblog.Comment(author=el.get('comment_author'),
                                                body=el.get('body'),
                                                post_id=tmp_post.id)
            self.try_commit(db, tmp_comments)

        db.close()


if __name__ == '__main__':
    url = 'https://geekbrains.ru/posts'
    parser = Parser_GBBlog(url)
    parser.run()


