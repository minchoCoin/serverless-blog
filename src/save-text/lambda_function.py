import json
import boto3
import os
import urllib.request

BUCKET_NAME = os.environ['BUCKET_NAME']
s3 = boto3.resource('s3')
transcribe = boto3.client('transcribe')

def lambda_handler(event, context):
    
    job_name = event['detail']['TranscriptionJobName']
    job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    uri = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
    print(uri)
    
    content = urllib.request.urlopen(uri).read().decode('UTF-8')
    print(json.dumps(content))
    
    data =  json.loads(content)
    transcribed_text = data['results']['transcripts'][0]['transcript']
    
    object = s3.Object(BUCKET_NAME, job_name + ".txt")
    object.put(Body=transcribed_text)
