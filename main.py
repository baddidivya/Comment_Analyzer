from flask import Flask, render_template, request
import pyfile_web_scraping, sentiment_analysis_youtube_comments, mail_sending_to_user_with_attached_csv_files, delete_files_after_mail
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/youtube")
def index_page():
    return render_template('index.html')

@app.route('/scrap', methods = ['POST'])
def scrap_comments():
    url = request.form.get('youtube url')
    emailto = request.form.get('user mail id')

    file_and_detail = pyfile_web_scraping.scrapfyt(url)
    sentiment = sentiment_analysis_youtube_comments.sepposnegcom("Full Comments.csv")

    list_file_and_detail = list(file_and_detail)
    list_sentiment = list(sentiment)
    print(list_file_and_detail)
    video_title, video_owner, video_comment_with_replies, video_comment_without_replies = list_file_and_detail[1:]
    pos_comments_csv, neg_comments_csv, neu_comments_csv, video_posive_comments, video_negative_comments, video_neutral_comments = list_sentiment
    pos_comments_csv = pd.read_csv('Positive Comments.csv')
    neg_comments_csv = pd.read_csv('Negative Comments.csv')
    neu_comments_csv = pd.read_csv('Neutral Comments.csv')
    full_comments_df = pd.read_csv('Full Comments.csv')
    #word cloud
    text = " ".join(review for review in full_comments_df.Comment)
    wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(text)
    wordcloud.to_file("static/word_cloud_plot.png")
    wordcloud.to_file("word_cloud_plot.png")

    #pie chart
    types = ['positive comments', 'negative comments', 'neutral comments']
    colors = ['green','red','blue']
    data = [len(pos_comments_csv.axes[0]), len(neg_comments_csv.axes[0]), len(neu_comments_csv.axes[0])]
    plt.pie(data, labels = types,colors=colors, autopct='%1.2f%%')
    plot=plt
    plot.savefig(os.path.join('static', 'pie_chart_plot.png'))
    plot.savefig(os.path.join('pie_chart_plot.png'))
    mail_sending_to_user_with_attached_csv_files.mailsend(emailto)

    if(len(pos_comments_csv.axes[0])>len(neg_comments_csv.axes[0]) and len(pos_comments_csv.axes[0])>len(neu_comments_csv.axes[0])):
        message="Positive"
    elif(len(neg_comments_csv.axes[0])>len(pos_comments_csv.axes[0]) and len(neg_comments_csv.axes[0])>len(neu_comments_csv.axes[0])):
        message="Negative"
    else:
        message="Neutral"
    delete_files_after_mail.file_delete()

    after_complete_message = "Your file is ready and sent to your mail id"

    return render_template("index.html",after_complete_message = after_complete_message, title = video_title,
                           owner = video_owner, comment_w_replies = video_comment_with_replies,
                           comment_wo_replies = video_comment_without_replies,
                           positive_comment = video_posive_comments, negative_comment = video_negative_comments, neutral_comment =video_neutral_comments,
                           pos_comments_csv = [pos_comments_csv.to_html()], neg_comments_csv = [neg_comments_csv.to_html()], neu_comments_csv = [neu_comments_csv.to_html()],message=message)


@app.route("/twitter")
def twitter_page():
    return render_template('index2.html')


@app.route('/sentiment', methods = ['GET','POST'])
def sentiment():
    userid = request.form.get('userid')
    hashtag = request.form.get('hashtag')

    if userid == "" and hashtag == "":
        error = "Please Enter any one value"
        return render_template('index2.html', error=error)
    
    if not userid == "" and not hashtag == "":
        error = "Both entry not allowed"
        return render_template('index2.html', error=error)


    consumerKey = "tElQSmLQ0gea5BZHgBad7q1xX"
    consumerSecret = "GT0h2TWaBIN5m69A9joCuDemhmVE6EbnuCU26NrBVi9ndiaYIs"
    accessToken = "1678438212350492672-blIY2M5VvO5ykDbkBXWQmtlnSa2BUh"
    accessTokenSecret = "DoOYAkjqoOC1RMMNOhN0ip2MvmjSmIFDS7ICb3zk1bDcm"
    
    authenticate = tweepy.OAuthHandler(consumerKey, consumerSecret)
    authenticate.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(authenticate, wait_on_rate_limit = True)

    #cleaning
    def cleanTxt(text):
        text = re.sub('@[A-Za-z0–9]+', '', text)
        text = re.sub('#', '', text) 
        text = re.sub('RT[\s]+', '', text)
        text = re.sub('https?:\/\/\S+', '', text) 
        return text
    def getSubjectivity(text):
        return TextBlob(text).sentiment.subjectivity
    def getPolarity(text):
        return TextBlob(text).sentiment.polarity
    def getAnalysis(score):
            if score < 0:
                return 'Negative'
            elif score == 0:
                return 'Neutral'
            else:
                return 'Positive'

    if userid == "":
        msgs = []
        msg =[]
        for tweet in tweepy.Cursor(api.search_tweets, q=hashtag).items(500):
            msg = [tweet.text] 
            msg = tuple(msg)                    
            msgs.append(msg)

        df = pd.DataFrame(msgs)
        df['Tweets'] = df[0].apply(cleanTxt)
        df.drop(0, axis=1, inplace=True)
        df['Subjectivity'] = df['Tweets'].apply(getSubjectivity)
        df['Polarity'] = df['Tweets'].apply(getPolarity)
        df['Analysis'] = df['Polarity'].apply(getAnalysis)
        positive = df.loc[df['Analysis'].str.contains('Positive')]
        negative = df.loc[df['Analysis'].str.contains('Negative')]
        neutral = df.loc[df['Analysis'].str.contains('Neutral')]

        positive_per = round((positive.shape[0]/df.shape[0])*100, 1)
        negative_per = round((negative.shape[0]/df.shape[0])*100, 1)
        neutral_per = round((neutral.shape[0]/df.shape[0])*100, 1)

        return render_template('sentiment.html', name=hashtag,positive=positive_per,negative=negative_per,neutral=neutral_per)
    else:
        username = "@"+userid

        post = api.user_timeline(screen_name=userid, count = 500, lang ="en", tweet_mode="extended")
        twitter = pd.DataFrame([tweet.full_text for tweet in post], columns=['Tweets'])

        twitter['Tweets'] = twitter['Tweets'].apply(cleanTxt)
        twitter['Subjectivity'] = twitter['Tweets'].apply(getSubjectivity)
        twitter['Polarity'] = twitter['Tweets'].apply(getPolarity)

        twitter['Analysis'] = twitter['Polarity'].apply(getAnalysis)
        positive = twitter.loc[twitter['Analysis'].str.contains('Positive')]
        negative = twitter.loc[twitter['Analysis'].str.contains('Negative')]
        neutral = twitter.loc[twitter['Analysis'].str.contains('Neutral')]

        positive_per = round((positive.shape[0]/twitter.shape[0])*100, 1)
        negative_per = round((negative.shape[0]/twitter.shape[0])*100, 1)
        neutral_per = round((neutral.shape[0]/twitter.shape[0])*100, 1)

        return render_template('sentiment.html', name=username,positive=positive_per,negative=negative_per,neutral=neutral_per)

if __name__ == "__main__":
    app.run()
