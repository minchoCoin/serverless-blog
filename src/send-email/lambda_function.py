import json
import smtplib
import os
import boto3
import pymysql
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# 환경 변수 설정
GMAIL_USER = os.environ['GMAIL_USER']
GMAIL_PASSWORD = os.environ['GMAIL_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']

def lambda_handler(event, context):
    # S3 이벤트에서 버킷 이름과 객체 키 가져오기
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # S3 객체 다운로드
    s3 = boto3.client('s3')
    file_path = '/tmp/' + key.split('/')[-1]  # 파일 이름만 추출하여 사용
    s3.download_file(bucket, key, file_path)
    
    # 원본 파일 이름 추출
    original_file_name = key.replace('.txt', '')
    # print(f"Processed original file name: {original_file_name}")
    
    # RDS에서 이메일 주소 조회
    recipient_email = get_recipient_email_from_rds(original_file_name)
    # print(f"Processed recipient_email: {recipient_email}")
    
    send_email_with_attachment(recipient_email, file_path, key.split('/')[-1])
    
    return {
        'statusCode': 200,
        'body': json.dumps('Email sent successfully!')
    }

def get_recipient_email_from_rds(file_name):
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 올바른 테이블 이름을 사용하여 쿼리 실행
            sql = "SELECT email FROM audio_file_email_info WHERE filename = %s"
            cursor.execute(sql, (file_name,))
            result = cursor.fetchone()
            if result:
                return result['email']
            else:
                raise ValueError("No email found for the given file name")
    finally:
        connection.close()

def send_email_with_attachment(to_email, file_path, file_name):
    from_email = GMAIL_USER

    # 이메일 메시지 작성
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = 'Your file has been uploaded'

    # 이메일 본문 작성
    body = MIMEText('Please find the attached file.', 'plain')
    msg.attach(body)

    # 첨부 파일 추가
    with open(file_path, 'rb') as attachment:
        part = MIMEApplication(attachment.read(), Name=file_name)
        part['Content-Disposition'] = f'attachment; filename="{file_name}"'
        msg.attach(part)
    
    # Gmail SMTP 서버를 통해 이메일 발송
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(from_email, to_email, msg.as_string())
        server.close()
        print('Email sent successfully')
    except Exception as e:
        print(f'Error sending email: {e}')
