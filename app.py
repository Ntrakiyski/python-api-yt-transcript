from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flasgger import Swagger

import video_processor  # Import the updated module with video processing logic

app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)

class VideTranscr(Resource):
    def post(self):
        """
        This method responds to the POST request for adding a new record to the DB table.
        ---
        tags:
        - Records
        parameters:
            - in: body
              name: body
              required: true
              schema:
                required:
                  - videoURL
                properties:
                  videoURL:
                    type: string
                    description: YouTube video URL
        responses:
            200:
                description: Successfully processed the YouTube video URL and retrieved video information, transcript, and chapters.
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        status:
                          type: string
                          example: success
                        videoInfo:
                          type: object
                          description: Information about the video.
                        chapters:
                          type: array
                          items:
                            type: object
                            description: Details of video chapters with transcripts.
            400:
                description: Invalid request or unable to process the YouTube video URL.
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        status:
                          type: string
                          example: error
                        message:
                          type: string
                          example: The videoURL parameter is missing or invalid.
        """
        data = request.json
        
        # Extract the videoURL from the incoming JSON data
        video_url = data.get('videoURL')
        
        if not video_url:
            return {'message': 'videoURL is required'}, 400
        
        # Call the process_video_url function from video_processor
        result = video_processor.process_video_url(video_url)
        
        # Return the result of processing
        return jsonify(result)

api.add_resource(VideTranscr, "/video")

if __name__ == "__main__":
    app.run(debug=True)
