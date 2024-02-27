from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import ipapi


app = Flask('app')

# Configure your MySQL connection
db = mysql.connector.connect(
    host="securityapp.czp1fr3ynvvj.ap-south-1.rds.amazonaws.com",
    user="admin",
    password="securityapp",
    database="security_app")
cursor = db.cursor()

# Create 'location_data' table if not exists
create_location_data_query = """
CREATE TABLE IF NOT EXISTS location_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(255),
    region VARCHAR(255),
    country VARCHAR(255),
    ip VARCHAR(15)
);
"""
cursor.execute(create_location_data_query)

# Create 'phone_video_data' table if not exists
create_phone_video_data_query = """
CREATE TABLE IF NOT EXISTS phone_video_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country_id VARCHAR(255),
    phone_number VARCHAR(20),
    video_link VARCHAR(255),
    FOREIGN KEY (country_id) REFERENCES location_data(id)
);
"""
cursor.execute(create_phone_video_data_query)
print('hi')


@app.route('/', methods=['GET', 'POST'])
def Index():
  data = ipapi.location(output='json')
  country_name = data.get('country', '')
  cursor.execute(
      "SELECT mobile_number, video_file FROM PhoneNumberData WHERE country_name = %s",
      (country_name, ))
  result = cursor.fetchone()
  if result:
    phone_number, video_filename = result
  else:
    phone_number = '+92 12345 04321'  # You can set a default phone number here
    video_filename = 'video.mp4'  # Default video filename
  # Save data into 'location_data' table
  insert_location_query = """
  INSERT INTO location_data (city, region, country, ip)
  VALUES (%s, %s, %s, %s);
  """
  cursor.execute(insert_location_query,
                 (data.get('city', ''), data.get('region', ''),
                  data.get('country', ''), data.get('ip', '')))
  db.commit()
  return render_template('index.html',
                         data=data,
                         phone_number=phone_number,
                         video_filename=video_filename)


app.run(host='0.0.0.0', port=8080)