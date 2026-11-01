from flask import Flask, render_template, request, redirect
from config import get_connection

app = Flask(__name__)

# ---------------- HOME ---------------- #

@app.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("index.html", books=books)


# ---------------- ADD BOOK ---------------- #

@app.route("/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        category = request.form["category"]
        isbn = request.form["isbn"]
        quantity = int(request.form["quantity"])

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO books
            (title, author, category, isbn, quantity, available)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, author, category, isbn, quantity, quantity))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/")

    return render_template("add_book.html")


# ---------------- ISSUE BOOK PAGE ---------------- #

@app.route("/issue", methods=["GET", "POST"])
def issue_book():
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        student_id = request.form["student_id"]
        book_id = request.form["book_id"]
        issue_date = request.form["issue_date"]
        due_date = request.form["due_date"]

        # Issue book entry
        cursor.execute("""
            INSERT INTO issued_books
            (student_id, book_id, issue_date, due_date, status)
            VALUES (%s, %s, %s, %s, 'Issued')
        """, (student_id, book_id, issue_date, due_date))

        # Reduce available books
        cursor.execute("""
            UPDATE books
            SET available = available - 1
            WHERE id = %s
        """, (book_id,))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/")

    # GET request
    cursor.execute("SELECT id, name FROM students")
    students = cursor.fetchall()

    cursor.execute("SELECT id, title FROM books WHERE available > 0")
    books = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "issue_book.html",
        students=students,
        books=books
    )
# ---------------- RETURN BOOK ---------------- #

@app.route("/return")
def return_list():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            issued_books.id,
            students.name,
            books.title,
            issued_books.issue_date,
            issued_books.due_date
        FROM issued_books
        JOIN students ON students.id = issued_books.student_id
        JOIN books ON books.id = issued_books.book_id
        WHERE issued_books.status='Issued'
    """)

    issued = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("return_book.html", issued=issued)


@app.route("/return/<int:id>")
def return_book(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT book_id FROM issued_books WHERE id=%s",
        (id,)
    )

    record = cursor.fetchone()

    if record:

        cursor.execute("""
            UPDATE issued_books
            SET
                status='Returned',
                return_date=CURDATE()
            WHERE id=%s
        """, (id,))

        cursor.execute("""
            UPDATE books
            SET available=available+1
            WHERE id=%s
        """, (record["book_id"],))

        conn.commit()

    cursor.close()
    conn.close()

    return redirect("/return")

# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    app.run(debug=True)