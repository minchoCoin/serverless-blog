import mysql from "mysql2/promise.js";
const pool = mysql.createPool({
    host: 'mysqldb.abcdefghijklm.ap-northeast-2.rds.amazonaws.com',
    database: 'mydbname',
    user: 'myusername',
    password: 'mypassword',
    port: 3306,
    connectionLimit: 20,
});
import buildRes from "./util.mjs"

import fileProcessingService from "./file-processing-service.mjs"
const fileUploadPath = '/file-upload'



export const handler = async (event, context) => {
  
  
  //console.log('Request Event: ', event);
    let response;
    if (event.httpMethod === 'POST' && event.path === fileUploadPath){
        response = await fileProcessingService(event.body);
        if(response.statusCode!=200){
          return response;
        }
      }
            
    else{
      response = buildRes(404);
      return response;
    }
          
  
  context.callbackWaitsForEmptyEventLoop = false;
  
  let fileInfo = JSON.parse(response.body);
  
  let email = fileInfo.email;
  let fileName = fileInfo.filename;
  let languageCode = fileInfo.languageCode;
  
  
  const connection = await pool.getConnection(async conn => conn);
  try {
    let x=await connection.query(`INSERT INTO fileTable VALUES ('${email}', '${fileName}', '${languageCode}',NOW());`);
    //console.log(x)
  } catch (err) {
    console.log(err);
    response = buildRes(500,{'message':'file upload is completed, but error occured in RDS DB'});
    
  } finally {
    connection.release();
  }
  return response;
};
