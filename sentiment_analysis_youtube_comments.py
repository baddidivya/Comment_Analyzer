
import pandas as pd
import csv
import nltk
import os.path as checkcsv
import pickle


def sepposnegcom(comment_file):

    dataset = pd.read_csv(comment_file, encoding_errors = 'ignore')
    dataset = dataset.iloc[:, 0:]

    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    analyser = SentimentIntensityAnalyzer()
    X_test=dataset['Comment']
    # pickled_model=pickle.load(open('model.pkl','rb'))
    #predicted_values=pickled_model.predict(X_test)
    def vader_sentiment_result(sent):
        scores = analyser.polarity_scores(sent)
        pol_score = scores["compound"]

        if pol_score > 0:
            return 2               #positive comments --> 2
        elif pol_score < 0:
            return 0               #negitive comments --> 0
        else:
            return 1               #neutral comments  --> 1


    dataset['vader_sentiment'] = dataset['Comment'].apply(lambda x : vader_sentiment_result(x))


    for (sentiment), group in dataset.groupby(['vader_sentiment']):
         group.to_csv(f'{sentiment}.csv', index=False)
    
    if checkcsv.exists('(2,).csv') == False:                             # If 1.csv file does not exist, it creates one empty 1.csv file.
        with open('(2,).csv', 'w', encoding='UTF8', newline='') as f1:
            writer1 = csv.writer(f1)
            header1 = ['Empty', 'Empty', 'Empty']
            row1 = ['No Positive Comments', 'No Positive Comments', 'No Positive Comments']
            writer1.writerow(header1)
            writer1.writerow(row1)
    if checkcsv.exists('(1,).csv') == False:                             # If 1.csv file does not exist, it creates one empty 1.csv file.
        with open('(1,).csv', 'w', encoding='UTF8', newline='') as f1:
            writer1 = csv.writer(f1)
            header1 = ['Empty', 'Empty', 'Empty']
            row1 = ['No Neutral Comments', 'No Neutral Comments', 'No Neutral Comments']
            writer1.writerow(header1)
            writer1.writerow(row1)

    if checkcsv.exists('(0,).csv') == False:                             # If 1.csv file does not exist, it creates one empty 1.csv file.
        with open('(0,).csv', 'w',encoding='UTF8', newline='') as f0:
            writer0 = csv.writer(f0)
            header0 = ['Empty', 'Empty', 'Empty']
            row0 = ['No Negative Comments', 'No Negative Comments', 'No Negative Comments']
            writer0.writerow(header0)
            writer0.writerow(row0)
    
    pos = (pd.read_csv('(2,).csv', engine = 'python')).iloc[:, :-1]
    neg = (pd.read_csv('(0,).csv', engine = 'python')).iloc[:, :-1]
    neu = (pd.read_csv('(1,).csv', engine = 'python')).iloc[:, :-1]

    positive_comments = pos.to_csv("Positive Comments.csv", index=False)
    negative_comments = neg.to_csv("Negative Comments.csv",index=False)
    neutral_comments = neu.to_csv("Neutral Comments.csv",index=False)

    video_positive_comments = str(len(pos.axes[0])) + ' Comments'  #Finding total rows in positive comments
    video_negative_comments = str(len(neg.axes[0])) + ' Comments'  #Finding total rows in negative comments
    video_neutral_comments = str(len(neu.axes[0])) + ' Comments'

    if (pd.read_csv('(2,).csv', nrows=0).columns.tolist())[0] == 'Empty':
        video_positive_comments = '0 Comments'
    if (pd.read_csv('(1,).csv', nrows=0).columns.tolist())[0] == 'Empty':
        video_neutral_comments = '0 Comments'
    if (pd.read_csv('(0,).csv', nrows=0).columns.tolist())[0] == 'Empty':
        video_negative_comments = '0 Comments'

    ## return function
    return positive_comments, negative_comments, neutral_comments, video_positive_comments, video_negative_comments, video_neutral_comments
