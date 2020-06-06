""" Template Weather Component """

import logging
import json

import voluptuous as vol

from homeassistant.components.weather import (
    PLATFORM_SCHEMA,
    ENTITY_ID_FORMAT,
    WeatherEntity,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_FRIENDLY_NAME,
    ATTR_UNIT_OF_MEASUREMENT,
    EVENT_HOMEASSISTANT_START,
    CONF_FRIENDLY_NAME_TEMPLATE,
    MATCH_ALL,
)
from .const import (
    CONF_WEATHER,
    CONF_ATTRIBUTION_TEMPLATE,
    CONF_CONDITION_TEMPLATE,
    CONF_FORECAST_TEMPLATE,
    CONF_HUMIDITY_TEMPLATE,
    CONF_OZONE_TEMPLATE,
    CONF_PRESSURE_TEMPLATE,
    CONF_TEMPERATURE_TEMPLATE,
    CONF_TEMPERATURE_UNIT_TEMPLATE,
    CONF_VISIBILITY_TEMPLATE,
    CONF_WIND_DIR_TEMPLATE,
    CONF_WIND_TEMPLATE,
)

from homeassistant.core import callback
from homeassistant.exceptions import TemplateError
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity, async_generate_entity_id
from homeassistant.helpers.event import async_track_state_change

from homeassistant.components.template import extract_entities, initialise_templates
from homeassistant.components.template.const import CONF_AVAILABILITY_TEMPLATE

_LOGGER = logging.getLogger(__name__)
_LOGGER.debug("Loading...")

