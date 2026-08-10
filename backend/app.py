from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_simple_captcha import CAPTCHA
import pymysql
import jwt
import datetime
from datetime import timezone

app = Flask(__name__)
app.secret_key = "your-secret-key"
CORS(app, supports_credentials=True)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "test",
    "charset": "utf8mb4",
}
try:
    conn = pymysql.connect(**DB_CONFIG)
    print("✅ 数据库连接成功！")
    conn.close()
except Exception as e:
    print(f"❌ 数据库连接失败：{e}")

YOUR_CONFIG = {
    "SECRET_CAPTCHA_KEY": "LONG_KEY",  # 建议设置一个复杂的字符串
    "CAPTCHA_LENGTH": 4,  # 验证码字符长度
    "EXPIRE_SECONDS": 60 * 5,  # 验证码有效期 (秒)
    "CAPTCHA_DIGITS": False,  # 是否包含数字
    "BACKGROUND_COLOR": (0, 0, 0),  # 背景颜色 (黑色)
    "TEXT_COLOR": (255, 255, 255),  # 文字颜色 (白色)
}

# 2. 初始化验证码实例 (传入config)
SIMPLE_CAPTCHA = CAPTCHA(config=YOUR_CONFIG)

# 3. 将验证码与Flask应用绑定 (使用init_app方法)
SIMPLE_CAPTCHA.init_app(app)


# 验证码生成
@app.route("/api/captcha", methods=["GET"])
def get_captcha():
    new_captcha_dict = SIMPLE_CAPTCHA.create()

    # 键名是 'img'、'text'、'hash'
    return jsonify(
        {
            "image": "data:image/jpeg;base64,"
            + new_captcha_dict["img"],  # base64 图片数据
            "key": new_captcha_dict["hash"],  # 用于校验的哈希值
        }
    )


# token验证
SECRET_KEY = "your-secret-key"


