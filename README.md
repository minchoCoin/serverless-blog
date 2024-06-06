# 소개
2024년 1학기에 수강한 클라우드 컴퓨팅의 텀프로젝트이다.
# 프로젝트명
AWS Transcribe를 사용한 음성을 글자로 변환(Speech-To-Text)해주는 웹사이트 제작

- AWS Transcribe를 사용한 음성노트(SpeechNote) 웹사이트 제작

# 프로젝트 멤버 및 역할 분담
| name | part |
|------|------|
|김태훈|AWS 전체 구축, 파일 업로드 lambda 함수(file_upload_backend)구현      |
|박민재|이메일 전송 lambda 함수(save_text, send_email) 구현      |
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
10. eventbridge에서 save_text 람다 함수를 호출함(작업이름과 함께 호출).
11. save_text이 transcribe에 작업이름을 전송하여 변환 결과를 받는다.
12. 변환 결과를 s3에 파일로 저장한다.
13. s3에 변환결과가 업로드되면 send_email 람다 함수를 호출한다.
14. RDS DB에서 파일이름에 해당하는 이메일 주소 얻음
15. google SMTP를 사용하여 변환 결과를 파일 형태로 전송

구성 방법: [link](https://github.com/minchoCoin/stt-service/blob/main/%EC%8B%9C%EC%8A%A4%ED%85%9C%EA%B5%AC%EC%B6%95.pdf)

## 결과물 소개

동작 영상 : [link](https://youtu.be/KWpaLcgWzTE)

녹음파일 출처 : [link](https://www.nexusbook.com/innerFile/book/book_details.asp?bookID=6000)

### 웹페이지

![캡처15](https://github.com/minchoCoin/stt-service/assets/62372650/73158ad5-2231-4bad-8074-bb2835dd78ed)
(사진1 : 웹페이지를 들어가면 홈 화면은 다음과 같다.)
![image](https://github.com/minchoCoin/stt-service/assets/62372650/971dbaa3-e7aa-42ca-a65b-0b92a6fcbdd0)
(사진2 : 웹페이지 홈 화면을 확대한 모습. 왼쪽 상단에 Post를 눌러 음성파일(mp3)을 업로드할 수 있는 창으로 전환할 수 있다.)
![image](https://github.com/minchoCoin/stt-service/assets/62372650/1936b813-9db5-45f8-a048-d03d0ab57e5c)
(사진3 : 전환한 모습. 위쪽부터 이메일, 언어(영어,한국어, 중국어 일본어), 파일을 선택하고, Submit 버튼을 누르면 된다.)

![image](https://github.com/minchoCoin/stt-service/assets/62372650/3b8e1418-047c-4267-913d-e99e76af7b5d)
(사진4 : 임의로 입력한 모습)
![캡처2](https://github.com/minchoCoin/stt-service/assets/62372650/1f198dd1-5964-4758-98cd-a66efc284c33)
(사진5 : 지원되는 언어는 영어(미국), 한국어, 일본어, 중국어 이다.)
![image](https://github.com/minchoCoin/stt-service/assets/62372650/de3bd893-fb1c-41ba-9889-20abd7d38563)
(사진6 : Submit 버튼을 누르면 잠시 후 File and email uploaded successfully 알람이 뜬다. 프론트엔드에서 AWS API GateWay 주소로 formdata 형식으로 요청을 보낸다. API GateWay는 file_upload_backend 함수와 연결되어 있으며, 이 함수는 s3에 파일을 업로드한다. 람다 함수의 특성상 약 6MB 이상의파일은 업로드할수 없다.)
### 백엔드
![캡처5](https://github.com/minchoCoin/stt-service/assets/62372650/0ae19802-91a1-4c90-a6cc-2ffe2102fd2e)
(사진7 : s3://bucket/input_audio에 업로드한 오디오파일이 저장된다. 이름 중복을 막기 위해 padding 및 nonce를 추가하여 저장한다.)
![캡처12](https://github.com/minchoCoin/stt-service/assets/62372650/67bf1a27-f7c0-4b91-943a-e4445a1b5929)
(사진8 : file_upload_backend 함수는 파일 이름과 그에 해당하는 이메일 주소 및 언어를 RDS DB에 저장한다.)
![캡처6](https://github.com/minchoCoin/stt-service/assets/62372650/d0c4f8f6-0047-4a19-9b9b-c95044ec382d)
(사진9 : s3에 파일이 업로드되면, audio_transcribe 람다 함수가 호출되고, 이 함수는 transcribe 서비스에 변환 작업을 생성한다(RDS DB에서 언어 코드를 받아온다).)
![캡처7](https://github.com/minchoCoin/stt-service/assets/62372650/3439b52f-67d4-45a6-8539-892e5cddfd62)
(사진10 : 위와 같이 작업이 생성된다.)
![캡처8](https://github.com/minchoCoin/stt-service/assets/62372650/6af4c5f0-02d7-420f-b2dd-968133826afb)
(사진11 : 작업이 완료되면 AWS transcribe 서비스 페이지에서 작업 결과를 볼 수 있다.)
![캡처9](https://github.com/minchoCoin/stt-service/assets/62372650/88cfc02d-0442-487f-a6e8-4d5c437f7bdf)
(사진12 : 작업이 완료되면 eventbridge와 cloudwatch가 이를 감지하여 save_text 함수를 호출한다. 이 함수는 변환 결과를 transcribe서비스로 부터 받아서 s3에 저장한다. 즉 s3://bucket/output_text에 저장한다)
![캡처10](https://github.com/minchoCoin/stt-service/assets/62372650/e4bba53f-1aa3-4e2d-8b91-5ccd4aeabbc3)
(사진13 : s3에 output_text 밑에 txt 파일이 저장되면, send_email 람다 함수가 호출된다. 이 함수는 저장된 txt 파일(파일 이름은 업로드된 음성파일의 이름과 동일)을 DB에 저장된 이메일 주소로 전송한다. )
![캡처11](https://github.com/minchoCoin/stt-service/assets/62372650/b2904716-490a-42f5-9260-59354cb64bdf)
(사진14 : 위와 같이 변환 결과를 이메일로 받을 수 있다.) 아래는 변환 결과 예시이다.

```
Day till what's your departure date? I'd like to leave on the 10th of July. When are you leaving? When are you planning to leave? When would you like to depart? What's your return date? When will you return? When would you like to return? What day will you be returning? My return date is July 24th. What's the departure time? What's the arrival time? Your flight will arrive at 10:30 a.m. local time. Are you traveling alone? No, I'm traveling with my family.
```

## 주요 AWS 설정 설명
자세한 것은 [시스템구축.pdf](https://github.com/minchoCoin/stt-service/blob/main/%EC%8B%9C%EC%8A%A4%ED%85%9C%EA%B5%AC%EC%B6%95.pdf)을 참고하세요.

### s3 정적 웹사이트 호스팅
![image](https://github.com/minchoCoin/stt-service/assets/62372650/69f97152-3fea-4efa-b229-498067634e00)

웹사이트를 호스팅할 s3를 하나 만들고, 정적 웹사이트 호스팅을 하도록 설정한다. 접속하면 index.html을 반환하도록 한다.

### cloudfront 설정
![image](https://github.com/minchoCoin/stt-service/assets/62372650/1f6e2b43-4f77-4b3b-ac56-7e5d69468f31)
cloudfront를 사용하여 s3에 있는 정적 웹사이트를 호스팅한다. cloudfront를 사용하면 https가 적용된다.

### API GateWay 생성 및 람다 함수 연결
![image](https://github.com/minchoCoin/stt-service/assets/62372650/a19b6c66-f3b8-43c0-a413-787711c23a38)

API GateWay를 생성한다. API GateWay는 람다 함수와 연결하고, lambda 프록시 통합을 설정하여 formdata형식의 데이터를 정상적으로 받을 수 있도록 한다.

![image](https://github.com/minchoCoin/stt-service/assets/62372650/b35f767f-25bd-49c9-87a6-934d932cab06)

file_upload_backend 람다 함수는 API GateWay에 의해 트리거 된다.

### s3 생성 및 람다 함수 연결
![image](https://github.com/minchoCoin/stt-service/assets/62372650/489e1947-43c2-4e8b-ad09-f31d5b547644)

s3 bucket에 /input_audio 밑에 .mp3 파일이 업로드(put)되면 람다 함수를 호출하는 것으로 설정한다.

![image](https://github.com/minchoCoin/stt-service/assets/62372650/52dbaf3e-81b6-407d-8ed2-1d3ef6867777)

호출할 람다 함수는 업로드된 오디오파일을 transcribe에 변환 요청하는 audio_transcribe 람다 함수로 설정한다.

![image](https://github.com/minchoCoin/stt-service/assets/62372650/e4dd4c74-8c70-44d0-b0af-7ce1cf05f664)

s3에 의해 audio_transcribe가 트리거 됨을 알 수 있다.

### eventbridge 설정

![image](https://github.com/minchoCoin/stt-service/assets/62372650/3cfa6024-8129-49d5-b770-bb906986df01)

eventbridge에서 transcribe 작업이 완료됨을 감지하도록 설정한다.

![image](https://github.com/minchoCoin/stt-service/assets/62372650/1d1782f7-9578-4986-825d-6484c037acbe)

해당 이벤트가 발생하면 save_text 람다 함수를 호출하도록 설정한다.

![image](https://github.com/minchoCoin/stt-service/assets/62372650/b2262438-ec1f-4fab-91a2-e3322dc8af84)

이제 eventbridge에 의해 save_text가 호출됨을 알 수 있다.

### 핵심 코드
```py
transcribeClient = boto3.client('transcribe')

    try:
        transcribeClient.start_transcription_job(
            TranscriptionJobName=jobName,
            LanguageCode=languageCode,
            MediaFormat='mp3',
            Media={
                'MediaFileUri': f's3://{bucketName}/{baseFileName}'
            },
        )
        ...
    except Exception as e: 
        ...
```
python의 boto3 라이브러리를 이용하여 transcription job을 생성한다. jobname과 언어코드, 포멧(mp3), 음성 파일 위치를 전달하여 생성한다.

참고 : save_text 및 send_email 함수 설명
- save_text 설명 : [save_text/README.md](https://github.com/minchoCoin/stt-service/blob/main/src/save-text/README.md)
- send_email 설명 : [send_email/README.md](https://github.com/minchoCoin/stt-service/blob/main/src/send-email/README.md)


# 사용 방법
1. 먼저 [https://d3yte1ymgtgsl.cloudfront.net/](https://d3yte1ymgtgsl.cloudfront.net/) 에 접속하세요. 접속하면 아래와 같이 나옵니다.
![캡처15](https://github.com/minchoCoin/stt-service/assets/62372650/73158ad5-2231-4bad-8074-bb2835dd78ed)
2. 왼쪽 상단에 post를 누르면 아래 화면과 같이 이메일 주소와 파일을 업로드할 수 있는 form이 나옵니다.
![image](https://github.com/minchoCoin/stt-service/assets/62372650/1936b813-9db5-45f8-a048-d03d0ab57e5c)
3. 이메일 주소와 언어, 파일을 선택합니다. 람다 함수의 특성상 6MB 이상의 파일은 업로드 할수 없습니다.
![캡처13](https://github.com/minchoCoin/stt-service/assets/62372650/6d626f05-a85e-4e44-b99e-adcfda1f03f8)
4. 사용할 수 있는 언어는 영어(미국), 한국어, 일본어, 중국어 입니다.
![캡처2](https://github.com/minchoCoin/stt-service/assets/62372650/1f198dd1-5964-4758-98cd-a66efc284c33)
5. Submit 버튼을 누르면 잠시 후 File and email uploaded successfully 알람이 발생합니다. 변환이 완료되고 이메일로 전송되기 까지 시간이 약간 걸릴 수 있습니다.
![캡처4](https://github.com/minchoCoin/stt-service/assets/62372650/b9fc19ba-3554-4c4d-999c-ef06cef2fcf7)
6. 제출한 이메일로 파일이 전송됩니다. 텍스트파일 형태로 전송됩니다.
![캡처10](https://github.com/minchoCoin/stt-service/assets/62372650/e4bba53f-1aa3-4e2d-8b91-5ccd4aeabbc3)
7. 전송된 텍스트 파일에서 변환된 결과를 확인할 수 있습니다.
![캡처11](https://github.com/minchoCoin/stt-service/assets/62372650/b2904716-490a-42f5-9260-59354cb64bdf)
아래는 변환 결과 예시이다.
```
Day till what's your departure date? I'd like to leave on the 10th of July. When are you leaving? When are you planning to leave? When would you like to depart? What's your return date? When will you return? When would you like to return? What day will you be returning? My return date is July 24th. What's the departure time? What's the arrival time? Your flight will arrive at 10:30 a.m. local time. Are you traveling alone? No, I'm traveling with my family.
```
# 활용방안
1. 강의 녹음을 글로 변환
강연이나 강의 녹음을 들으면서 정리할 필요없이 이 서비스를 이용해 글로 변환하여 읽으면서 복습할 수 있습니다.

[강연 노트 예시](https://youtu.be/OcK3Uqlg2kE)를 변환해보겠습니다. 동작 영상은 [link](https://youtu.be/SEC13EslJKc)에서 볼 수 있습니다.

아래는 이메일로 전송된 파일 예시입니다.(일부 후략)(lecturenote2minchocoin576724248.txt)
```
인공 지능은 일반적으로 인간의 지능이 필요하거나 인간이 분석할 수 있는 것보다 규모가 큰 데이터를 포함하는 방식으로 추론, 학습 및 행동할 수 있는 컴퓨터 및 기계를 구축하는 것과 관련된 과학 분야입니다. 먼저, 인공지능 학습 모델에 대해 말씀드리겠습니다. 비즈니스에서 AI 를 이야기할 때 학습 데이터에 관해 이야기하는 경우가 많습니다. 그것은 무엇을 의미할까요? 제한된 메모리 인공지능은 새로운 데이터로 학습 하여 시간이 지남에 따라 개선되는 AI 입니다. 머신러닝 은 알고리즘으로 데이터를 학습 하여 결과를 얻는 인공 지능의 허위 집합 입니다. 일반적으로 머신러닝 에는 세 가지 유형의 학습 모델이 사용됩니다. 지도 학습은 라벨이 지정된 학습 데이터를 사용하여 특정 입력을 출력에 매칭 하는 머신러닝 모델입니다. 간단히 말해, 고양이 사진을 인식 하도록 알고리즘을 훈련 시키려면 고양이라는 라벨이 지정된 사진을 필드 합니다 비 지도 학습은 라벨이 지정되지 않은 데이터를 기반으로 패턴을 학습하는 머신 러닝 모델입니다. 
```

2. 음성 메모
메모할 내용을 녹음하고, 이 서비스를 이용해 텍스트로 변환하여 타이핑 없이 메모할 수 있습니다.

# 개선 방향
- 앱으로 만들어 파일 업로드 등의 관점에서 접근성을 높인다.
- 24시간 또는 1개월 당 변환할 수 있는 음성 파일 시간을 제한한다.
    - 이를 위해 로그인 기능을 구현하여 계정마다 시간을 제한한다.
- 이메일을 보내는 방식이 아니라 웹에서 바로 확인할 수 있도록 한다.
- clova note와 같이 AI 요약 서비스 제공
- 사용자 지정 단어집 제공
- 파일을 s3에 바로 업로드하여 길이제한 없애기
    - 현재는 약 6MB의 제한이 있음

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
- vpc ipv6 setting : [https://hossamelshahawi.com/2021/10/24/fix-errno97-address-family-not-supported-by-protocol/](https://hossamelshahawi.com/2021/10/24/fix-errno97-address-family-not-supported-by-protocol/)
# License
[Apache License v2.0](https://www.apache.org/licenses/LICENSE-2.0)