WEATHER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TEMPERATURE_TEMPLATE): cv.template,
        vol.Required(CONF_TEMPERATURE_UNIT_TEMPLATE): cv.template,
        vol.Optional(CONF_PRESSURE_TEMPLATE): cv.template,
        vol.Required(CONF_HUMIDITY_TEMPLATE): cv.template,
        vol.Optional(CONF_WIND_TEMPLATE): cv.template,
        vol.Optional(CONF_WIND_DIR_TEMPLATE): cv.template,
        vol.Optional(CONF_OZONE_TEMPLATE): cv.template,
        vol.Optional(CONF_ATTRIBUTION_TEMPLATE): cv.template,
        vol.Optional(CONF_VISIBILITY_TEMPLATE): cv.template,
        vol.Optional(CONF_FORECAST_TEMPLATE): cv.template,
        vol.Required(CONF_CONDITION_TEMPLATE): cv.template,
        vol.Optional(CONF_AVAILABILITY_TEMPLATE): cv.template,
        vol.Optional(ATTR_FRIENDLY_NAME): cv.string,
        vol.Optional(CONF_FRIENDLY_NAME_TEMPLATE): cv.template,
        vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,        
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_WEATHER): cv.schema_with_slug_keys(WEATHER_SCHEMA)}
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the template weather."""

    _LOGGER.debug("Setting up platform")

    weather = []

    for device, device_config in config[CONF_WEATHER].items():
        attribution_template = device_config.get(CONF_ATTRIBUTION_TEMPLATE)
        condition_template = device_config[CONF_CONDITION_TEMPLATE]
        forecast_template = device_config.get(CONF_FORECAST_TEMPLATE)
        humidity_template = device_config.get(CONF_HUMIDITY_TEMPLATE)
        ozone_template = device_config.get(CONF_OZONE_TEMPLATE)
        pressure_template = device_config.get(CONF_PRESSURE_TEMPLATE)
        temperature_template = device_config.get(CONF_TEMPERATURE_TEMPLATE)
        temperature_unit_template = device_config.get(CONF_TEMPERATURE_UNIT_TEMPLATE)
        visibility_template = device_config.get(CONF_VISIBILITY_TEMPLATE)
        wind_bearing_template = device_config.get(CONF_WIND_DIR_TEMPLATE)
        wind_template = device_config.get(CONF_WIND_TEMPLATE)
        friendly_name = device_config.get(ATTR_FRIENDLY_NAME, device)
        friendly_name_template = device_config.get(CONF_FRIENDLY_NAME_TEMPLATE)
        availability_template = device_config.get(CONF_AVAILABILITY_TEMPLATE)

        templates = {
            CONF_AVAILABILITY_TEMPLATE: availability_template,
            CONF_ATTRIBUTION_TEMPLATE: attribution_template,
            CONF_CONDITION_TEMPLATE: condition_template,
            CONF_FORECAST_TEMPLATE: forecast_template,
            CONF_HUMIDITY_TEMPLATE: humidity_template,
            CONF_OZONE_TEMPLATE: ozone_template,
            CONF_PRESSURE_TEMPLATE: pressure_template,
            CONF_TEMPERATURE_TEMPLATE: temperature_template,
            CONF_TEMPERATURE_UNIT_TEMPLATE: temperature_unit_template,
            CONF_VISIBILITY_TEMPLATE: visibility_template,
            CONF_WIND_DIR_TEMPLATE: wind_bearing_template,
            CONF_WIND_TEMPLATE: wind_template,
        }

        initialise_templates(hass, templates)
        entity_ids = extract_entities(
            device,
            "weather",
            device_config.get(ATTR_ENTITY_ID),
            templates
        )

        _LOGGER.debug("Creating entity %s...", friendly_name)
        weather.append(
            WeatherTemplate(
                hass,
                device,
                friendly_name,
                friendly_name_template,
                condition_template,
                temperature_template,
                temperature_unit_template,
                pressure_template,
                humidity_template,
                wind_template,
                wind_bearing_template,
                ozone_template,
                attribution_template,
                visibility_template,
                forecast_template,
                availability_template,
                entity_ids
            )
        )

    async_add_entities(weather)
    _LOGGER.debug("Done.")

class WeatherTemplate(WeatherEntity):
    """Representation of a Weather Template"""

    def __init__(
        self,
        hass,
        device_id,
        friendly_name,
        friendly_name_template,
        condition_template,
        temperature_template,
        temperature_unit_template,
        pressure_template,
        humidity_template,
        wind_template,
        wind_bearing_template,
        ozone_template,
        attribution_template,
        visibility_template,
        forecast_template,
        availability_template,
        entity_ids,
    ):
        """Initialize the entity."""

        self.hass = hass
        self.entity_id = async_generate_entity_id(
            ENTITY_ID_FORMAT, device_id, hass=hass
        )
        self._name = friendly_name
        self._friendly_name_template = friendly_name_template
        self._condition_template = condition_template
        self._condition = None
        self._availability_template = availability_template
        self._available = False
        self._temperature = None
        self._temperature_template = temperature_template
        self._temperature_units = None
        self._temperature_unit_template = temperature_unit_template
        self._pressure = None
        self._pressure_template = pressure_template
        self._humidity = None
        self._humidity_template = humidity_template
        self._wind = None
        self._wind_template = wind_template
        self._wind_bearing = None
        self._wind_bearing_template = wind_bearing_template
        self._ozone = None
        self._ozone_template = ozone_template
        self._attribution = None
        self._attribution_template = attribution_template
        self._visibility = None
        self._visibility_template = visibility_template
        self._forecast = None
        self._forecast_template = forecast_template
        self._entities = entity_ids
        _LOGGER.debug("Created entity %s: %s", self.entity_id, friendly_name)

    async def async_added_to_hass(self):
        """Register callbacks."""
        _LOGGER.debug("Registering: %s...", self.entity_id)

        @callback
        def template_state_listener(entity, old_state, new_state):
            """Handle device state changes."""
            _LOGGER.debug("Got template state change from %s: %s...", entity, self._name)
            self.async_schedule_update_ha_state(True)

        @callback
        def template_weather_startup(event):
            """Update template on startup."""
            _LOGGER.debug("Starting up: %s...", self._name)

            if self._entities != MATCH_ALL:
                # Track state change only for valid templates
                async_track_state_change(
                    self.hass, self._entities, template_state_listener
                )

            self.async_schedule_update_ha_state(True)

        self.hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_START, template_weather_startup
        )
        
    @property
    def should_poll(self):
        """ this is event driven so polling is unecessary """
        return False

    @property
    def available(self):
        """ return if weather data is available. """
        return self._available

    @property
    def attribution(self):
        """Return the attribution."""
        return self._attribution

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
        
    @property
    def temperature(self):
        """Return the temperature."""
        return self._temperature

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._temperature_units

    @property
    def humidity(self):
        """Return the humidity."""
        return self._humidity

    @property
    def wind_speed(self):
        """Return the wind speed."""
        return self._wind

    @property
    def wind_bearing(self):
        """Return the wind bearing."""
        return self._wind_bearing

    @property
    def ozone(self):
        """Return the ozone level."""
        return self._ozone

    @property
    def pressure(self):
        """Return the pressure."""
        return self._pressure

    @property
    def visibility(self):
        """Return the visibility."""
        return self._visibility

    @property
    def condition(self):
        """Return the weather condition."""
        return self._condition

    @property
    def forecast(self):
        """Return the forecast array."""
        return self._forecast

    async def async_update(self):
        """Update the state from the template."""
        _LOGGER.debug("Updating: %s...", self._name)

        try:
            self._condition = self._condition_template.async_render()
            self._temperature = float(self._temperature_template.async_render())
            self._temperature_units = self._temperature_unit_template.async_render()
            self._available = True
        except TemplateError as ex:
            self._available = False
            if ex.args and ex.args[0].startswith(
                "UndefinedError: 'None' has no attribute"
            ):
                # Common during HA startup - so just a warning
                _LOGGER.warning(
                    "Could not render template %s, the state is unknown.", self._name
                )
            else:
                self._condition = None
                self._temperature = None
                self._temperature_units = None
                _LOGGER.error("Could not render template %s: %s", self._name, ex)            
            
        for property_name, template, formatter in (
            ("_name", self._friendly_name_template, None),
            ("_available", self._availability_template, lambda v: v.lower() == "true"),
            ("_attribution", self._attribution_template, None),
            ("_forecast", self._forecast_template, lambda v: json.loads(v) ),
            ("_humidity", self._humidity_template, lambda v: float(v)),
            ("_ozone", self._ozone_template, lambda v: float(v)),
            ("_pressure", self._pressure_template, lambda v: float(v)),
            ("_visibility", self._visibility_template, lambda v: float(v)),
            ("_wind_bearing", self._wind_bearing_template, lambda v: float(v)),
            ("_wind", self._wind_template, lambda v: float(v)),
        ):
            if template is None:
                continue

            try:
                value = template.async_render()
                if(formatter is not None):
                    value = formatter(value)
                
                setattr(self, property_name, value)
            except TemplateError as ex:
                friendly_property_name = property_name[1:].replace("_", " ")
                if ex.args and ex.args[0].startswith(
                    "UndefinedError: 'None' has no attribute"
                ):
                    # Common during HA startup - so just a warning
                    _LOGGER.warning(
                        "Could not render %s template %s, the state is unknown.",
                        friendly_property_name,
                        self._name,
                    )
                    continue

                try:
                    setattr(self, property_name, getattr(super(), property_name))
                except AttributeError:
                    _LOGGER.error(
                        "Could not render %s template %s: %s",
                        friendly_property_name,
                        self._name,
                        ex,
                    )
        _LOGGER.debug("Updated: %s...", self._name)
        