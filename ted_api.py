import requests
import pandas as pd
import isodate
import os



BaseUrl="https://www.googleapis.com/youtube/v3"
API_KEY=os.environ.get("Ted_API_KEY")
channel_ID=os.environ.get("TED_ED_CHANNEL")


#First API (search channels and video ID)
response=requests.get(f"{BaseUrl}/search?part=snippet&channelId={channel_ID}&key={API_KEY}&maxResults=10000").json()

#create a data frame to receive the data
df=pd.DataFrame(columns=["video_id","video_title","publish_time","viewCount","likeCount","commentCount","duration"])



#now it's time to get the videos details
def get_video_statistics(video_id:str):
    #second API (statistics of each video)
    response=requests.get(f"{BaseUrl}/videos?part=statistics&id={video_id}&key={API_KEY}&maxResults=10000").json()
    try:
        viewCount=response["items"][0]["statistics"]["viewCount"]
        likeCount=response["items"][0]["statistics"]["likeCount"]
        commentCount=response["items"][0]["statistics"]["commentCount"]
        return viewCount,likeCount,commentCount
    except KeyError as e:
        return None,None,None


#get video content details
def get_video_content_details(video_id:str):
    #second API (statistics of each video)
    response=requests.get(f"{BaseUrl}/videos?part=contentDetails&id={video_id}&key={API_KEY}&maxResults=10000").json()
    try:
        duration=response["items"][0]["contentDetails"]["duration"]
        duration=isodate.parse_duration(duration)
        return duration
    except KeyError as e:
        return None
 

## Loop and save informations

def store_info(df:pd.DataFrame,pageToken=''):
    response=requests.get(f"{BaseUrl}/search?part=snippet&channelId={channel_ID}&key={API_KEY}&maxResults=10000&pageToken={pageToken}").json()
    for video in response["items"]:
        if video["id"]["kind"]=="youtube#video":
            video_id=video["id"]["videoId"]
            video_title=video["snippet"]["title"]
            publish_time=video["snippet"]["publishTime"]
            publish_time=str(publish_time).split("T")[0]
            
            viewCount,likeCount,commentCount=get_video_statistics(video_id)
            duration=get_video_content_details(video_id)
            df=df.append({
                "video_id":video_id,"video_title":video_title,"publish_time":publish_time,
                "viewCount":viewCount,"likeCount":likeCount,"commentCount":commentCount,
                "duration":duration
            },ignore_index=True)
    nextPageToken=response.get("nextPageToken")

    return (df,nextPageToken)


nextPageToken=""





while True:
    df,nextPageToken=store_info(df,nextPageToken)
    nextPageToken=nextPageToken
    print(nextPageToken)
    if not nextPageToken:
        break




df.drop_duplicates(inplace=True)
#save it
df.to_csv("ted_youtube_videos.csv",index=False)
print(df)