def verify_token():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    parts = auth_header.split(" ")
    if len(parts) != 2 or parts[0] != "Bearer":
        return None

    token = parts[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError as e:
        print("Token 过期:", e)
        return None
    except jwt.InvalidTokenError as e:
        print("无效 Token:", e)
        return None
    except Exception as e:
        print("其他解码错误:", e)
        return None


# 注册接口
@app.route("/api/register", methods=["GET"])
def register():
    username = request.args.get("username")
    password = request.args.get("password")

    # 1. 校验参数是否为空
    if not username or not password:
        return jsonify({"message": "用户名和密码不能为空"}), 400
    if len(password) < 6:
        return jsonify({"message": "密码长度不能小于6位"}), 400
    if len(username) < 6:
        return jsonify({"message": "用户名长度不能小于6位"}), 400
    import re

    has_number = re.search(r"[0-9]", password) is not None
    has_upper = re.search(r"[A-Z]", password) is not None
    has_lower = re.search(r"[a-z]", password) is not None
    if not has_number or not has_upper or not has_lower:
        return jsonify({"message": "密码必须包含大小写字母和数字"}), 400

    conn = None
    cursor = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 2. 先查询用户名是否已存在
        check_sql = "SELECT username FROM users WHERE username = %s"
        cursor.execute(check_sql, (username,))
        if cursor.fetchone():
            return jsonify({"message": "用户名已存在，请换一个"}), 400

        # 3. 用户名不存在，执行插入
        insert_sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(insert_sql, (username, password))
        conn.commit()

        return jsonify({"message": "注册成功"}), 200

    except Exception as e:
        # 打印详细错误到终端（便于调试）
        print("❌ 注册失败：", e)
        return jsonify({"message": f"注册失败：{str(e)}"}), 500
    finally:
        # 确保关闭连接和游标
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# 登录接口+生成token
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user_captcha = data.get("captcha", "").upper()
    captcha_key = data.get("captchaKey")

    if not username or not password:
        return jsonify({"message": "用户名和密码不能为空"}), 400

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        sql = "SELECT id, password, role FROM users WHERE username = %s"
        cursor.execute(sql, (username,))
        result = cursor.fetchone()

        if result is None:
            return jsonify({"message": "用户名不存在"}), 401
        # if not user_captcha or not captcha_key:
        #     return jsonify({"code": 401, "message": "请输入验证码"}), 401
        # if not SIMPLE_CAPTCHA.verify(user_captcha, captcha_key):
        #     return jsonify({"code": 401, "message": "验证码错误"}), 401

        user_id = result[0]
        db_password = result[1]
        role = result[2]  # 第三列是 role

        if db_password == password:
            token = jwt.encode(
                {
                    "user_id": user_id,
                    "username": username,
                    "role": role,  # 可以根据实际情况设置角色
                    "exp": datetime.datetime.now(datetime.timezone.utc)
                    + datetime.timedelta(hours=12),
                },
                "your-secret-key",  # 建议使用环境变量
                algorithm="HS256",
            )

            return (
                jsonify(
                    {
                        "code": 200,
                        "message": "登录成功",
                        "username": username,
                        "token": token,
                        "role": role,
                    }
                ),
                200,
            )
        else:
            return jsonify({"message": "密码错误"}), 401
    except Exception as e:
        return jsonify({"message": f"登录失败：{str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


# 获取学生数据接口，填充表格
@app.route("/api/students", methods=["GET"])
def get_students():
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录或登录已过期"}), 401

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    offset = (page - 1) * limit
    search = request.args.get("search", "")
    fields = request.args.getlist("fields[]")
    gender = request.args.get("gender", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    sort_field = request.args.get("sort_field", "id")
    sort_order = request.args.get("sort_order", "DESC")

    # 验证排序字段和方向
    allowed_fields = ["id", "name", "age", "score"]
    if sort_field not in allowed_fields:
        sort_field = "id"
    if sort_order.upper() not in ["ASC", "DESC"]:
        sort_order = "DESC"

    print("排序字段:", sort_field, "排序方向:", sort_order)
    print("搜索关键词:", search)
    print("收到的 fields 列表:", fields)

    conn = None
    cursor = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # 2. 构建 WHERE 条件
        where_conditions = []
        params = []

        if search and fields:
            search_fields = []
            for field in fields:
                if field == "class":
                    search_fields.append("CONCAT(c.grade, c.class)")
                else:
                    search_fields.append(f"s.{field}")

            where_conditions.append(
                "(" + " OR ".join([f"{field} LIKE %s" for field in search_fields]) + ")"
            )
            params.extend(["%" + search + "%"] * len(fields))
        if start_date and end_date:
            where_conditions.append("DATE(created_at) BETWEEN %s AND %s")
            params.extend([start_date, end_date])

        if gender != "":
            where_conditions.append("s.gender = %s")
            params.append(gender)
        where_clause = (
            " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        )

        sql_count = f"SELECT COUNT(*) FROM students s LEFT JOIN class c ON s.class_id = c.id  {where_clause}"
        cursor.execute(sql_count, params)
        total = cursor.fetchone()[0]

        sql = f"""
                SELECT s.id, s.name, s.gender, s.age, CONCAT(c.grade, c.class) AS class_name, s.score, s.created_at
                FROM students s
                LEFT JOIN class c ON s.class_id = c.id
                {where_clause}
                ORDER BY {sort_field} {sort_order}
                LIMIT %s OFFSET %s
            """
        cursor.execute(sql, params + [limit, offset])
        results = cursor.fetchall()

        students = []
        for row in results:
            students.append(
                {
                    "id": row[0],
                    "name": row[1] if row[1] else "未填写",
                    "gender": row[2] if row[2] is not None else "未填写",
                    "age": row[3] if row[3] else 0,
                    "class": row[4] if row[4] else "未填写",
                    "score": row[5] if row[5] is not None else 0,
                    "createTime": (
                        row[6].strftime("%Y-%m-%d %H:%M:%S") if row[6] else "未填写"
                    ),
                }
            )

        return (
            jsonify(
                {
                    "code": 200,
                    "data": students,
                    "total": total,
                    "page": page,
                    "limit": limit,
                }
            ),
            200,
        )

    except Exception as e:
        print("❌ 查询用户数据失败：", e)
        return jsonify({"code": 500, "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# 学生添加接口
@app.route("/api/students", methods=["POST"])
def add_student():
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录或登录已过期"}), 401
    try:
        # 1. 获取前端传来的数据
        data = request.get_json()
        name = data.get("name")
        gender = data.get("gender")
        age = data.get("age")
        class_id = data.get("class_id")
        score = data.get("score")

        # 校验姓名
        if not name or not name.strip():
            return jsonify({"code": 400, "message": "姓名不能为空"}), 400

        # 校验性别
        if gender not in [1, 0]:
            return jsonify({"code": 400, "message": "请选择性别"}), 400

        # 校验年龄
        if not age:
            return jsonify({"code": 400, "message": "年龄不能为空"}), 400
        try:
            age = int(age)
        except ValueError:
            return jsonify({"code": 400, "message": "年龄必须是数字"}), 400

        # 校验班级
        if not class_id:
            return jsonify({"code": 400, "message": "请选择班级"}), 400

        # 校验分数
        if score is None or score == "":
            return jsonify({"code": 400, "message": "分数不能为空"}), 400
        try:
            score = float(score)
        except ValueError:
            return jsonify({"code": 400, "message": "分数必须是数字"}), 400

        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        sql = "INSERT INTO students (name, age, score, class_id, gender) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (name, age, score, class_id, gender))
        conn.commit()

        # 5. 关闭连接
        cursor.close()
        conn.close()

        # 6. 返回成功
        return jsonify({"code": 200, "message": "添加成功"}), 200

    except Exception as e:
        print("❌ 获取前端数据失败：", e)
        return jsonify({"code": 500, "message": str(e)}), 500


# 学生查询接口
@app.route("/api/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录或登录已过期"}), 401
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        sql = """
            SELECT s.id, s.name, s.gender, s.age, c.class AS class_name, s.score, s.class_id
            FROM students s
            LEFT JOIN class c ON s.class_id = c.id
            WHERE s.id = %s
        """
        cursor.execute(sql, (student_id,))
        result = cursor.fetchone()

        if result is None:  # 如果没有找到对应的学生
            return jsonify({"message": "学生不存在"}), 404

        student = {
            "id": result[0],
            "name": result[1] if result[1] else "未填写",
            "gender": result[2] if result[2] is not None else "未填写",
            "age": result[3] if result[3] else 0,
            "class": result[4] if result[4] else "未填写",
            "score": result[5] if result[5] is not None else 0,
            "class_id": result[6] if result[6] is not None else "",
        }

        cursor.close()
        conn.close()

        return jsonify({"code": 200, "data": student}), 200

    except Exception as e:
        print("❌ 查询用户数据失败：", e)
        return jsonify({"code": 500, "message": str(e)}), 500


# 班级选择字段查询
@app.route("/api/classes/options", methods=["GET"])
def get_class_options():
    print("get_class_options 被调用了")
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录"}), 401

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, grade, class FROM class ORDER BY FIELD(grade, '高一', '高二', '高三'), class"
    )
    results = cursor.fetchall()

    data = []
    for row in results:
        data.append({"id": row[0], "grade": row[1], "class": row[2]})

    return jsonify({"code": 200, "data": data}), 200


# 学生修改接口
@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录或登录已过期"}), 401
    try:
        data = request.get_json()
        name = data.get("name")
        gender = data.get("gender")
        age = data.get("age")
        class_id = data.get("class_id")
        score = data.get("score")
        # 校验姓名
        if not name or not name.strip():
            return jsonify({"code": 400, "message": "姓名不能为空"}), 400

        # 校验年龄
        if not age:
            return jsonify({"code": 400, "message": "年龄不能为空"}), 400
        try:
            age = int(age)
        except ValueError:
            return jsonify({"code": 400, "message": "年龄必须是数字"}), 400

        # 校验班级
        if not class_id:  # 前端直接传的是数字，直接判断是否为None或空即可
            return jsonify({"code": 400, "message": "请选择班级"}), 400

        # 校验分数
        if score is None or score == "":
            return jsonify({"code": 400, "message": "分数不能为空"}), 400
        try:
            score = float(score)
        except ValueError:
            return jsonify({"code": 400, "message": "分数必须是数字"}), 400

        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        sql = "UPDATE students SET name = %s, age = %s, class_id = %s, score = %s, gender = %s WHERE id = %s"
        cursor.execute(sql, (name, age, class_id, score, gender, student_id))
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({"code": 200, "message": "更新成功"}), 200

    except Exception as e:
        print("❌ 更新用户数据失败：", e)
        return jsonify({"code": 500, "message": str(e)}), 500


# 学生删除接口
@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录或登录已过期"}), 401
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        sql = "DELETE FROM students WHERE id = %s"
        cursor.execute(sql, (student_id,))
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({"code": 200, "message": "删除成功"}), 200

    except Exception as e:
        print("❌ 删除用户数据失败：", e)
        return jsonify({"code": 500, "message": str(e)}), 500


# 班级管理表格填充接口
@app.route("/api/classes", methods=["GET"])
def get_classes():
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录"}), 401

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    search = request.args.get("search", "").strip()
    offset = (page - 1) * limit

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # 构造搜索条件
        if search:
            # 搜索年级或班级编号（class 是整数，需要转换）
            # 如果搜索词是数字，按班级编号搜索；否则按年级搜索
            if search.isdigit():
                where_clause = "WHERE c.class = %s"
                params = (int(search),)
            else:
                where_clause = "WHERE c.grade LIKE %s"
                params = ("%" + search + "%",)

            # 总记录数
            sql_count = f"""
                SELECT COUNT(*) FROM class c
                {where_clause}
            """
            cursor.execute(sql_count, params)
            total = cursor.fetchone()[0]

            # 分页查询
            sql = f"""
                SELECT c.id, c.grade, c.class, COUNT(s.id) AS student_count, 
                       c.is_key_class, ROUND(AVG(s.score), 2) AS avg_score
                FROM class c
                LEFT JOIN students s ON s.class_id = c.id
                {where_clause}
                GROUP BY c.id
                ORDER BY FIELD(c.grade, '高一', '高二', '高三'), c.class
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, params + (limit, offset))
        else:
            # 无搜索条件
            cursor.execute("SELECT COUNT(*) FROM class")
            total = cursor.fetchone()[0]

            sql = """
                SELECT c.id, c.grade, c.class, COUNT(s.id) AS student_count, 
                       c.is_key_class, ROUND(AVG(s.score), 2) AS avg_score
                FROM class c
                LEFT JOIN students s ON s.class_id = c.id
                GROUP BY c.id
                ORDER BY FIELD(c.grade, '高一', '高二', '高三'), c.class
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (limit, offset))

        results = cursor.fetchall()

        data = []
        for row in results:
            data.append(
                {
                    "id": row[0],
                    "grade": row[1],
                    "class": row[2],  # 班级编号（数字）
                    "student_count": row[3] if row[3] else 0,
                    "is_key_class": row[4],
                    "avg_score": row[5] if row[5] is not None else 0,
                }
            )

        return (
            jsonify(
                {
                    "code": 200,
                    "data": data,
                    "total": total,
                    "page": page,
                    "limit": limit,
                }
            ),
            200,
        )

    except Exception as e:
        print("❌ 查询班级数据失败：", e)
        return jsonify({"code": 500, "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# 班级添加接口
@app.route("/api/classes", methods=["POST"])
def add_class():
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录或登录已过期"}), 401

    data = request.get_json()
    grade = data.get("grade")
    class_number = data.get("class")
    is_key_class = data.get("is_key_class", 0)

    if not grade:
        return jsonify({"code": 400, "message": "年级不能为空"}), 400

    if not class_number:
        return jsonify({"code": 400, "message": "班级编号不能为空"}), 400

    try:
        class_number = int(class_number)
        if class_number <= 0:
            raise ValueError
    except ValueError:
        return jsonify({"code": 400, "message": "班级编号必须是正整数"}), 400

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # 检查同年级下是否已存在相同编号
        check_sql = "SELECT id FROM class WHERE grade = %s AND class = %s"
        cursor.execute(check_sql, (grade, class_number))
        existing = cursor.fetchone()

        if existing:
            return (
                jsonify({"code": 400, "message": f"{grade}已存在{class_number}班"}),
                400,
            )

        sql = "INSERT INTO class (grade, class, is_key_class) VALUES (%s, %s, %s)"
        cursor.execute(sql, (grade, class_number, is_key_class))
        conn.commit()

        return jsonify({"code": 200, "message": "添加成功"}), 200

    except Exception as e:
        print("❌ 添加班级失败：", e)
        return jsonify({"code": 500, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# 班级编辑自动填充
@app.route("/api/classes/<int:class_id>", methods=["GET"])
def get_class(class_id):
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录或登录已过期"}), 401

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        sql = "SELECT id, grade, class, is_key_class FROM class WHERE id = %s"
        cursor.execute(sql, (class_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"code": 404, "message": "班级不存在"}), 404

        data = {
            "id": result[0],
            "grade": result[1],
            "class_number": result[2],
            "is_key_class": result[3],
        }

        return jsonify({"code": 200, "data": data}), 200

    except Exception as e:
        print("❌ 获取班级信息失败：", e)
        return jsonify({"code": 500, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# 班级修改
@app.route("/api/classes/<int:class_id>", methods=["PUT"])
def update_class(class_id):
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录或登录已过期"}), 401

    data = request.get_json()
    grade = data.get("grade")
    class_number = data.get("class_number")
    is_key_class = data.get("is_key_class", 0)

    if not grade:
        return jsonify({"code": 400, "message": "年级不能为空"}), 400

    if not class_number:
        return jsonify({"code": 400, "message": "班级编号不能为空"}), 400

    try:
        class_number = int(class_number)
        if class_number <= 0:
            raise ValueError
    except ValueError:
        return jsonify({"code": 400, "message": "班级编号必须是正整数"}), 400

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # 检查同年级下是否已存在相同编号
        check_sql = "SELECT id FROM class WHERE grade = %s AND class = %s AND id != %s"
        cursor.execute(check_sql, (grade, class_number, class_id))
        existing = cursor.fetchone()

        if existing:
            return (
                jsonify({"code": 400, "message": f"{grade}已存在{class_number}班"}),
                400,
            )

        sql = "UPDATE class SET grade = %s, class = %s, is_key_class = %s WHERE id = %s"
        cursor.execute(sql, (grade, class_number, is_key_class, class_id))
        conn.commit()

        return jsonify({"code": 200, "message": "修改成功"}), 200

    except Exception as e:
        print("❌ 修改班级失败：", e)
        return jsonify({"code": 500, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# 班级删除
@app.route("/api/classes/<int:class_id>", methods=["DELETE"])
def delete_class(class_id):
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录或登录已过期"}), 401

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        sql = "DELETE FROM class WHERE id = %s"
        cursor.execute(sql, (class_id,))
        conn.commit()

        return jsonify({"code": 200, "message": "删除成功"}), 200

    except Exception as e:
        print("❌ 删除班级失败：", e)
        return jsonify({"code": 500, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# 科目管理表格填充接口
@app.route("/api/subjects", methods=["GET"])
def get_subjects():
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录"}), 401

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    offset = (page - 1) * limit
    search = request.args.get("search", "")  # 获取搜索关键词

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # 构建搜索条件
        where_clause = ""
        params = []
        if search:
            where_clause = "WHERE s.subject LIKE %s"
            params.append("%" + search + "%")

        # 总记录数
        count_sql = f"SELECT COUNT(*) FROM subjects s {where_clause}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]

        # 分页查询
        sql = f"""
            SELECT s.id, s.subject, s.full_score, s.is_class_special, s.created_at,
                   GROUP_CONCAT(CONCAT(c.grade, c.class, '班') SEPARATOR '、') AS class_names
            FROM subjects s
            LEFT JOIN subject_classes sc ON s.id = sc.subjects_id
            LEFT JOIN class c ON sc.class_id = c.id
            {where_clause}
            GROUP BY s.id
            ORDER BY s.id DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(sql, params + [limit, offset])
        results = cursor.fetchall()

        data = []
        for row in results:
            data.append(
                {
                    "id": row[0],
                    "subject": row[1],
                    "full_score": row[2],
                    "is_class_special": row[3],
                    "created_at": row[4],
                    "class_names": row[5] if row[5] else "全校",
                }
            )

        return (
            jsonify(
                {
                    "code": 200,
                    "data": data,
                    "total": total,
                    "page": page,
                    "limit": limit,
                }
            ),
            200,
        )

    except Exception as e:
        print("❌ 查询科目列表失败：", e)
        return jsonify({"code": 500, "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# 科目添加接口
@app.route("/api/subjects", methods=["POST"])
def add_subject():
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录"}), 401

    data = request.get_json()
    print("收到的 class_ids:", data.get("class_ids"))
    subject = data.get("name")
    full_score = data.get("full_score")
    is_class_special = data.get("is_special", 0)
    class_ids = data.get("class_ids", [])  # 多个班级 ID 数组

    if not subject:
        return jsonify({"code": 400, "message": "科目不能为空"}), 400

    if full_score is None or full_score == "":
        return jsonify({"code": 400, "message": "满分不能为空"}), 400

    try:
        full_score = float(full_score)
        if full_score <= 0:
            return jsonify({"code": 400, "message": "满分必须大于0"}), 400
    except ValueError:
        return jsonify({"code": 400, "message": "满分必须是数字"}), 400

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # 1. 插入科目
        sql = """
            INSERT INTO subjects (subject, full_score, is_class_special)
            VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (subject, full_score, is_class_special))
        subjects_id = cursor.lastrowid  # 获取新插入的科目 ID

        # 2. 插入关联班级
        if class_ids:
            for class_id in class_ids:
                if class_id:  # 过滤空值
                    sql = "INSERT INTO subject_classes (subjects_id, class_id) VALUES (%s, %s)"
                    cursor.execute(sql, (subjects_id, class_id))

        conn.commit()
        return jsonify({"code": 200, "message": "添加成功"}), 200

    except Exception as e:
        print("❌ 添加科目失败：", e)
        conn.rollback()
        return jsonify({"code": 500, "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# 科目编辑自动填充
@app.route("/api/subjects/<int:subject_id>", methods=["GET"])
def get_subject_for_edit(subject_id):
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录"}), 401

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # 查询科目信息
        sql = "SELECT * FROM subjects WHERE id = %s"
        cursor.execute(sql, (subject_id,))
        subject = cursor.fetchone()

        if not subject:
            return jsonify({"code": 404, "message": "科目不存在"}), 404

        # 查询关联的班级 ID
        sql = "SELECT class_id FROM subject_classes WHERE subjects_id = %s"
        cursor.execute(sql, (subject_id,))
        class_ids = [row[0] for row in cursor.fetchall()]

        return (
            jsonify(
                {
                    "code": 200,
                    "data": {
                        "id": subject[0],
                        "subject": subject[1],
                        "full_score": subject[2],
                        "is_class_special": subject[3],
                        "class_ids": class_ids,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        print("❌ 查询科目信息失败：", e)
        return jsonify({"code": 500, "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# 科目修改接口
@app.route("/api/subjects/<int:subject_id>", methods=["PUT"])
def update_subject(subject_id):
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录"}), 401

    data = request.get_json()
    subject = data.get("subject")
    full_score = data.get("full_score")
    is_class_special = data.get("is_special", 0)
    class_ids = data.get("class_ids", [])

    # 校验
    if not subject or not subject.strip():
        return jsonify({"code": 400, "message": "科目名称不能为空"}), 400

    if full_score is None or full_score == "":
        return jsonify({"code": 400, "message": "满分不能为空"}), 400

    try:
        full_score = float(full_score)
        if full_score <= 0:
            return jsonify({"code": 400, "message": "满分必须大于0"}), 400
    except ValueError:
        return jsonify({"code": 400, "message": "满分必须是数字"}), 400

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # 1. 更新科目主表
        sql = """
            UPDATE subjects
            SET subject = %s, full_score = %s, is_class_special = %s
            WHERE id = %s
        """
        cursor.execute(sql, (subject.strip(), full_score, is_class_special, subject_id))

        # 2. 更新中间表（先删后增）
        # 删除旧关联
        cursor.execute(
            "DELETE FROM subject_classes WHERE subjects_id = %s", (subject_id,)
        )

        # 插入新关联
        for class_id in class_ids:
            if class_id:  # 过滤空值
                cursor.execute(
                    "INSERT INTO subject_classes (subjects_id, class_id) VALUES (%s, %s)",
                    (subject_id, class_id),
                )

        conn.commit()
        return jsonify({"code": 200, "message": "更新成功"}), 200

    except Exception as e:
        print("❌ 更新科目失败：", e)
        conn.rollback()
        return jsonify({"code": 500, "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# 科目删除接口
@app.route("/api/subjects/<int:subject_id>", methods=["DELETE"])
def delete_subject(subject_id):
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录"}), 401

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # 1. 删除科目与班级的关联
        cursor.execute(
            "DELETE FROM subject_classes WHERE subjects_id = %s", (subject_id,)
        )

        # 2. 删除学生与该科目的关联（如果有选课记录）
        cursor.execute(
            "DELETE FROM student_subjects WHERE subject_id = %s", (subject_id,)
        )

        # 3. 删除科目本身
        cursor.execute("DELETE FROM subjects WHERE id = %s", (subject_id,))

        conn.commit()
        return jsonify({"code": 200, "message": "删除成功"}), 200

    except Exception as e:
        print("❌ 删除科目失败：", e)
        conn.rollback()
        return jsonify({"code": 500, "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# 管理员管理表填充接口
@app.route("/api/users", methods=["GET"])
def get_admins():
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录或登录已过期"}), 401

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    offset = (page - 1) * limit
    search = request.args.get("search", "").strip()

    conn = None
    cursor = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 构造查询条件
        if search:
            sql_count = "SELECT COUNT(*) FROM users WHERE username LIKE %s"
            cursor.execute(sql_count, ("%" + search + "%",))
            total = cursor.fetchone()[0]

            sql = """
                SELECT id, username, role, created_at
                FROM users
                WHERE username LIKE %s
                ORDER BY id DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, ("%" + search + "%", limit, offset))
        else:
            sql_count = "SELECT COUNT(*) FROM users"
            cursor.execute(sql_count)
            total = cursor.fetchone()[0]

            sql = """
                SELECT id, username, role, created_at
                FROM users
                ORDER BY id DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (limit, offset))

        results = cursor.fetchall()

        data = []
        for row in results:
            data.append(
                {
                    "id": row[0],
                    "username": row[1],
                    "role": row[2],  # 新增 role 字段
                    "created_at": (
                        row[3].strftime("%Y-%m-%d %H:%M:%S") if row[3] else None
                    ),
                }
            )

        return (
            jsonify(
                {
                    "code": 200,
                    "data": data,
                    "total": total,
                    "page": page,
                    "limit": limit,
                }
            ),
            200,
        )

    except Exception as e:
        print("❌ 查询管理员列表失败：", e)
        return jsonify({"code": 500, "message": "服务器错误"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# 管理员管理修改身份
@app.route("/api/users/<int:user_id>/role", methods=["PUT"])
def update_user_role(user_id):
    # 验证 Token
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录或登录已过期"}), 401

    # 权限检查：只有管理员可以修改他人角色
    if payload.get("role") != "admin":
        return jsonify({"code": 403, "message": "权限不足"}), 403

    data = request.get_json()
    new_role = data.get("role")

    # 校验角色是否合法
    valid_roles = ["user", "teacher", "admin"]
    if new_role not in valid_roles:
        return (
            jsonify(
                {
                    "code": 400,
                    "message": "无效的角色，允许的角色为：user, teacher, admin",
                }
            ),
            400,
        )

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # 检查用户是否存在
        cursor.execute("SELECT id, role FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"code": 404, "message": "用户不存在"}), 404

        # 不能修改自己的角色（防止管理员把自己降级）
        current_user_id = payload.get("user_id")
        if user_id == current_user_id:
            return jsonify({"code": 403, "message": "不能修改自己的角色"}), 403

        # 更新角色
        cursor.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
        conn.commit()

        return jsonify({"code": 200, "message": f"用户角色已更新为：{new_role}"}), 200

    except Exception as e:
        print("❌ 修改用户角色失败：", e)
        conn.rollback()
        return jsonify({"code": 500, "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# 管理员删除用户
@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录或登录已过期"}), 401

    # 只有管理员可以删除用户
    if payload.get("role") != "admin":
        return jsonify({"code": 403, "message": "权限不足"}), 403

    # 不能删除自己
    current_user_id = payload.get("user_id")
    if user_id == current_user_id:
        return jsonify({"code": 403, "message": "不能删除自己"}), 403

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # 检查用户是否存在
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            return jsonify({"code": 404, "message": "用户不存在"}), 404

        # 删除用户（如果有其他表关联，需要先清理）
        # 如果有关联表，先删除关联数据（如 student_subjects 等）
        # cursor.execute("DELETE FROM student_subjects WHERE student_id = %s", (user_id,))

        # 删除用户
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()

        return jsonify({"code": 200, "message": "用户删除成功"}), 200

    except Exception as e:
        print("❌ 删除用户失败：", e)
        conn.rollback()
        return jsonify({"code": 500, "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# 管理员重置密码
@app.route("/api/users/<int:user_id>/reset-password", methods=["PUT"])
def reset_user_password(user_id):
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录或登录已过期"}), 401

    # 只有管理员可以重置密码
    if payload.get("role") != "admin":
        return (
            jsonify({"code": 403, "message": "权限不足，只有管理员可以重置密码"}),
            403,
        )

    # 不能重置自己的密码（如果需要可以放开）
    current_user_id = payload.get("user_id")
    if user_id == current_user_id:
        return (
            jsonify({"code": 403, "message": "不能重置自己的密码，请使用修改密码功能"}),
            403,
        )

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # 检查用户是否存在
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            return jsonify({"code": 404, "message": "用户不存在"}), 404

        # 重置密码（默认密码：123456）
        default_password = "123456"
        # 如果密码加密了，需要加密后存储
        # hashed_password = hashlib.md5(default_password.encode()).hexdigest()
        # cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))

        # 如果密码是明文存储
        cursor.execute(
            "UPDATE users SET password = %s WHERE id = %s", (default_password, user_id)
        )
        conn.commit()

        return (
            jsonify(
                {
                    "code": 200,
                    "message": "密码已重置为默认密码",
                }
            ),
            200,
        )

    except Exception as e:
        print("❌ 重置密码失败：", e)
        conn.rollback()
        return jsonify({"code": 500, "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# =======================================

# 教师系统页面部分

# =======================================


# 教师绑定班级接口
@app.route("/api/teacher/classes", methods=["GET"])
def get_teacher_classes():
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录"}), 401

    user_id = payload.get("user_id")
    role = payload.get("role")

    # 教师或管理员可查看
    if role not in ["teacher", "admin"]:
        return jsonify({"code": 403, "message": "权限不足"}), 403

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        if role == "admin":
            # 管理员可查看所有班级
            cursor.execute("SELECT id, grade, class FROM class ORDER BY grade, class")
            results = cursor.fetchall()
            data = [{"id": r[0], "grade": r[1], "class": r[2]} for r in results]
        else:
            # 教师只查看绑定的班级
            sql = """
                SELECT c.id, c.grade, c.class
                FROM class c
                JOIN teacher_classes tc ON c.id = tc.class_id
                WHERE tc.teacher_id = %s
                ORDER BY c.grade, c.class
            """
            cursor.execute(sql, (user_id,))
            results = cursor.fetchall()
            data = [{"id": r[0], "grade": r[1], "class": r[2]} for r in results]

        return jsonify({"code": 200, "data": data}), 200

    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# 查看班级学生表格接口
@app.route("/api/students/by-class/<int:class_id>", methods=["GET"])
def get_students_by_class(class_id):
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录"}), 401

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    sql = "SELECT id, name, gender, age, score FROM students WHERE class_id = %s ORDER BY name"
    cursor.execute(sql, (class_id,))
    results = cursor.fetchall()

    data = []
    for row in results:
        data.append(
            {
                "id": row[0],
                "name": row[1],
                "gender": row[2],
                "age": row[3],
                "score": row[4],
            }
        )

    return jsonify({"code": 200, "data": data}), 200


# 科目接口
@app.route("/api/subjects/options", methods=["GET"])
def get_subject_options():
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录"}), 401

    # 教师或管理员可查看
    if payload.get("role") not in ["teacher", "admin"]:
        return jsonify({"code": 403, "message": "权限不足"}), 403

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # 获取所有科目，只返回 id 和 subject 名称
        sql = "SELECT id, subject FROM subjects ORDER BY subject"
        cursor.execute(sql)
        results = cursor.fetchall()

        data = [{"id": r[0], "subject": r[1]} for r in results]

        return jsonify({"code": 200, "data": data}), 200

    except Exception as e:
        print("❌ 获取科目选项失败：", e)
        return jsonify({"code": 500, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# 成绩录入
@app.route("/api/scores/batch", methods=["POST"])
def batch_save_scores():
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录"}), 401

    if payload.get("role") not in ["teacher", "admin"]:
        return jsonify({"code": 403, "message": "权限不足"}), 403

    data = request.get_json()
    class_id = data.get("class_id")
    subject_id = data.get("subject_id")
    scores = data.get("scores", [])

    # 校验班级
    if not class_id:
        return jsonify({"code": 400, "message": "请选择班级"}), 400

    # 校验科目
    if not subject_id:
        return jsonify({"code": 400, "message": "请选择科目"}), 400

    # 校验成绩列表
    if not scores:
        return jsonify({"code": 400, "message": "成绩列表不能为空"}), 400

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # 先删除该班级该科目的旧成绩（覆盖更新）
        sql_delete = "DELETE FROM student_subjects WHERE student_id IN (SELECT id FROM students WHERE class_id = %s) AND subject_id = %s"
        cursor.execute(sql_delete, (class_id, subject_id))

        # 批量插入新成绩
        sql_insert = "INSERT INTO student_subjects (student_id, subject_id, score) VALUES (%s, %s, %s)"
        for item in scores:
            cursor.execute(sql_insert, (item["student_id"], subject_id, item["score"]))

        conn.commit()
        return jsonify({"code": 200, "message": f"成功保存 {len(scores)} 条成绩"}), 200

    except Exception as e:
        print("❌ 批量保存成绩失败：", e)
        conn.rollback()
        return jsonify({"code": 500, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# 成绩查询
@app.route("/api/scores/by-class-subject", methods=["GET"])
def get_scores_by_class_subject():
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录"}), 401

    if payload.get("role") not in ["teacher", "admin"]:
        return jsonify({"code": 403, "message": "权限不足"}), 403

    class_id = request.args.get("class_id")
    subject_id = request.args.get("subject_id")

    if not class_id or not subject_id:
        return jsonify({"code": 400, "message": "班级和科目不能为空"}), 400

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        sql = """
            SELECT s.id, s.name, s.gender, ss.score
            FROM students s
            LEFT JOIN student_subjects ss ON s.id = ss.student_id AND ss.subject_id = %s
            WHERE s.class_id = %s
            ORDER BY s.name
        """
        cursor.execute(sql, (subject_id, class_id))
        results = cursor.fetchall()
        # 1. 获取该科目的满分
        cursor.execute("SELECT full_score FROM subjects WHERE id = %s", (subject_id,))
        full_score_row = cursor.fetchone()
        if not full_score_row:
            return jsonify({"code": 404, "message": "科目不存在"}), 404
        full_score = full_score_row[0]

        # 提取有效成绩（非 None）
        scores = [row[3] for row in results if row[3] is not None]
        total = len(scores)

        # 4. 计算统计指标（基于满分百分比）
        pass_threshold = full_score * 0.6
        excellent_threshold = full_score * 0.9

        if total > 0:
            avg_score = round(sum(scores) / total, 2)
            max_score = max(scores)
            min_score = min(scores)
            pass_count = len([s for s in scores if s >= pass_threshold])
            excellent_count = len([s for s in scores if s >= excellent_threshold])
            pass_rate = round(pass_count / total * 100, 1)
            excellent_rate = round(excellent_count / total * 100, 1)
        else:
            avg_score = max_score = min_score = pass_count = excellent_count = (
                pass_rate
            ) = excellent_rate = 0

        data = []
        for row in results:
            data.append(
                {
                    "student_id": row[0],
                    "name": row[1],
                    "gender": row[2],
                    "score": row[3] if row[3] is not None else "未录入",
                }
            )

        # ✅ 返回数据 + 统计信息
        return (
            jsonify(
                {
                    "code": 200,
                    "data": data,
                    "stats": {
                        "total": total,
                        "avg": avg_score,
                        "max": max_score,
                        "min": min_score,
                        "pass_count": pass_count,
                        "excellent_count": excellent_count,
                        "pass_rate": pass_rate,
                        "excellent_rate": excellent_rate,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        print("❌ 查询成绩失败：", e)
        return jsonify({"code": 500, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# 学生自己成绩查询
@app.route("/api/student/<int:student_id>/scores", methods=["GET"])
def get_student_scores(student_id):
    payload = verify_token()
    if not payload:
        return jsonify({"code": 401, "message": "未登录"}), 401

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # 获取学生基本信息
        sql_student = """
            SELECT s.name, c.grade, c.class
            FROM students s
            LEFT JOIN class c ON s.class_id = c.id
            WHERE s.id = %s
        """
        cursor.execute(sql_student, (student_id,))
        student = cursor.fetchone()
        if not student:
            return jsonify({"code": 404, "message": "学生不存在"}), 404

        # 获取成绩列表
        sql_scores = """
            SELECT sub.subject, ss.score, sub.full_score
            FROM student_subjects ss
            JOIN subjects sub ON ss.subject_id = sub.id
            WHERE ss.student_id = %s
            ORDER BY sub.subject
        """
        cursor.execute(sql_scores, (student_id,))
        scores = cursor.fetchall()

        data = {
            "name": student[0],
            "class_name": (
                f"{student[1]}{student[2]}班" if student[1] and student[2] else "未分配"
            ),
            "scores": [
                {"subject": row[0], "score": row[1], "full_score": row[2]}
                for row in scores
            ],
        }

        return jsonify({"code": 200, "data": data}), 200

    except Exception as e:
        print("❌ 查询学生成绩失败：", e)
        return jsonify({"code": 500, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
