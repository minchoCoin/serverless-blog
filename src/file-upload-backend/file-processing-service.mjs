// file-processing-service.js
import { PutObjectCommand, S3Client } from "@aws-sdk/client-s3";
import buildRes from "./util.mjs"
const bucketName = 'mybucket'; // S3 버킷이름 입력
const s3Subfolder = 'input_audio';
const client = new S3Client({});


import mysql from "mysql2/promise.js";
const pool = mysql.createPool({
    host: 'mysqldbhost.xxxxxxxxxxxx.ap-region.rds.amazonaws.com',
    database: 'mysqldb',
    user: 'username',
    password: 'mypassword',
    port: 3306,
    connectionLimit: 20,
});



async function process(requestBody,context){
    //console.log(requestBody);
    let response;
    const tmp = requestBody.split('\r\n');
    
    const email =tmp[3].replace(/^"|$/g, '').trim();
    let filename=tmp[7].replace(/^"|$/g, '').trim();
    const languagecode = tmp[11].replace(/^"|$/g, '').trim();
    const byteCharacters = Buffer.from(tmp[16].trim(), 'base64');
    
    //change filename
    filename = filename.split(".")[0] + email.split('@')[0] + (Math.floor(Math.random() * 2000000000)).toString() + '.mp3';
  
  
  const connection = await pool.getConnection(async conn => conn);
  try {
    let x=await connection.query(`INSERT INTO fileTable VALUES ('${email}', '${filename}', '${languagecode}',NOW());`);
    //console.log(x)
  } catch (err) {
    console.log(err);
    response = buildRes(500,{'message':'error occured in RDS DB'});
    return response;
    
  } finally {
    connection.release();
  }
    
    
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