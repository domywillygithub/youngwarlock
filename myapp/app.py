from flask import Flask, render_template, request
import psycopg2
from send_mail import send_mail

app = Flask(__name__)

env = 'dev'

# Set the connection parameters based on the environment
if env == 'dev':
    app.debug = True
    connection_params = {
        "host": "dpg-clm80phfb9qs739926s0-a.oregon-postgres.render.com",
        "port": "5432",
        "database": "test_db_1bsx",  # Change to your actual database name
        "user": "test_db_1bsx_user",
        "password": "f1ytacejZ7RQcSRLqZl7m4aijEKt8V0x",
        #postgres://test_db_1bsx_user:f1ytacejZ7RQcSRLqZl7m4aijEKt8V0x@dpg-clm80phfb9qs739926s0-a.oregon-postgres.render.com/test_db_1bsx
    }
else:
    app.debug = False
    connection_params = {
        "host": "dpg-clm80phfb9qs739926s0-a",
        "port": "5432",
        "database": "test_db_1bsx",  # Change to your actual database name
        "user": "test_db_1bsx_user",
        "password": "f1ytacejZ7RQcSRLqZl7m4aijEKt8V0x"

        # postgres://test_db_1bsx_user:f1ytacejZ7RQcSRLqZl7m4aijEKt8V0x@dpg-clm80phfb9qs739926s0-a/test_db_1bsx
    }

try:
    # Establish a connection
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()

    # Create the feedback table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            customer VARCHAR(100) NOT NULL,
            dealer VARCHAR(100) NOT NULL,
            rating INTEGER NOT NULL,
            comments TEXT
        )
    ''')
    connection.commit()

except psycopg2.Error as e:
    print("Error connecting to the database:", e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        customer = request.form['customer']
        dealer = request.form['dealer']
        rating = request.form['rating']
        comments = request.form['comments']

        if customer == '' or dealer == '':
            return render_template('index.html', message='Please enter required fields')

        try:
            # Check if the customer has already submitted feedback
            cursor.execute("SELECT id FROM feedback WHERE customer = %s", (customer,))
            existing_feedback = cursor.fetchone()

            if existing_feedback:
                return render_template('index.html', message='You already submitted your feedback')
            
            # Execute an SQL statement to insert data into the feedback table
            sql = "INSERT INTO feedback (customer, dealer, rating, comments) VALUES (%s, %s, %s, %s)"
            data = (customer, dealer, rating, comments)
            cursor.execute(sql, data)

            # Commit the transaction
            connection.commit()
            send_mail(customer,dealer,rating,comments)

            return render_template('success.html')

        except psycopg2.Error as e:
            print("Error inserting data into the database:", e)
            return render_template('index.html', message='Error submitting feedback')

if __name__ == '__main__':
    app.run()
