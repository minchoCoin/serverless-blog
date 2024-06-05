import boto3
import json
import pymysql
from datetime import datetime


def responseBuilder(status, body): # lambda_handler의 리턴은 json이어야 함!
    return {
        'statusCode' : status,
        'headers' : {
            'Access-Control-Allow-Origin' : '*',
            'Content-Type' : 'application/json'
        },
        'body' : json.dumps(body, default=str)
    }


def lambda_handler(event, context):
    # 람다를 트리거시킨 버킷 이름과 파일명 가져오기
    baseFileName = event['Records'][0]['s3']['object']['key']
    bucketName = event['Records'][0]['s3']['bucket']['name']

    jobName = baseFileName.split('/')[-1]  # {input_audio/파일명} 에서 파일명만 가져오기
    fileName = jobName.replace('.mp3', '')

    host = 'placeholder' # 실제 값으로 대체하기
    user = 'placeholder'
    password = 'placeholder'
    database = 'placeholder'
    port = placeholder # 포트 값은 문자열이 아니라 숫자!!

    try:
        connection = pymysql.connect(host=host, user=user, passwd=password, db=database, port=port)
    except Exception as e:
        return responseBuilder(500, {'message' : 'an Error occurred while DB connection!', 'error' : e})

    try:
        with connection.cursor() as curr:
            curr.execute(f'SELECT language FROM fileTable WHERE filename = "{jobName}"')
            res = curr.fetchone() # fetchall() 대신 fetchone() 사용!
            if res:
                languageCode = res[0]
            else:
                return responseBuilder(404, {'message': 'File not found in database!'})
    except Exception as e:
        return responseBuilder(500, {'message': 'an Error occurred while languageCode fetch!', 'error': e})
    finally:
        connection.close() # 쿼리 후 DB연결 종료

    # transcribe API 호출하기
    transcribeClient = boto3.client('transcribe')

    try:
        transcribeClient.start_transcription_job(
            TranscriptionJobName=jobName,
            LanguageCode=languageCode,
            MediaFormat='mp3',
            Media={
                'MediaFileUri': f's3://{bucketName}/{baseFileName}'
            },
            # 저장은 save_text 람다에서 수행
            # OutputBucketName=bucketName,
            # OutputKey=f'output_text/{fileName}.json'
        )
        body = {
            'message' : 'Transcribe job started',
            'location' : f's3://{bucketName}/output_text/{fileName}.json',
            'filename' : jobName,
            'languageCode' : languageCode
        }
        return responseBuilder(200, body)
    except Exception as e :
        return responseBuilder(500, {'message' : 'an Error occurred while transcribe!', 'error' : e})
