from flask import Flask, render_template, request, redirect
from config import get_connection

app = Flask(__name__)

# ---------------- HOME ---------------- #

@app.route("/")
def index():

    search = request.args.get("search", "")

    conn = get_connection()
    cursor = conn.cursor()

    # Dashboard Counts
    cursor.execute("SELECT COUNT(*) AS total FROM books")
    total_books = cursor.fetchone()["total"]

    cursor.execute("SELECT SUM(available) AS available FROM books")
    available_books = cursor.fetchone()["available"] or 0

    cursor.execute("""
        SELECT COUNT(*) AS issued
        FROM issued_books
        WHERE status='Issued'
    """)
    issued_books = cursor.fetchone()["issued"]

    cursor.execute("SELECT COUNT(*) AS students FROM students")
    total_students = cursor.fetchone()["students"]

    # Search
    if search:

        cursor.execute("""
            SELECT *
            FROM books
            WHERE title LIKE %s
               OR author LIKE %s
               OR category LIKE %s
               OR isbn LIKE %s
        """, (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        ))

    else:

        cursor.execute("SELECT * FROM books")

    books = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "index.html",
        books=books,
        search=search,
        total_books=total_books,
        available_books=available_books,
        issued_books=issued_books,
        total_students=total_students
    )
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

# ---------------- EDIT BOOK ---------------- #

# ---------------- EDIT BOOK ---------------- #

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_book(id):

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        title = request.form["title"]
        author = request.form["author"]
        category = request.form["category"]
        isbn = request.form["isbn"]
        new_quantity = int(request.form["quantity"])

        # Existing quantity and available
        cursor.execute(
            "SELECT quantity, available FROM books WHERE id=%s",
            (id,)
        )

        old = cursor.fetchone()

        old_quantity = old["quantity"]
        old_available = old["available"]

        difference = new_quantity - old_quantity
        new_available = old_available + difference

        if new_available < 0:
            new_available = 0

        cursor.execute("""
            UPDATE books
            SET
                title=%s,
                author=%s,
                category=%s,
                isbn=%s,
                quantity=%s,
                available=%s
            WHERE id=%s
        """, (
            title,
            author,
            category,
            isbn,
            new_quantity,
            new_available,
            id
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/")

    # GET Request
    cursor.execute("SELECT * FROM books WHERE id=%s", (id,))
    book = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "edit_book.html",
        book=book
    )
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
# ---------------- DELETE BOOK ---------------- #

@app.route("/delete/<int:id>")
def delete_book(id):

    conn = get_connection()
    cursor = conn.cursor()

    # Check if book is currently issued
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM issued_books
        WHERE book_id=%s
        AND status='Issued'
    """, (id,))

    issued = cursor.fetchone()["total"]

    if issued > 0:
        cursor.close()
        conn.close()
        return "❌ Book cannot be deleted because it is currently issued."

    cursor.execute(
        "DELETE FROM books WHERE id=%s",
        (id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/")
# ---------------- STUDENTS ---------------- #

@app.route("/students")
def students():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM students
    ORDER BY id
    """)

    students = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "students.html",
        students=students
    )

# ---------------- ADD STUDENT ---------------- #

@app.route("/add-student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        department = request.form["department"]
        campus = request.form["campus"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO students
            (name, email, phone, department, campus)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            name,
            email,
            phone,
            department,
            campus
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/students")

    return render_template("add_student.html")
    # ---------------- EDIT STUDENT ---------------- #

@app.route("/edit-student/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        department = request.form["department"]
        campus = request.form["campus"]

        cursor.execute("""
            UPDATE students
            SET
                name=%s,
                email=%s,
                phone=%s,
                department=%s,
                campus=%s
            WHERE id=%s
        """, (
            name,
            email,
            phone,
            department,
            campus,
            id
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/students")

    cursor.execute(
        "SELECT * FROM students WHERE id=%s",
        (id,)
    )

    student = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "edit_student.html",
        student=student
    )
# ---------------- DELETE STUDENT ---------------- #

@app.route("/delete-student/<int:id>")
def delete_student(id):

    conn = get_connection()
    cursor = conn.cursor()

    # Check if student has any issued books
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM issued_books
        WHERE student_id=%s
        AND status='Issued'
    """, (id,))

    issued = cursor.fetchone()["total"]

    if issued > 0:
        cursor.close()
        conn.close()
        return "❌ Cannot delete student. Student has issued books."

    cursor.execute(
        "DELETE FROM students WHERE id=%s",
        (id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/students")
    
# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    app.run(debug=True)