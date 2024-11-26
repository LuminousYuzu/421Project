from flask import Flask, request, render_template, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# Database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='student_forum'
    )
    return conn


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']

        if float(age) < 0:
            flash('Age cannot be negative.', 'danger')
            return redirect(url_for('add_student'))

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Insert into Student without PostID
            cursor.execute('INSERT INTO Student (Name, Age, Gender) VALUES (%s, %s, %s)', (name, age, gender))

            # Commit transaction
            conn.commit()
            flash('Student added successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('index'))
    return render_template('add_student.html')

@app.route('/delete_student', methods=['GET', 'POST'])
def delete_student():
    if request.method == 'POST':
        pid = request.form['pid']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM Student WHERE PID = %s', (pid,))
            conn.commit()
            flash('Student deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('index'))
    return render_template('delete_student.html')

@app.route('/update_student', methods=['GET', 'POST'])
def update_student():
    if request.method == 'POST':
        pid = request.form['pid']
        name = request.form['name']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE Student SET Name = %s WHERE PID = %s', (name, pid))
            conn.commit()
            flash('Student updated successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('index'))
    return render_template('update_student.html')

@app.route('/view_students')
def view_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Student')
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('view_students.html', students=students)

@app.route('/get_posts_by_student', methods=['GET', 'POST'])
def get_posts_by_student():
    if request.method == 'POST':
        pid = request.form['pid']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc('GetPostsByStudent', [pid])
            posts = []
            for result in cursor.stored_results():
                posts.extend(result.fetchall())
            return render_template('view_posts.html', posts=posts)
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('index'))
        finally:
            cursor.close()
            conn.close()
    return render_template('get_posts_by_student.html')

if __name__ == '__main__':
    app.run(debug=True)
