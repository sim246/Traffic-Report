using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using RaspberryPi.NetStandard;
using RaspberryPi.NetStandard.Cameras;
using RaspberryPi.NetStandard.Cameras.MMAL;

//dotnet add package RaspberryPi.NetStandard
namespace web_api.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class CollisionSensorController : ControllerBase
    {
        private readonly string[] PostalCodes = { "H2L 4T9", "H2J 4B4", "H3H 1Y3", "H1Z 3A7", "H2H 1S9" };
        private readonly string[] Types = { "motion", "collision" };

        private readonly ILogger<CollisionSensorController> _logger;
        private readonly Camera _camera;

        public CollisionSensorController(ILogger<CollisionSensorController> logger)
        {
            _logger = logger;

            // Initialize the Raspberry Pi camera
            _camera = new MMALCamera();
        }

        [HttpGet(Name = "GetMotionCollision")]
        [ProducesResponseType(typeof(IEnumerable<MotionCollision>), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(string), StatusCodes.Status400BadRequest)]
        [ProducesResponseType(typeof(string), StatusCodes.Status404NotFound)]
        [ProducesResponseType(typeof(string), StatusCodes.Status500InternalServerError)]
        [Produces("application/json")]
        public ActionResult<IEnumerable<MotionCollision>> Get()
        {
            string thePostalCode = RandomPostalCode();
            string theType = RandomDetection();
            bool theValue = RandomValue();
            var theDetection = new Detection { Type = theType, Value = theValue };
            var theDate = DateOnly.FromDateTime(DateTime.Now);
            string pictureFileName = CapturePictureOnCollision(theType);

            return Enumerable.Range(1, 5).Select(index => new MotionCollision
            {
                Date = theDate,
                PostalCode = thePostalCode,
                TheDetection = theDetection,
                Picture = pictureFileName
            }).ToArray();
        }

        private string CapturePictureOnCollision(string detectionType)
        {
            if (detectionType.ToLower() == "collision")
            {
                // Capture a picture when a collision is detected
                string pictureFileName = $"collision_picture_{DateTime.Now:yyyyMMddHHmmss}.jpg";
                CapturePicture(pictureFileName);
                return pictureFileName;
            }

            return "no_picture.jpg"; // Return a placeholder or empty string if no collision
        }

        private void CapturePicture(string fileName)
        {
            // Capture a picture using the Raspberry Pi camera
            using (var capture = _camera.Capture())
            {
                using (var stream = new FileStream(fileName, FileMode.Create))
                {
                    capture.Save(stream, ImageFormat.Jpeg);
                }
            }
        }

        private bool RandomValue()
        {
            var random = new Random();
            return random.Next(2) == 1;
        }

        private string RandomDetection()
        {
            var random = new Random();
            return Types[random.Next(2)];
        }

        private string RandomPostalCode()
        {
            var random = new Random();
            int ran = random.Next(5);
            return PostalCodes[ran];
        }
    }
}