import findspark
findspark.init()
from tensorflow.keras.models import load_model
from tensorflow.keras import models, utils
import tensorflow_hub as hub
from tensorflow_estimator.python.estimator.canned.dnn import dnn_logit_fn_builder
import tensorflow as tf
from datetime import date
import streamlit as st
import pandas as pd
import pyspark
import time
from pyspark.ml.recommendation import ALS
from pyspark import SparkContext, SQLContext, SparkConf, StorageLevel
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.ml.feature import StringIndexer
from pyspark.sql.functions import col
from pyspark.mllib.recommendation import Rating
from pyspark.ml import Pipeline
# import pywhatkit
import datetime
from twilio.rest import Client
import smtplib
from email.message import EmailMessage
import pyautogui as pg
import numpy as np
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
from xlsxwriter import Workbook
import math
import requests