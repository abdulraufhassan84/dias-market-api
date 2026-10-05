import os
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)

DB_FILE = "dias_database_v3.db"


def get_db_connection():
  conn = sqlite3.connect(DB_FILE)
  conn.row_factory = sqlite3.Row  # Ili data zisomeke kwa mfumo wa Dictionary/JSON
  return conn


# 1. API YA KUPATA BIDHAA ZOTE SOKONI (Kutumiwa na Android App & Desktop)
@app.route("/api/products", methods=["GET"])
def get_products():
  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, jina_la_bidhaa, mjasiriamali, kundi, bei, idadi, picha_path,"
        " status FROM products ORDER BY id DESC"
    )
    rows = cursor.fetchall()
    conn.close()

    products_list = [dict(row) for row in rows]
    return jsonify({"success": True, "data": products_list}), 200
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


# 2. API YA KUSAJILI MTEJA MPYA KUTOKA MOBILE APP
@app.route("/api/register_client", methods=["POST"])
def register_client():
  data = request.get_json()
  if not data:
    return jsonify({"success": False, "error": "Hakuna data iliyotumwa"}), 400

  client_id = data.get("client_id")
  jina = data.get("jina_la_mteja")
  simu = data.get("namba_ya_simu")
  eneo = data.get("eneo", "Mjini Magharibi")
  tarehe = data.get("tarehe_ya_usajili")

  if not client_id or not jina or not simu:
    return jsonify(
        {"success": False, "error": "Jaza nafasi zote zinazotakiwa"}
    ), 400

  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
            INSERT INTO registered_clients (client_id, jina_la_mteja, namba_ya_simu, eneo, tarehe_ya_usajili)
            VALUES (?, ?, ?, ?, ?)
        """,
        (client_id, jina, simu, eneo, tarehe),
    )
    conn.commit()
    conn.close()
    return jsonify(
        {
            "success": True,
            "message": "Mteja amesajiliwa mafanikio na alert imetumwa desktop!",
        }
    ), 201
  except sqlite3.IntegrityError:
    return (
        jsonify({"success": False, "error": "Client ID imeshawahi kusajiliwa"}),
        400,
    )
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


# 3. API YA KUTUMA ODA MPYA KUTOKA MOBILE APP
@app.route("/api/orders", methods=["POST"])
def create_order():
  data = request.get_json()
  if not data:
    return jsonify({"success": False, "error": "Hakuna data iliyotumwa"}), 400

  order_id = data.get("order_id")
  mteja = data.get("mteja")
  mjasiriamali = data.get("mjasiriamali")
  bidhaa = data.get("bidhaa")
  kiasi = data.get("kiasi")
  eneo = data.get("eneo")
  tarehe_muda = data.get("tarehe_muda")

  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
            INSERT INTO orders (order_id, mteja, mjasiriamali, bidhaa, kiasi, eneo, status, tarehe_muda)
            VALUES (?, ?, ?, ?, ?, ?, 'Pending', ?)
        """,
        (order_id, mteja, mjasiriamali, bidhaa, kiasi, eneo, tarehe_muda),
    )
    conn.commit()
    conn.close()
    return jsonify(
        {
            "success": True,
            "message": "Oda imepokelewa na kupelekwa desktop kwa mafanikio!",
        }
    ), 201
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)
