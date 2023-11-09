using System.Runtime.CompilerServices;
using Microsoft.AspNetCore.Mvc;

namespace web_api.Controllers
{
  [ApiController]
  [Route("[controller]")]
  public class WeatherForecastController : ControllerBase
  {
    private static readonly string[] Summaries = 
    {
      "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"
    };

    private static readonly string[] PostalCodes = 
    {
      "K1A 0B1", "V6C 1V5", "M5V 2T6", "L5V 1M5"
    };

    private readonly ILogger<WeatherForecastController> _logger;

    public WeatherForecastController(ILogger<WeatherForecastController> logger)
    {
      _logger = logger;
    }

    [HttpGet(Name = "GetWeatherForecast")]
    [ProducesResponseType(typeof(IEnumerable<WeatherForecast>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(string), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(string), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(string), StatusCodes.Status500InternalServerError)]
    [Produces("application/json")]
    public ActionResult<Object> Get()
    {
      var postalCode = GetRandomPostalCode();
      var temperature = GetRandomTemperature();
      var condition = GetRandomCondition();
      var conditionIntensity = GetConditionIntensity(condition);
      var date = DateOnly.FromDateTime(DateTime.Now);

      return new WeatherForecast
      {
        PostalCode = postalCode,
        Temperature = temperature,
        Type = condition,
        Intensity = conditionIntensity,
        Date = date
      };
    }

    private string GetRandomPostalCode()
    {
      return PostalCodes[Random.Shared.Next(PostalCodes.Length)];
    }

    private int GetRandomTemperature()
    {
      return Random.Shared.Next(-40, 41);
    }

    private string GetRandomCondition()
    {
      string[] conditionTypes = 
      {
        "snowfall",
        "rain",
        "sunny",
        "cloudy"
      };
      return conditionTypes[Random.Shared.Next(conditionTypes.Length)];
    }

    private string GetConditionIntensity(string condition)
    {
      if(condition.Equals("snowfall") || condition.Equals("rain")) 
      {
        string[] intensities = 
        {
          "light",
          "medium",
          "heavy"
        };
        return intensities[Random.Shared.Next(intensities.Length)];
      }
      return "n/a";
    }
  }
}