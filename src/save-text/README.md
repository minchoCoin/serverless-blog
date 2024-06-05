# save-text

## AWS Transcribe 작업 결과를 S3에 저장하는 AWS Lambda 함수

이 AWS Lambda 함수는 AWS Transcribe 작업이 완료되면, 변환 결과를 가져와서 텍스트 파일로 S3 버킷에 저장하는 기능을 수행합니다. AWS 서비스와 상호작용하기 위해 AWS SDK와 Python의 내장 라이브러리를 사용합니다.

### Prerequisites

- AWS 계정
- AWS Lambda 설정
- AWS Transcribe 설정
- S3 버킷
- Lambda가 S3와 Transcribe에 접근할 수 있는 IAM 역할
- 환경 변수 `BUCKET_NAME`를 대상 S3 버킷 이름으로 설정

### Installation

1. **S3 버킷 생성**:
    - 변환된 텍스트 파일을 저장할 S3 버킷을 생성합니다.

2. **IAM 역할 생성**:
    - S3에 읽기/쓰기 및 AWS Transcribe 접근 권한이 있는 IAM 역할을 생성합니다.
   - 다음 정책을 역할에 첨부합니다:
   - `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` - CloudWatch Logs에 대한 권한
   - `transcribe:GetTranscriptionJob` - AWS Transcribe 작업 정보에 대한 권한
   - `s3:PutObject` - S3 버킷에 객체를 업로드할 수 있는 권한

3. **Lambda 함수 설정**:
    - 새로운 AWS Lambda 함수를 생성합니다.
    - 위에서 생성한 IAM 역할을 Lambda 함수에 할당합니다.
    - 환경 변수 `BUCKET_NAME`를 S3 버킷 이름으로 설정합니다.

4. **코드 배포**:
    - 제공된 Python 코드를 Lambda 함수 편집기에 복사하여 붙여넣습니다.
    - 저장하고 Lambda 함수를 배포합니다.

### Environment Variables

- `BUCKET_NAME`: 변환된 텍스트를 저장할 S3 버킷의 이름입니다.

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
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": [
        // 특정 Lambda 함수의 로그 스트림을 생성하고 로그 이벤트를 기록할 수 있는 권한
        "arn:aws:logs:ap-northeast-2:your-account-id:log-group:/aws/lambda/this-lambda-function:*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        // 모든 Transcription Job 정보를 가져올 수 있는 권한
        "transcribe:GetTranscriptionJob"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        // 특정 S3 버킷에 객체를 업로드할 수 있는 권한
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::your-bucket/*"
    }
  ]
}
```

### Code Explanation

```python
import json
import boto3
import os
import urllib.request

# 환경 변수에서 버킷 이름을 가져옵니다
BUCKET_NAME = os.environ['BUCKET_NAME']

# AWS 리소스 초기화
s3 = boto3.resource('s3')
transcribe = boto3.client('transcribe')

def lambda_handler(event, context):
    # 이벤트 상세 정보에서 작업 이름을 가져옵니다
    job_name = event['detail']['TranscriptionJobName']
    
    # 변환 작업 세부 정보를 가져옵니다
    job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    
    # 변환 결과 URI를 가져옵니다
    uri = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
    print(uri)
    
    # URI에서 내용을 읽습니다
    content = urllib.request.urlopen(uri).read().decode('UTF-8')
    
    # 내용을 CloudWatch에 로그로 기록합니다
    print(json.dumps(content))
    
    # JSON 내용을 파싱합니다
    data = json.loads(content)
    
    # 변환된 텍스트를 추출합니다
    transcribed_text = data['results']['transcripts'][0]['transcript']
    
    # 변환된 텍스트를 S3에 업로드합니다
    object = s3.Object(BUCKET_NAME, job_name + ".txt")
    object.put(Body=transcribed_text)
```

### Event Trigger

이 Lambda 함수는 AWS Transcribe 작업 상태가 "COMPLETED"로 변경될 때 Amazon CloudWatch 이벤트 규칙에 의해 트리거됩니다.

### Workflow

1. **트리거**: Transcribe 작업이 완료되면 함수가 트리거됩니다.
2. **변환 결과 가져오기**: 함수는 Transcribe 작업 세부 정보에서 변환 결과 URI를 가져옵니다.
3. **변환문 다운로드**: 함수는 URI에서 변환문을 다운로드합니다.
4. **내용 기록**: 함수는 변환문 내용을 CloudWatch에 기록합니다.
5. **변환문 저장**: 함수는 변환문 내용을 파싱하여 지정된 S3 버킷에 텍스트로 저장합니다.

### Logging

함수는 변환 결과의 URI와 변환문 내용을 AWS CloudWatch에 로그로 기록하여 모니터링 및 디버깅을 용이하게 합니다.

### Conclusion

이 Lambda 함수는 AWS Transcribe에서 변환된 텍스트를 S3 버킷에 저장하는 과정을 자동화하여 변환된 데이터를 관리하고 접근하기 쉽게 만듭니다. 모든 사전 요구 사항을 충족하고 함수가 AWS 환경에서 적절하게 구성되고 테스트되었는지 확인하십시오.