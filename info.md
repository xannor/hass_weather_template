# Weather Template
Weather Template for Home Assisstant

## How it works
This custom component adds a weather template that can be used to merge various weather components for use in a weather card

## Installation

### HACS
Requirements:
 - HACS version 0.9 or higher
 
 Add this repo as a custom repository [integration] in hacs and install
 
### Manual ###
copy the entire weather_template folder in custom_components into the config/custom_components folder on your installation, reboot, and add template to your configuration yaml

## Usage
This component adds a weather_template platform that functions similar to the regular template platforms

example:
```
weather:
- platform: weather_template
  weather:
    darksky_meteobridge:
      availability_template: "{{ true if states('sensor.temperature') != None and states('weather.dark_sky') != None else false }}"
      temperature_template: "{{ states('sensor.temperature') }}"
      temperature_unit_template: "{{ state_attr('sensor.temperature', 'unit_of_measurement') }}"
      condition_template: "{{ states('weather.dark_sky') }}"
      pressure_template: "{{ states('sensor.pressure') }}"
      humidity_template: "{{ states('sensor.humidity') }}"
      wind_template: "{{ states('sensor.wind_speed') }}"
      wind_bearing_template: "{{ states('sensor.wind_bearing') }}"
      ozone_template: "{{ state_attr('weather.dark_sky', 'ozone') }}"
      attribution_template: "{{ state_attr('weather.dark_sky', 'attribution') }} and {{ state_attr('sensor.temperature', 'brand') }}"
      visibility_template: "{{ state_attr('weather.dark_sky', 'visibility') }}"
      forecast_template: "{{ state_attr('weather.dark_sky', 'forecast') | to_json }}"

```
