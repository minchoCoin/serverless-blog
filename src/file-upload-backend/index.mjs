
import buildRes from "./util.mjs"

import fileProcessingService from "./file-processing-service.mjs"
const fileUploadPath = '/file-upload'



export const handler = async (event, context) => {
  context.callbackWaitsForEmptyEventLoop = false;
  //console.log('Request Event: ', event);
    let response;
    if (event.httpMethod === 'POST' && event.path === fileUploadPath){
        response = await fileProcessingService(event.body,context);
        return response;
      }
            
    else{
      response = buildRes(404);
      return response;
    }
};
