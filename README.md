# 소개
2024년 1학기에 수강한 클라우드 컴퓨팅의 텀프로젝트이다.
# 프로젝트명
AWS Transcribe를 사용한 음성을 글자로 변환(Speech-To-Text)해주는 웹사이트 제작

# 프로젝트 멤버 및 역할 분담
| name | part |
|------|------|
|김태훈|AWS 전체 구축, 파일 업로드 lambda 함수(file_upload_backend)구현      |
|박민재|이메일 전송 lambda 함수(send_email) 구현      |
|김성문|오디오 텍스트 변환 lambda 함수(audio_transcribe) 구현      |
|박재열|웹페이지(프론트엔드) 구현|

# 프로젝트 소개
AWS Transcribe를 사용한 음성을 텍스트로 변환(STT)해주는 서비스를 만드는 프로젝트입니다. 사용자가 음성 파일을 이메일 주소, 언어코드와 함께 웹사이트를 통하여 업로드하면, 텍스트로 변환되어 사용자의 이메일로 전송됩니다. 

사용되는 클라우드 서비스는 Amazon CloudFront, Amazon S3, Amazon API GateWay, AWS Lambda, Amazon RDS, AWS Transcribe, AWS CloudWatch입니다. 이 프로젝트에서 각각의 용도는 다음과 같습니다.

## Amazon CloudFront
S3에 저장된 웹페이지를 캐싱하여, 사용자가 S3에 직접 접근하지 않고, 근처에 있는 CloudFront에서 웹페이지 파일을 다운로드받을 수 있게 한다. S3 퍼블릭 엑세스를 차단할 수 있으므로 보안을 강화할 수 있고, https가 적용된다.
## Amazon S3
정적 웹페이지에 필요한 파일(html 등)을 저장하고, 사용자가 업로드한 오디오 파일과 텍스트로 변환된 결과를 저장한다. 만약 s3에 오디오 파일이 업로드 되면, 텍스트 변환을 담당하는 lambda 함수를 호출하게 된다.
## Amazon API GateWay
사용자와 lambda 함수를 연결시켜준다. 사용자가 해당 API주소로 오디오 파일과 이메일 정보 등을 전송하면, API GateWay는 전송받은 정보와 함께 lambda 함수를 호출한다. lambda 함수에서 반환된 값은, 사용자에게 전달한다.

