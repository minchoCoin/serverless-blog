# send-email

## AWS Lambda 함수: S3에 저장된 Transcribe 결과를 이메일로 전송

이 AWS Lambda 함수는 S3 버킷에 AWS Transcribe 결과 텍스트 파일이 저장될 때 트리거되어, 해당 파일을 다운로드하고, 데이터베이스에서 수신자의 이메일 주소를 조회한 후, 파일을 첨부하여 이메일로 전송합니다.

### Prerequisites

- AWS 계정
- AWS Lambda 설정
- AWS S3 버킷
- AWS RDS(MySQL) 설정
- Gmail 계정

### Installation

1. **Lambda 함수 생성**:
    - AWS Lambda 콘솔에서 새 Lambda 함수를 생성합니다.
    - 실행 환경으로 Python 3.x를 선택합니다.
    - IAM 역할을 생성하거나 기존 역할을 선택하여 필요한 권한을 부여합니다.

2. **IAM 역할 생성**:
   - S3에서 객체를 읽고 RDS에 접근할 수 있는 IAM 역할을 생성합니다.
   - 다음 정책을 역할에 첨부합니다:
     - `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` - CloudWatch Logs에 대한 권한
     - `s3:GetObject` - S3 버킷에서 객체를 가져올 수 있는 권한
     - `rds:DescribeDBInstances`, `rds-db:connect` - RDS 인스턴스를 설명하고 연결할 수 있는 권한

3. **환경 변수 설정**:
   - Lambda 함수의 설정에서 환경 변수를 추가합니다.
   - 아래의 환경 변수 목록을 참고하여 값을 입력합니다.

4. **트리거 설정**:
    - S3 콘솔에서 Lambda 트리거를 설정합니다.
    - 특정 버킷에 객체가 생성될 때 Lambda 함수가 트리거되도록 설정합니다.

5. **코드 배포**:
    - 아래의 코드를 Lambda 함수에 복사하여 붙여넣습니다.
    - 함수를 저장하고 배포합니다.

### Google SMTP Setting

Google SMTP 서버를 이용하기 위해서는 Gmail 설정을 변경해야 합니다. 다음 단계를 따라 설정해 주세요:

1. **IMAP 액세스** 허용:
   - Gmail 계정에 로그인합니다.
   - 오른쪽 상단의 설정 아이콘을 클릭하고 "모든 설정 보기"를 선택합니다.
   - "전달 및 POP/IMAP" 탭으로 이동합니다.
   - "IMAP 액세스" 섹션에서 "IMAP 사용"을 선택하고 변경 사항을 저장합니다.
2. **2단계 인증** 설정:
   - Google 계정으로 이동합니다.
   - "보안" 탭을 선택합니다.
   - "Google에 로그인" 섹션에서 "2단계 인증"을 설정합니다.
   - 화면의 안내에 따라 2단계 인증을 완료합니다.

3. **App Password** 생성:
   - 2단계 인증이 설정된 상태에서 앱 비밀번호 페이지로 이동합니다.
   - "앱 비밀번호" 섹션에서 "앱 선택" 드롭다운 메뉴에서 "메일"을 선택합니다.
   - "기기 선택" 드롭다운 메뉴에서 "사용 중인 기기"를 선택합니다.
   - "생성" 버튼을 클릭하여 16자리 앱 비밀번호를 생성합니다.
   - 생성된 16자리 앱 비밀번호를 환경 변수 GMAIL_PASSWORD에 설정합니다.

### Environment Variables

다음 환경 변수를 Lambda 함수 설정에 추가해야 합니다:

- `GMAIL_USER`: Gmail 사용자 이메일 주소
- `GMAIL_PASSWORD`: Gmail APP Password
- `DB_HOST`: RDS 데이터베이스 호스트
- `DB_USER`: RDS 데이터베이스 사용자 이름
- `DB_PASSWORD`: RDS 데이터베이스 비밀번호
- `DB_NAME`: RDS 데이터베이스 이름

### IAM Explanation

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "logs:CreateLogGroup",
      "Resource": "arn:aws:logs:ap-northeast-2:your-account-id:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        // 특정 Lambda 함수의 로그 스트림을 생성하고 로그 이벤트를 기록할 수 있는 권한
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": [
        "arn:aws:logs:ap-northeast-2:381492021924:log-group:/aws/lambda/this-lambda-function:*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        // 특정 S3 버킷에 객체를 가져올 수 있는 권한
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::your-bucket/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        // RDS 인스턴스를 설명하고 연결할 수 있는 권한
        "rds:DescribeDBInstances",
        "rds-db:connect"
      ],
      "Resource": "*"
    }
  ]
}

```

### Code Explanation

```python
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
    
    # RDS에서 이메일 주소 조회
    recipient_email = get_recipient_email_from_rds(original_file_name)
    
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
```

### Event Trigger

이 Lambda 함수는 AWS S3에 AWS Transcribe 결과 텍스트 파일이 업로드될 때 트리거됩니다.

### Workflow

1. **트리거**: S3 버킷에 텍스트 파일이 업로드되면 함수가 트리거됩니다.
2. **파일 다운로드**: S3 버킷에서 텍스트 파일을 다운로드합니다.
3. **이메일 주소 조회**: RDS 데이터베이스에서 파일 이름을 기반으로 수신자의 이메일 주소를 조회합니다.
4. **이메일 전송**: 조회한 이메일 주소로 텍스트 파일을 첨부하여 이메일을 전송합니다.

### Logging

Lambda 함수는 이메일 전송 성공 여부 및 오류 메시지를 CloudWatch에 기록합니다.

### Conclusion

이 Lambda 함수는 S3에 AWS Transcribe 결과 텍스트 파일이 업로드될 때 자동으로 트리거되어, 해당 파일을 다운로드하고, 데이터베이스에서 이메일 주소를 조회하여 파일을 첨부한 이메일을 전송합니다. 모든 사전 요구 사항을 충족하고 함수가 AWS 환경에서 적절하게 구성되고 테스트되었는지 확인하십시오.