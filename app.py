from src import app
from src.db.postgres import init_db


def main():
    init_db(app)
    app.run(debug=True)


if __name__ == '__main__':
    main()
