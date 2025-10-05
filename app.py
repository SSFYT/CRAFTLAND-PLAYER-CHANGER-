from flask import Flask, request, send_file, jsonify
from io import BytesIO

# Server ko shuru karo
app = Flask(__name__)

# File badalne wala function (Chef ka asli kaam)
def modify_player_data(file_bytes, target_player_id):
    """
    Craftland file ke player slot ko badalta hai.
    """
    
    # Offset 16507 (0x407B) par player slot ki value store hai.
    # Yeh number aapne Hex Editor se dhoondha hai.
    PLAYER_ID_OFFSET = 16507 
    
    # Naye player ki ID ko integer (number) meṅ badlo
    try:
        # User player 1, 4, 15 chuneṅge, aur wahi value file meṅ jayegi.
        player_id_int = int(target_player_id) 
    except ValueError:
        # Agar galti ho, toh original file wapas kar do.
        return file_bytes
    
    # File ko aasan list (array) meṅ badlo
    data_list = list(file_bytes)
    
    # Check karo ki file itni lambi hai ya nahin
    if PLAYER_ID_OFFSET < len(data_list):
        
        # ➡️ MAGIC HO GAYA! ⬅️
        # File ki 16507th jagah par naye player ka number daal do.
        data_list[PLAYER_ID_OFFSET] = player_id_int 
        
        # Badle hue data ko wapas .bytes file bana do
        modified_bytes = bytes(data_list)
        return modified_bytes
    else:
        # Agar file bahut choti ho, toh original file wapas kar do.
        return file_bytes

# Woh rasta (API Route) jahan front-end file bhejega
@app.route('/api/change_player', methods=['POST'])
def change_player():
    
    # Check karo ki file aur player chuna gaya hai ya nahin
    if 'projectFile' not in request.files or not request.form.get('playerSelect'):
        return jsonify({"error": "File ya Player nahi chuna gaya."}), 400

    file = request.files['projectFile']
    target_player = request.form.get('playerSelect')
    
    # Front-end se bheja gaya asli naam yahan le rahe hain
    # (Jisse file ka naam download meṅ wapas wahi rahe)
    original_filename = request.form.get('original_filename') 
    
    if not original_filename:
        # Agar Front-end ne naam nahin bheja, toh file ka naam istemal karenge
        original_filename = file.filename 

    file_data = file.read()
    
    # File badal do (Offset 16507 par)
    modified_data = modify_player_data(file_data, target_player)
    
    # Wapas bhej do
    output = BytesIO(modified_data)
    
    # ✅ Download_name meṅ sirf asli naam istemal kiya gaya hai
    return send_file(
        output,
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name=original_filename # Filename bilkul waisa hi rahega
    )

# Server ko shuru karne ki command (Render iska istemal karta hai)
if __name__ == '__main__':
    # Yeh local testing ke liye hai. Render par yeh alag se chalta hai.
    app.run(debug=True, port=5000)
