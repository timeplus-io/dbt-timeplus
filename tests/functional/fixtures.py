# seeds/my_seed.csv
my_seed_csv = """
id,name,some_date
1,Easton,1981-05-20T06:46:51
2,Lillian,1978-09-03T18:10:33
3,Jeremiah,1982-03-11T03:59:51
4,Nolan,1976-05-06T20:21:35
""".lstrip()

# models/my_model.sql
my_model_sql = """
{{ config(
  pre_hook=[
    "create random stream if not exists " ~ target.schema ~ ".car_live_data (\n"
    ~ "  cid string,\n"
    ~ "  gas_percent float64,\n"
    ~ "  in_use bool,\n"
    ~ "  latitude float64,\n"
    ~ "  locked bool,\n"
    ~ "  longitude float64,\n"
    ~ "  speed_kmh float64,\n"
    ~ "  time string,\n"
    ~ "  total_km float64\n"
    ~ ")"
  ]
) }}
select window_end, cid, count() as cnt
from tumble(table(car_live_data), 1s)
group by window_end, cid
"""

# models/my_model.yml
my_model_yml = """
version: 2
sources:
  - name: default
    description: these tables are created via car sharing demo app
    tables:
      - name: dim_user_info
        description: A relative static table with all registered user informations.
        columns:
          - name: uid
            description: user id
            tests:
              - not_null
              - unique
          - name: first_name
            description: first name
            tests:
              - not_null   
          - name: last_name
            description: last name
            tests:
              - not_null       
          - name: email
            description: email address
            tests:
              - not_null          
          - name: credit_card
            description: credit card number
            tests:
              - not_null      
          - name: gender
            description: F for female, M for male
            tests:
              - not_null     
              - accepted_values:
                  values: ['F','M']      
          - name: birthday
            description: birthday
            tests:
              - not_null            
      - name: dim_car_info
        description: A relative static table with all registered cars
        columns:
          - name: cid
            description: car id
            tests:
              - not_null
              - unique
          - name: license_plate_no
            description: the license plate number
            tests:
              - not_null  
              - unique 
          - name: in_service
            description: whether it's in service or in maintainance
            tests:
              - not_null            
      - name: car_live_data
        description: A data stream with latest data from car sensors. When the car engine is started, report data every second. Otherwise, report data every half an hour.
        columns:
          - name: time
            description: datetime of the sensor data
            tests:
              - not_null
          - name: cid
            description: car id
            tests:
              - not_null  
              - relationships:
                  to: source('default','dim_car_info')
                  field: cid
          - name: longitude
            description: current position
            tests:
              - not_null        
          - name: latitude
            description: current position
            tests:
              - not_null   
          - name: gas_percent
            description: percentage of gas level, 100 means full tank
            tests:
              - not_null        
          - name: speed_kmh
            description: current driving speed in KM/hour
            tests:
              - not_null       
          - name: total_km
            description: this car's total distance in km. Keep increasing after trips
            tests:
              - not_null   
          - name: locked
            description: whether the car is locked
            tests:
              - not_null   
          - name: in_use
            description: whether someone is using the car
            tests:
              - not_null   
      - name: bookings
        description: A data stream with trip details and payment info. Each row is generated during the booking lifecycle
        columns:
          - name: time
            description: When the event happens
            tests:
              - not_null
          - name: bid
            description: booking id
            tests:
              - not_null  
          - name: booking_time
            description: When the user books the car. Expire in 30min
            tests:
              - not_null
          - name: uid
            description: user id
            tests:
              - not_null  
              - relationships:
                  to: source('default','dim_user_info')
                  field: uid
          - name: cid
            description: car id
            tests:
              - not_null  
              - relationships:
                  to: source('default','dim_car_info')
                  field: cid
          - name: action
            description: "the action of the booking entry"
            tests:
              - not_null        
              - accepted_values:
                  values: ['add','cancel','extend','service','end','expire']  
          - name: expire
            description: When the booking will be expired
            tests:
              - not_null   
      - name: trips
        description: A data stream with trip details and payment info. Each row is generated at the end of the trip
        columns:
          - name: tid
            description: trip id
            tests:
              - not_null  
              - unique
          - name: start_time
            description: When the trip starts
            tests:
              - not_null
          - name: end_time
            description: When the trip ends
            tests:
              - not_null
          - name: bid
            description: booking id
            tests:
              - not_null  
              - relationships:
                  to: source('default','bookings')
                  field: bid
          - name: start_lon
            description: start location
            tests:
              - not_null
          - name: start_lat
            description: start location
            tests:
              - not_null
          - name: end_lon
            description: end location
            tests:
              - not_null
          - name: end_lat
            description: end location
            tests:
              - not_null
          - name: distance
            description: distance drove in km
            tests:
              - not_null  
          - name: amount
            description: how much the user should pay for the trip
            tests:
              - not_null  
"""
