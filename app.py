from dotenv import load_dotenv
from website import create_app
from dotenv import load_dotenv, find_dotenv
import os

app = create_app()

if __name__ == '__main__':
    load_dotenv(find_dotenv())
    app.run(debug=os.getenv('IS_DEV'))


