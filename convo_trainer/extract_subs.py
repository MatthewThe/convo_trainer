from youtube_transcript_api import YouTubeTranscriptApi

youtube_video_id = "LgA3Ynirhms"
# transcript_list = YouTubeTranscriptApi.list_transcripts(youtube_video_id)

# print(transcript_list.find_manually_created_transcript())
srt = YouTubeTranscriptApi.get_transcript(youtube_video_id, languages=["fr"])

print("\n".join([x['text'] for x in srt[:70]]))
