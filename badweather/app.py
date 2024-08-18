from flask import Flask, render_template
from sqlalchemy import create_engine
import pandas as pd

app = Flask(__name__)

def load_dataframe():
    engine = create_engine(f'mysql+pymysql://dieter:password@127.0.0.1:3306/dieter$default')
    query = 'select * from weather_data where not isnull(actual_temp)'
    df = pd.read_sql(query, engine)
    df = df.astype({'actual_temp': 'int64', 'actual_rain': 'int64'})
    return df

def add_time_labels(df):
    df

def calculate_temp_accuracy(group, tolerance):
    predictions = group[
        (group['actual_temp'] >= group['predicted_temp'] - tolerance) &
        (group['actual_temp'] <= group['predicted_temp'] + tolerance)
    ]
    accuracy = (len(predictions) / len(group)) * 100 if len(group) > 0 else 0
    if accuracy == 100.0 or accuracy == 0:
        accuracy = int(accuracy)

    return f'{accuracy}%'

def calculate_rain_accuracy(group, tolerance):
    if (group['actual_rain'] == 0).all() and (group['predicted_rain'] == 0).all():
        return '100%'
    
    predictions = group[
        (group['actual_rain'] > 0) &
        (group['predicted_rain'] > tolerance)
    ]
    print(f'Len group: {len(group)}, len pred: {len(predictions)}')
    accuracy = (len(predictions) / len(group)) * 100 if len(group) > 0 else 0
    if accuracy == 100.0 or accuracy == 0:
        accuracy = int(accuracy)

    return f'{accuracy}%'

def create_accuracy_df(accuracy_function, tolerance):
    data = df[df['offset'] == 0]
    data = data.groupby('time').apply(accuracy_function, tolerance)
    data = data.reset_index(name='accuracy')
    data['time'] = data['time'].replace(time_labels)

    data['time_numeric'] = data['time'].str.extract('(\\d+)').astype(int)
    data = data.sort_values(by='time_numeric')
    data = data.drop(columns='time_numeric')

    by_day = df[df['offset'] > 0]
    if by_day.shape[0] > 0 :
        by_day = by_day.groupby('offset').apply(accuracy_function, tolerance)
        by_day = by_day.reset_index(name='accuracy')
        by_day['offset'] = by_day['offset'].replace(day_labels)
        by_day = by_day.rename(columns={'offset': 'time'})
        by_day = by_day.sort_values(by='time')

        data = pd.concat([data, by_day], ignore_index=True)
    
    return data

def create_context():
    temp_accuracy = create_accuracy_df(calculate_temp_accuracy, temp_tolerance)
    temp_accuracy = temp_accuracy.to_dict(orient='records')

    rain_accuracy = create_accuracy_df(calculate_rain_accuracy, rain_tolerance)
    rain_accuracy = rain_accuracy.to_dict(orient='records')

    friendly_columns = [
        'Date',
        'Day Offset',
        'Time',
        'Predicted Type',
        'Predicted Temp.',
        'Predicted Rain',
        'Actual Type',
        'Actual Temp.',
        'Actual Rain'
    ]

    context = {
        'friendly_columns': friendly_columns,
        'columns': df.columns,
        'rows': df.to_dict(orient='records'),
        'temp_tolerance': temp_tolerance,
        'temp_accuracy': temp_accuracy,
        'rain_tolerance': rain_tolerance,
        'rain_accuracy': rain_accuracy
    }
    return context

time_labels = {
    0: '12 hours',
    13: '1 hour',
    15: '3 hours',
    18: '6 hours',
}

day_labels = {
    0: '0 days',
    1: '1 day',
    2: '2 days',
    3: '3 days'
}

df = load_dataframe()
temp_tolerance=1
rain_tolerance=10
context = create_context()

@app.route('/')
def index():
    return render_template('index.html', **context)