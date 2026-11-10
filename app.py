
import sqlite3
from datetime import date
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)
DB = "expenses.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Expense Tracker</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f3f6fb;
            color: #172033;
        }

        header {
            background: linear-gradient(135deg, #173b75, #2563eb);
            color: white;
            padding: 30px 20px;
        }

        .header-inner, main {
            max-width: 1000px;
            margin: auto;
        }

        header h1 {
            margin: 0 0 8px;
            font-size: 30px;
        }

        header p {
            margin: 0;
            color: #dbeafe;
        }

        main {
            padding: 25px 16px 45px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 18px;
        }

        .card {
            background: white;
            padding: 22px;
            margin-bottom: 20px;
            border-radius: 16px;
            box-shadow: 0 5px 20px rgba(25, 45, 80, 0.06);
        }

        .label {
            color: #64748b;
            font-size: 14px;
            margin-bottom: 12px;
        }

        .total {
            font-size: 32px;
            font-weight: bold;
            color: #1d4ed8;
            overflow-wrap: anywhere;
        }

        h2 {
            font-size: 20px;
            margin-top: 0;
        }

        form.expense-form {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
        }

        input, select {
            width: 100%;
            padding: 12px;
            border: 1px solid #dbe2ee;
            border-radius: 9px;
            font-size: 14px;
            background: white;
        }

        button {
            padding: 12px 16px;
            border: none;
            border-radius: 9px;
            background: #2563eb;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }

        button:hover {
            background: #1d4ed8;
        }

        .summary-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .summary-list li {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            padding: 13px 0;
            border-bottom: 1px solid #edf0f5;
        }

        .summary-list li:last-child {
            border-bottom: none;
        }

        .table-wrap {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 600px;
        }

        th, td {
            text-align: left;
            padding: 14px 10px;
            border-bottom: 1px solid #edf0f5;
        }

        th {
            color: #64748b;
            font-size: 13px;
        }

        .category {
            display: inline-block;
            padding: 5px 10px;
            background: #eff6ff;
            color: #1d4ed8;
            border-radius: 20px;
            font-size: 12px;
        }

        .delete {
            padding: 8px 12px;
            background: #fee2e2;
            color: #b91c1c;
        }

        .delete:hover {
            background: #fecaca;
        }

        .empty {
            color: #64748b;
            padding: 15px 0;
        }

        footer {
            text-align: center;
            color: #64748b;
            font-size: 13px;
            padding: 15px;
        }

        @media (max-width: 500px) {
            header h1 {
                font-size: 25px;
            }

            .total {
                font-size: 27px;
            }
        }
    </style>
</head>

<body>
    <header>
        <div class="header-inner">
            <h1>💰 Expense Tracker</h1>
            <p>Track your spending. Manage your money smarter.</p>
        </div>
    </header>

    <main>
        <div class="grid">
            <div class="card">
                <div class="label">TOTAL EXPENSES</div>
                <div class="total">₹ {{ "%.2f"|format(total) }}</div>
            </div>

            <div class="card">
                <div class="label">TOTAL TRANSACTIONS</div>
                <div class="total">{{ expenses|length }}</div>
            </div>
        </div>

        <div class="card">
            <h2>➕ Add an Expense</h2>

            <form class="expense-form" method="POST" action="/add">
                <input name="title" placeholder="Expense name" required
                       maxlength="100">

                <input name="amount" type="number" min="0.01"
                       step="0.01" placeholder="Amount (₹)" required>

                <select name="category" required>
                    <option value="Food">Food</option>
                    <option value="Travel">Travel</option>
                    <option value="Bills">Bills</option>
                    <option value="Shopping">Shopping</option>
                    <option value="Education">Education</option>
                    <option value="Health">Health</option>
                    <option value="Other">Other</option>
                </select>

                <input name="date" type="date" value="{{ today }}" required>

                <button type="submit">Add Expense</button>
            </form>
        </div>

        <div class="card">
            <h2>📊 Category Summary</h2>

            <ul class="summary-list">
                {% for c in categories %}
                <li>
                    <span>{{ c.category }}</span>
                    <strong>₹ {{ "%.2f"|format(c.total) }}</strong>
                </li>
                {% else %}
                <li class="empty">No expenses recorded yet.</li>
                {% endfor %}
            </ul>
        </div>

        <div class="card">
            <h2>🧾 Expense History</h2>

            {% if expenses %}
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Expense</th>
                            <th>Category</th>
                            <th>Amount</th>
                            <th>Action</th>
                        </tr>
                    </thead>

                    <tbody>
                        {% for e in expenses %}
                        <tr>
                            <td>{{ e.date }}</td>
                            <td>{{ e.title }}</td>
                            <td><span class="category">{{ e.category }}</span></td>
                            <td>₹ {{ "%.2f"|format(e.amount) }}</td>
                            <td>
                                <form method="POST"
                                      action="/delete/{{ e.id }}"
                                      onsubmit="return confirm('Delete this expense?');">
                                    <button class="delete" type="submit">
                                        Delete
                                    </button>
                                </form>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <p class="empty">No expenses yet. Add your first expense above.</p>
            {% endif %}
        </div>
    </main>

    <footer>Expense Tracker · Built with Python, Flask and SQLite</footer>
</body>
</html>
"""


@app.route("/")
def home():
    conn = get_db()

    expenses = conn.execute(
        "SELECT * FROM expenses ORDER BY date DESC, id DESC"
    ).fetchall()

    total = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses"
    ).fetchone()[0]

    categories = conn.execute("""
        SELECT category, SUM(amount) AS total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
    """).fetchall()

    conn.close()

    return render_template_string(
        PAGE,
        expenses=expenses,
        total=total,
        categories=categories,
        today=date.today().isoformat()
    )


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "Other")
    expense_date = request.form.get("date", "")

    try:
        amount = float(request.form.get("amount", "0"))
    except ValueError:
        return "Invalid amount. Please go back and try again.", 400

    if not title or amount <= 0 or not expense_date:
        return "Please enter valid expense details.", 400

    allowed_categories = {
        "Food", "Travel", "Bills", "Shopping",
        "Education", "Health", "Other"
    }

    if category not in allowed_categories:
        category = "Other"

    conn = get_db()
    conn.execute("""
        INSERT INTO expenses (title, amount, category, date)
        VALUES (?, ?, ?, ?)
    """, (title, amount, category, expense_date))
    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete(expense_id):
    conn = get_db()
    conn.execute(
        "DELETE FROM expenses WHERE id = ?", (expense_id,)
    )
    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
