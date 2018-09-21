import praw
import pdb
import re
import os
import time
import sys
from datetime import datetime
from pytz import timezone
from tzlocal import get_localzone

class RedditBot:

    def __init__(self, client_id: str, client_secret: str, password: str, user_agent: str, username: str, subreddits: list, posts_file: os.path):
        self.client_id = client_id
        self.client_secret = client_secret
        self.password = password
        self.user_agent = user_agent
        self.username = username

        reader = self.reader(posts_file)
        self.posts_file_name = reader[0]
        self.posts_replied_to = reader[1]

        self.reddit_instance = praw.Reddit(client_id=self.client_id,
                        client_secret=self.client_secret,
                        password=self.password,
                        user_agent=self.user_agent,
                        username=self.username)

        self.subreddit_instances = []
        for subreddit in subreddits:
            self.subreddit_instances.append(self.reddit_instance.subreddit(subreddit))

        self.reply_footer = 'This is a test post, please comment \'WRONG\' if we\'ve missed something'

    def reader(self, file_path: os.path):
        if not os.path.isfile(file_path):
            posts_replied_to = []                
        else:
            with open(file_path, 'r') as reader:
                posts_replied_to = reader.read()
                posts_replied_to = posts_replied_to.split("\n")
                posts_replied_to = list(filter(None, posts_replied_to))
        f = open(file_path, "w")
        for post_id in posts_replied_to:
            f.write(post_id + "\n")
        f.close()
        return (file_path, posts_replied_to)

    def writer(self, posts_file_name, posts_replied_to: list):
        posts_replied_to = list(set(posts_replied_to))
        with open(posts_file_name, 'w') as f:
            for post_id in posts_replied_to:
                f.write(post_id + "\n")

    def sleep(self, i: int):
        print('Sleeping for:{} seconds\n'.format(i))
        time.sleep(i)

    def start_server(self, persist: bool = False, delay: int = 60, repeats: int = 1, limit: int = 5, testmode: bool = False):
        if not persist:
            while repeats > 0:
                repeats = repeats - 1
                for subreddit in self.subreddit_instances:
                    for post in subreddit.hot(limit=limit):
                        if post.id not in self.posts_replied_to:
                            op_comments = []
                            post.comments.replace_more(limit=None)
                            for comment in post.comments.list():
                                if comment.author == post.author:
                                    op_comments.append(comment.permalink + "?context=1")
                            self.posts_replied_to.append(post.id)
                            self.writer(self.posts_file_name, self.posts_replied_to)
                            reply_string = ''
                            counter = 0
                            for link in op_comments:
                                counter = counter + 1
                                reply_string = reply_string + '[Comment {}'.format(counter) + '](https://reddit.com' + link + ')\n'
                            format = "%Y-%m-%d %H:%M:%S %Z%z"
                            now_utc = datetime.now(timezone('UTC'))
                            time = str(now_utc.strftime(format))
                            post_content = 'AMA OP\'s Comments (last updated on {}):\n\n'.format(time)+reply_string+'\n\n'+self.reply_footer
                            print(post_content+'\n\n')
                            if not testmode:
                                post.reply(post_content)
                self.sleep(delay)
        else:
            while True:
                for subreddit in self.subreddit_instances:
                    for post in subreddit.hot(limit=limit):
                        if post.id not in self.posts_replied_to:
                            op_comments = []
                            post.comments.replace_more(limit=None)
                            for comment in post.comments.list():
                                if comment.author == post.author:
                                    op_comments.append(comment.permalink + "?context=1")
                            self.posts_replied_to.append(post.id)
                            self.writer(self.posts_file_name, self.posts_replied_to)
                            reply_string = ''
                            counter = 0
                            for link in op_comments:
                                counter = counter + 1
                                reply_string = reply_string + '[Comment {}'.format(counter) + '](https://reddit.com' + link + ')\n\n'
                            format = "%Y-%m-%d %H:%M:%S %Z%z"
                            now_utc = datetime.now(timezone('UTC'))
                            time = str(now_utc.strftime(format))
                            post_content = 'AMA OP\'s Comments (last updated on {}):\n\n'.format(time)+reply_string+'\n\n'+self.reply_footer
                            print(post_content+'\n\n')
                            if not testmode:
                                post.reply(post_content)
                self.sleep(delay)


if __name__ == "__main__":
    bot = RedditBot(client_id=',
                     client_secret='',
                     password='',
                     user_agent='',
                     username='', posts_file = os.path.join('posts.txt'), subreddits=['AMA'])
    bot.start_server(repeats=1, limit=3, delay=300, persist=True, testmode=False)