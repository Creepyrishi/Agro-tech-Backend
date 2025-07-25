import logging
from flask import Flask, request, jsonify
import db
from datetime import datetime, timezone
import ai

# logging
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

## save_data endpoint
@app.route('/save_data', methods=['POST'])
def save_data():
    """
    This is the endpoint where Aurdino will post the data every 30 min or so.

    Expected data schema: {  
                    "device_id": "station-01",
                    "data": {
                        "temperature": 26.4,
                        "humidity": 61,
                        "soil_moisture": 432,
                        "gas_level": 230,
                        "ph_value": 6.7,
                        "soil_temperature": 23.5,
                        "light_intensity": 320
                    }
                }
    """

    data = request.get_json()

    # Predicting and appeding in data to store
    prediction = ai.predict_flammability(data)
    data["timestamp"] = datetime.now(timezone.utc)
    data["prediction"] = prediction

    try:
        if db.save_data(data):
            return jsonify({'status': 'sucess'}), 200
        else:
            logging.error('Failed to save data: Database operation unsuccessful.')
            return jsonify({'status': 'failed'}), 500
    
    except Exception as e:
        logging.error(f'Error occurred: {e}') 
        return jsonify({'status': 'failed'}), 500


## Get data endpoint
@app.route('/get_all_data', methods = ['GET'])
def get_all_data():
    """
    This function returns all dataspresent in the database which are sorted by time latest to oldest.
    response scheme: [{  
        "_id": "235235",
        "device_id": "station-01",
        "timestamp": "utc",
        "data": {
            "temperature": 26.4,
            "humidity": 61,
            "soil_moisture": 432,
            "gas_level": 230,
            "ph_value": 6.7,
            "soil_temperature": 23.5,
            "light_intensity": 320
        },
        "prediction": 34
    }]
    """
    datas = db.get_all_data()
    if datas:
        return jsonify(datas)
    else:
        return jsonify({'status': 'failed'}), 500


@app.route('/get_current_data', methods = ['GET'])
def get_current_data():
    """
    This function returns lastest data point.
    response scheme: {  
        "_id": "235235",
        "device_id": "station-01",
        "timestamp": "utc",
        "data": {
            "temperature": 26.4,
            "humidity": 61,
            "soil_moisture": 432,
            "gas_level": 230,
            "ph_value": 6.7,
            "soil_temperature": 23.5,
            "light_intensity": 320
        },
        "prediction": 34
    }
    """
    data = db.get_current_data()
    if data:
        return jsonify(data[0])
    else:
        return jsonify({'status': 'failed'}), 500


## Chat route
@app.route("/chat", methods=["POST"])
def chat():
    """
    This is chat route which takes a json in body and response markdown text in text/plain content-type.
    Expected Json body: {
    _id : (IMEI number maybe)
    message : Chat
    }
    """

    data = request.get_json()
    message = data.get("message")
    _id = data.get("_id")
    if not db.update_chat(_id, {'role': 'user', 'content': message}):
        return jsonify({'status': 'failed'}), 500
    
    response = ai.get_explanation(_id)
    if not db.update_chat(_id, {'role': 'assistant', 'content': response}):
        return jsonify({'status': 'failed'}), 500
    
    if not response:
        return jsonify({'status': 'failed'}), 500
    
    return response, {'Content-Type' : 'text/plain'}

if __name__ == '__main__':
    app.run(debug=True)