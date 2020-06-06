# Weather Template
Weather Template for Home Assisstant

## How it works
This custom component adds a weather template that can be used to merge various weather components for use in a weather card

## Configuration
This component adds a weather_template platform that functions similar to the regular template platforms

example configuration:
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

### Configuration Variables ###
<dl>
 <dt>weather</dt>
 <dd>
  <i>(map)(Required)</i><br/>Listof your weather stations
  <dl>
   <dt>station_name</dt>
   <dd>
    <i>(map)(Required)</i><br/>The slug of the station
    <dl>
     <dt>friendly_name</dt>
     <dd><i>(string)(Optional)</i><br/>The name to use on the front end.</dd>
    </dl>
    <dl>
     <dt>entity_id</dt>
     <dd><i>(string|list)(Optional)</i><br/>
      A list of entity IDs so the station only reacts to state changes of these entities. 
      This can be used if the automatic analysis fails to find all relevant entities.
     </dd>
    </dl>
    <dl>
     <dt>condition_template</dt>
     <dd><i>(template)(Required)</i><br/>
      A template that evaluates to a <a href="https://www.home-assistant.io/integrations/weather/#condition-mapping">weather condition</a>
     </dd>
    </dl>
    <dl>
     <dt>temperature_template</dt>
     <dd><i>(template)(Required)</i><br/>
      A template that evaluates to a numeric temperature value
     </dd>
    </dl>
    <dl>
     <dt>temperature_unit_template</dt>
     <dd><i>(template)(Required)</i><br/>
      A template that evaluates to a temperature unitof measurement (either °F or °C)
     </dd>
    </dl>
    <dl>
     <dt>availability_template</dt>
     <dd><i>(template)(Option)</i><br/>
      Defines a template to get the available state of the component. 
      If the template returns true, the device is available. 
      If the template returns any other value, the device will be unavailable. 
      If availability_template is not configured, the component will always be available.
      <br/><br/>
      <i>Default value:</i><br/>true
     </dd>
    </dl>
    <dl>
     <dt>pressure_template</dt>
     <dd><i>(template)(Optional)</i><br/>
      A template that evaluates to a numeric pressure
      <br/><br/>
      <i>Default value:</i><br/>None
     </dd>
    </dl>
    <dl>
     <dt>humidity_template</dt>
     <dd><i>(template)(Optional)</i><br/>
      A template that evaluates to a numeric humidity
      <br/><br/>
      <i>Default value:</i><br/>None
     </dd>
    </dl>
    <dl>
     <dt>wind_template</dt>
     <dd><i>(template)(Optional)</i><br/>
      A template that evaluates to a numeric wind speed
      <br/><br/>
      <i>Default value:</i><br/>None
     </dd>
    </dl>
    <dl>
     <dt>wind_bearing_template</dt>
     <dd><i>(template)(Optional)</i><br/>
      A template that evaluates to a numeric(in degrees) wind bearing
      <br/><br/>
      <i>Default value:</i><br/>None
     </dd>
    </dl>
    <dl>
     <dt>ozone_template</dt>
     <dd><i>(template)(Optional)</i><br/>
      A template that evaluates to a numeric ozone value
      <br/><br/>
      <i>Default value:</i><br/>None
     </dd>
    </dl>
    <dl>
     <dt>visibility_template</dt>
     <dd><i>(template)(Optional)</i><br/>
      A template that evaluates to a numeric visibility range
      <br/><br/>
      <i>Default value:</i><br/>None
     </dd>
    </dl>
    <dl>
     <dt>forecast_template</dt>
     <dd><i>(template)(Optional)</i><br/>
      A template that evaluates <i>proper</i> json representing forcast data.
      <br/><br/>
      <i>Default value:</i><br/>None
     </dd>
    </dl>
    <dl>
     <dt>attribution_template</dt>
     <dd><i>(template)(Optional)</i><br/>
      A template that evaluates to the text to atribute the data to
      <br/><br/>
      <i>Default value:</i><br/>None
     </dd>
    </dl>
   </dd>
  </dl>
 </dd>
<dl>
