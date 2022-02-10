from TwitterAPI import TwitterAPI, TwitterOAuth, TwitterRequestError, TwitterConnectionError, TwitterPager
import pandas as pd
import time
import json
import re

consumer_key = "gMpl7xixYzZDq3S3InanMSXuN"
consumer_secret = "JlQn9WQdhdVQBUz8yx2Qqa8xorM4djzGkml5Q0LDJssckieUAh"
access_token_key = "1310934082960994304-4dbyexQzVcNwLFLl6HVtYkGoSiIZIt"
access_token_secret = "Nbuts1Iid0nHWIy0kXbptkcIPvZD92XD6GnQOXdmzTWFy"
twapi = TwitterAPI(consumer_key, consumer_secret, access_token_key,
                   access_token_secret, api_version='2')



from .twitter_comment import TreeNode



"""
Retrieves level 1 replies for a given conversation id
Returns lists conv_id, child_id, text tuple which shows every reply's tweet_id and text in the last two lists
"""


def retrieve_replies(conversation_id):
    try:
        # GET ROOT OF THE CONVERSATION
        r = twapi.request(f'tweets/:{conversation_id}',
                          {
                              'tweet.fields': 'author_id,conversation_id,created_at,in_reply_to_user_id'
                          })

        for item in r:
           root = TreeNode(item)
           # print(f'ROOT {root.id()}')

        # GET ALL REPLIES IN CONVERSATION

        pager = TwitterPager(twapi, 'tweets/search/recent',
                             {
                                 'query': f'conversation_id:{conversation_id}',
                                 'tweet.fields': 'author_id,conversation_id,created_at,in_reply_to_user_id'
                             })

        orphans = []

        for item in pager.get_iterator(wait=2):
            node = TreeNode(item)
            # print(f'{node.id()} => {node.reply_to()}')
            # COLLECT ANY ORPHANS THAT ARE NODE'S CHILD
            orphans = [
                orphan for orphan in orphans if not node.find_parent_of(orphan)]
            # IF NODE CANNOT BE PLACED IN TREE, ORPHAN IT UNTIL ITS PARENT IS FOUND
            if not root.find_parent_of(node):
                orphans.append(node)

        conv_id, child_id, text = root.list_l1()
#         print('\nTREE...')
# 	    root.print_tree(0)

        assert len(orphans) == 0, f'{len(orphans)} orphaned tweets'

    except TwitterRequestError as e:
        print(e.status_code)
        for msg in iter(e):
            print(msg)

    except TwitterConnectionError as e:
        print(e)

    except Exception as e:
        print(e)

    return conv_id, child_id, text








"""
Retrieves replies for a list of conversation ids (conv_ids
Returns a dataframe with columns [conv_id, child_id, text] tuple which shows every reply's tweet_id and text in the last two columns
"""


#Process text
def process_text(line):
    line = line.strip()
    line = re.sub("\n", "", line)
    pattern = r'@\w+'
    line = re.sub(pattern, "", line, flags=re.I)
    line = re.sub(r'https?:\/\/\S*', '', line, flags=re.MULTILINE)
    EMOJI_PATTERN = re.compile(
        "["
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"
        "]+")

    line = re.sub(EMOJI_PATTERN, r'', line)
    line = re.sub('[^A-Za-z0-9 ]+', '', line)
    return line

#dealing with empty string
def neutral_goal(line):
    if len(line) == 0:
        return "the product is okay"
    else:
        return line

def reply_thread_maker(conv_ids):
    conv_ids = [conv_ids]
    conv_id = []
    child_id = []
    text = []
    for id in conv_ids:
        conv_id1, child_id1, text1 = retrieve_replies(id)
        conv_id.extend(conv_id1)
        child_id.extend(child_id1)
        text.extend(text1)

    replies_data = {'conversation_id': conv_id,
                    'child_tweet_id': child_id,
                    'tweet_text': text}

    # COnvert to pandas dataframe
    replies = pd.DataFrame(replies_data)

    # Remove @user_name
    #replies["tweet_text"] = replies.apply(lambda row: remove_spe(row["tweet_text"]), axis=1)

    #processed replies
    replies["processed_text"] = replies.apply(lambda row: process_text(row["tweet_text"]), axis=1)
    replies["processed_text"] = replies.apply(lambda row: neutral_goal(row["processed_text"]), axis=1)


    #Convert dataframe to json format

    comment_json = replies.to_json(orient="records")
    parsed = json.loads(comment_json)
    data_comments = json.dumps(parsed)


    return data_comments

