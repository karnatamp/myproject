import os
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class Config:
    SECRET_KEY = 'l4P2EdBhT0N04F9sPArHLh2CLUCk1Q'
    WTF_CSRF_SECRET_KEY = 'nI6RmnmFL1x9t5-7V3yCUv1iCeWnO-OBU5Yh09Zk'


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True


class ProductionConfig(Config):
    pass