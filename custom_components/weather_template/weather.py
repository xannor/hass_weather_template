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
    CONF_ENTITY_ID,
    CONF_UNIQUE_ID,
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
from homeassistant.helpers.reload import async_setup_reload_service

from homeassistant.components.template.template_entity import TemplateEntity
from homeassistant.components.template.const import CONF_AVAILABILITY_TEMPLATE

_LOGGER = logging.getLogger(__name__)
_LOGGER.debug("Loading...")

WEATHER_SCHEMA = vol.All(
    cv.deprecated(CONF_ENTITY_ID),
    vol.Schema(
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
            vol.Optional(CONF_ENTITY_ID): cv.entity_ids,
            vol.Optional(CONF_UNIQUE_ID): cv.string,
        }
    ),
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_WEATHER): cv.schema_with_slug_keys(WEATHER_SCHEMA)}
)

async def _async_create_entities(hass, config):
    """Create the Template Weather."""
    weather = []

    _LOGGER.debug("Creating Entities")

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
        unique_id = device_config.get(CONF_UNIQUE_ID)

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
                unique_id
            )
        )

    return weather

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the template weather."""

    _LOGGER.debug("Setting up platform")

    await async_setup_reload_service(hass, "weather", "weather_template")
    async_add_entities(await _async_create_entities(hass, config))
    _LOGGER.debug("Done.")

class WeatherTemplate(TemplateEntity, WeatherEntity):
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
        unique_id,
    ):
        """Initialize the entity."""

        super().__init__(availability_template=availability_template)
        self.hass = hass
        self.entity_id = async_generate_entity_id(
            ENTITY_ID_FORMAT, device_id, hass=hass
        )
        self._name = friendly_name
        self._friendly_name_template = friendly_name_template
        self._condition = None
        self._condition_template = condition_template
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
        self._unique_id = unique_id
        _LOGGER.debug("Created entity %s: %s", self.entity_id, friendly_name)

    @callback
    def _create_updater(self, property_name, formatter):

        @callback
        def _updater(value):
            if value is not None and formatter is not None:
                value = formatter(value)

            setattr(self, property_name, value)
            _LOGGER.debug("Updated %s.%s to %s", self.entity_id, property_name, value)

        return _updater

    def _update_forecast(self, forecast):
        try:
            forecast_json = json.loads(forecast)
        except ValueError:
            _LOGGER.error(
                "Could not parse forecast from template response: %s", forecast
            )
            self._forecast = None
            return
        self._forecast = forecast_json

    def _add_float_template_attribute(
        self,
        attribute,
        template, 
        validator = None,
        none_on_template_error: bool = False,
    ) -> None:
        """ wrapper around add_template_attribute that formats as a float """

        def on_update(value):
            if value is not None:
                try:
                    fvalue = float(value)
                except ValueError:
                    _LOGGER.error(
                        "Could not parse %s result as a number: %s", attribute, value
                    )
                    setattr(self, attribute, None)
                    return
            setattr(self, attribute, fvalue)

        self.add_template_attribute(
            attribute,
            template,
            validator,
            on_update,
            none_on_template_error
        )

    async def async_added_to_hass(self):
        """Register callbacks."""
        _LOGGER.debug("Registering: %s...", self.entity_id)

        self.add_template_attribute(
            "_condition", self._condition_template
        )
        self._add_float_template_attribute(
            "_temperature", self._temperature_template
        )
        self.add_template_attribute(
            "_temperature_units", self._temperature_unit_template
        )

        if self._friendly_name_template is not None:
            self.add_template_attribute(
                "_name", self._friendly_name_template
            )

        if self._attribution_template is not None:
            self.add_template_attribute(
                "_attribution", self._attribution_template
            )

        if self._forecast_template is not None:
            self.add_template_attribute(
                "_forecast", self._forecast_template, None, self._update_forecast
            )

        if self._humidity_template is not None:
            self._add_float_template_attribute(
                "_humidity", self._humidity_template
            )

        if self._ozone_template is not None:
            self._add_float_template_attribute(
                "_ozone", self._ozone_template
            )

        if self._pressure_template is not None:
            self._add_float_template_attribute(
                "_pressure", self._pressure_template
            )

        if self._visibility_template is not None:
            self._add_float_template_attribute(
                "_visibility", self._visibility_template
            )

        if self._wind_bearing_template is not None:
            self._add_float_template_attribute(
                "_wind_bearing", self._wind_bearing_template
            )

        if self._wind_template is not None:
            self._add_float_template_attribute(
                "_wind", self._wind_template
            )
        
        _LOGGER.debug("Registered: %s...", self.entity_id)
            
        await super().async_added_to_hass()

    @property
    def attribution(self):
        """Return the attribution."""
        return self._attribution

    @property
    def name(self):
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique id of this entity."""
        return self._unique_id
        
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
        