![image](https://github.com/minchoCoin/stt-service/assets/62372650/b427592b-cfb1-4ad0-8e04-c9fd79d15652)

위 그림과 같이 API GateWay를 통해 lambda 함수가 호출된다.

## AWS Lambda
Lambda는 서버리스 서비스로서, 서버 없이 함수로만 구성되어 있다. 이 함수는 event를 매개변수로 받아 response를 반환한다. nodejs, python, java 등으로 함수를 구성할 수 있으며, 시스템의 lambda 함수들의 언어가 같을 필요가 없다. 이 프로젝트에서, lambda 함수를 이용하여 오디오 파일을 S3에 저장하고, 이메일 정보 등을 DB에 저장하고, transcribe를 요청하며, 텍스트로 변환된 파일을 이메일로 전송한다.

![image](https://github.com/minchoCoin/stt-service/assets/62372650/28dd26fc-ba06-40b8-94f2-2e17e0c61378)

위 그림은 python으로 제작한 간단한 lambda 함수이다. event를 받아 응답코드 및 json을 반환한다.

## Amazon RDS
사용자에게서 받은 오디오 파일과 관련된 정보를 저장한다. 이 프로젝트에서는 mysql을 사용하며, 서로 다른 lambda 함수끼리 정보(이메일, 언어 코드 등)를 공유할 때 필요하다. table의 구성은 아래와 같다.
```
fileTable(
 email VARCHAR(320) NOT NULL,
 filename VARCHAR(600) NOT NULL,
 language VARCHAR(10) NOT NULL,
 time TIMESTAMP NOT NULL
)
```
## AWS CloudWatch and EventBridge 
AWS에서 제공하는 모니터링 서비스이다. 원래는 리소스 사용률 등을 모니터링할 수 있고, 일정 사용률 초과 등의 이벤트가 발생하면 사용자에게 알리는 기능을 가지고 있다. 이 프로젝트에서는 이를 활용하여, 오디오 텍스트 변환이 완료되면, 이를 CloudWatch가 탐지한다. EventBridge가 CloudWatch에서 텍스트 변환 완료 이벤트가 생성된 것을 확인하고, 이메일을 보내는 lambda 함수를 호출하게 된다.
Transcribe를 요청하는 lambda 함수에서 이메일까지 처리하지 않는 이유는, lambda 함수의 동작 시간은 최대 15분인데, 변환은 그보다 오래 걸릴 수 있기 때문이다.
![image](https://github.com/minchoCoin/stt-service/assets/62372650/568eea2d-8007-418d-8127-34ea4460aecd)

cloudwatch에서 이벤트를 감지하면, EventBridge가 lambda 함수를 호출한다.

![image](https://github.com/minchoCoin/stt-service/assets/62372650/dcbc99eb-f00b-4f46-994a-4d5737baa49a)

EventBridge가 lambda 함수를 호출할 이벤트 패턴은 위와 같다.

# 필요성 및 활용방안
회의, 강의, 강연 등에서 녹음을 통해 다시 내용을 정리하거나 복습하곤 한다. 그러나 몇시간에 가까운 녹음 파일을 듣기에는 시간이 많이 걸린다. 따라서 이것을 텍스트로 변환하여 볼 필요가 있다. 따라서 AWS Transcribe서비스를 이용한 STT웹서비스를 구축하려고 한다.
이 서비스는 사용자가 텍스트로 변환하고 싶은 음성 파일이 있을 경우 웹에서 음성 파일을 이메일과 언어 정보와 함께 업로드하면, 사용자의 이메일로 변환된 텍스트가 파일(xxx.txt)형태로 전송된다.

# 선행기술 조사
네이버에서 개발한 [클로바노트(CLOVA note)](https://clovanote.naver.com/)는 웹이나 모바일 앱에서 음성을 녹음하거나 음성파일을 업로드하면, 그것을 텍스트로 변환해주고, 이것을 시간과 화자와 함께 보여준다.
![image](https://github.com/minchoCoin/stt-service/assets/62372650/a45579b9-a4f7-4b24-b330-812b1eb8a19c)

(그림 1 클로바노트에서 음성 기록이 생성된 화면 [출처](https://blog.naver.com/clova_ai/222846847424))

녹음 파일 업로드 시 월 300분의 제한이 있으며, 녹음 파일의 길이는 180분으로 제한된다. 앱이나 웹에서 녹음 시, 1회 녹음은 180분으로 제한되지만, 텍스트 변환은 제한이 없다. 다만 300분 초과시 텍스트 변환 속도가 매우 느려진다(최대 24시간). 아직 유료 요금제는 제공되지 않는다.
클로바노트는 추가로 AI요약 기능도 있다. AI 요약기능은 월 10회 제공하며 아래와 같이 요약하여준다.

![image](https://github.com/minchoCoin/stt-service/assets/62372650/6abbf4b9-1e6e-4189-9ffe-c443b732122f)

(그림 2 클로바노트에서 AI요약을 실행한 장면 [출처](https://blog.naver.com/clova_ai/222846847424))

# 프로젝트 개발 결과물
## 구상도
![image](https://raw.githubusercontent.com/minchoCoin/stt-service/main/diagram/diagram.png)

1. 사용자가 cloudfront를 통해 정적 웹페이지에 접속한다.

2. cloudfront는 s3에 저장된 컨텐츠(html,css,js 등)를 가져와서 사용자에게 전달하거나 캐싱된 웹페이지를 전달한다.

3. 사용자가 웹페이지에서 이메일, 언어코드, 음성파일을 첨부하여  API로 POST요청을 보낸다.

4. API GateWay는 사용자에게서 받은 정보와 파일을 request에 담아 file_upload_backend를 호출한다.
5. 해당 lambda 함수는 이메일, 언어코드, 파일명, 시간을 RDS에 기록한다.
6. 해당 lambda 함수는 S3에 파일을 업로드한다.

7. S3에 파일이 업로드되면, S3는 audio_transcribe 람다 함수를 호출한다(이때 업로드된 파일명이 전달된다).
8. RDS에서 업로드된 파일명에 해당하는 언어 코드를 전달받고, S3에 저장된 음성파일 경로를 작업이름, 언어코드와 함께 transcribe에 텍스트 변환 요청한다(작업이름은 파일이름으로 설정)
9. 변환이 완료되면, cloudwatch가 이를 감지
10. eventbridge에서 send_email 람다 함수를 호출함(작업이름과 함께 호출).
11. send_email이 transcribe에 작업이름을 전송하여 변환 결과를 받는다.
12. 변환 결과를 s3에 파일로 저장한다.
13. 작업이름(=파일이름)에 해당하는 이메일 주소를 RDS에서 확인한다.
14. 변환 결과를 파일로 첨부하여 이메일(google SMTP)로 전송한다.
# 사용 방법

# 활용방안


# references
- [https://devocean.sk.com/blog/techBoardDetail.do?ID=163934](https://devocean.sk.com/blog/techBoardDetail.do?ID=163934)
- [https://aws.amazon.com/ko/what-is/serverless-computing/](https://aws.amazon.com/ko/what-is/serverless-computing/)
- [https://docs.aws.amazon.com/transcribe/latest/dg/getting-started.html](https://docs.aws.amazon.com/transcribe/latest/dg/getting-started.html)
- cloudfront 사용 : [link](https://duckgugong.tistory.com/336)
- 파일 업로드 웹 페이지 구축 : [link](https://heytech.tistory.com/403)
- s3 trigger lambda(and lambda call transcribe) : [link](https://medium.com/@manishdiddi03/automating-audio-transcription-how-to-use-aws-api-gateway-s3-sns-lambda-and-transcribe-to-20c220b1e77f)
- lambda language code : [link](https://docs.aws.amazon.com/transcribe/latest/dg/supported-languages.html)
- transcribe API guide: [link](https://docs.aws.amazon.com/transcribe/latest/APIReference/API_StartTranscriptionJob.html)
- sending email : [link](https://aws.amazon.com/ko/blogs/media/amazon-transcribe-and-email-integration/)
- using CloudWatch : [link](https://medium.com/analytics-vidhya/transcribing-audio-files-with-amazon-transcribe-lambda-s3-474dc9a1ced7)
- connect lambda and RDS DB : [link](https://velog.io/@chaduri7913/AWS-RDS-Lambda-%EC%97%B0%EA%B2%B0%ED%95%98%EA%B8%B0)
    - https://jane-aeiou.tistory.com/51
- google SMTP 사용 : [https://icedhotchoco.tistory.com/entry/sending-email-with-python](https://icedhotchoco.tistory.com/entry/sending-email-with-python)

# License
[Apache License v2.0](https://www.apache.org/licenses/LICENSE-2.0)
