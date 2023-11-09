using System;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace web_api.Controllers
{
  [ApiController]
  [Route("[controller]")]
  public class CollisionSensorController : ControllerBase
  {
    private static readonly string[] PostalCodes = 
    {
      "K1A 0B1", "V6C 1V5", "M5V 2T6", "L5V 1M5"
    };

    private static readonly string[] DetectionTypes = { "motion", "collision" };

    private readonly ILogger<CollisionSensorController> _logger;

    public CollisionSensorController(ILogger<CollisionSensorController> logger)
    {
      _logger = logger;
    }

    [HttpGet(Name = "GetMotionCollision")]
    [ProducesResponseType(typeof(IEnumerable<MotionCollision>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(string), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(string), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(string), StatusCodes.Status500InternalServerError)]
    [Produces("application/json")]
    public ActionResult<Object> Get()
    {
      var postalCode = GetRandomElement(PostalCodes);
      var detectionType = GetRandomElement(DetectionTypes);
      var detectionValue = GetRandomBoolean();

      var date = DateOnly.FromDateTime(DateTime.Now);

      return new MotionCollision
      {
        Date = date,
        PostalCode = postalCode,
        Detection = new Detection
        {
          Type = detectionType,
          Value = detectionValue
        }
      };
    }

    private static T GetRandomElement<T>(T[] array)
    {
      return array[Random.Shared.Next(array.Length)];
    }

    private static bool GetRandomBoolean()
    {
      return Random.Shared.Next(2) == 0;
    }
  }
}