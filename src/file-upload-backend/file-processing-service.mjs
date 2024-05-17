// file-processing-service.js
import { PutObjectCommand, S3Client } from "@aws-sdk/client-s3";
import buildRes from "./util.mjs"
import { Blob } from 'buffer';
const bucketName = 'bucket-name'; // S3 버킷이름 입력
const s3Subfolder = 'input_audio';
const client = new S3Client({});
async function process(requestBody){
    //console.log(requestBody);
    const tmp = requestBody.split('\r\n');
    
    const email =tmp[3].replace(/^"|$/g, '').trim();
    let filename=tmp[7].replace(/^"|$/g, '').trim();
    const languagecode = tmp[11].replace(/^"|$/g, '').trim();
    const byteCharacters = Buffer.from(tmp[16].trim(), 'base64')
    /*
    const byteNumbers = new Array(byteCharacters.length);
for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
}

const byteArray = new Uint8Array(byteNumbers);

const blob = new Blob([byteArray], {type: 'audio/mpeg'});
*/
    //change filename
    filename = filename.split(".")[0] + email.split('@')[0] + (Math.floor(Math.random() * 2000000000)).toString() + '.mp3';
    
const command = new PutObjectCommand({
    Bucket: bucketName,
    Key: `${s3Subfolder}/${filename}`,
    Body: byteCharacters
  });
    
    
    try{
        const data = await client.send(command);
        const body = { 'message': 'File uploaded successfully', 'location': data.Location,'email': email, 'filename':filename,'languageCode' : languagecode};
        return buildRes(200,body);
        
    }
    catch (error){
        console.error('Error uploading file to S3:', error);
        return buildRes(500,{'message' : 'error uploading file to S3'});
    }
    
}

export default process;