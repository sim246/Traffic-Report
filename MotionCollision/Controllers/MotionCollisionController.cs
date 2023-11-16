using System;
using System.Collections.Generic;
using System.IO;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using MMALSharp;
using MMALSharp.Components;
using MMALSharp.Handlers;
using MMALSharp.Native;
using MMALSharp.Ports;
using MMALSharp.Ports.Outputs;
using MMALSharp.Common;

namespace web_api.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class CollisionSensorController : ControllerBase
    {
        private readonly string[] PostalCodes = { "H2L 4T9", "H2J 4B4", "H3H 1Y3", "H1Z 3A7", "H2H 1S9" };
        private readonly string[] Type = { "motion", "collision" };
        private MMALCamera camera = MMALCamera.Instance;

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
            string thePostalCode = RandomPostalCode();
            string theType = RandomDetection();
            bool theValue = RandomValue();
            var theDetection = new Detection { type = theType, value = theValue };
            var theDate = DateOnly.FromDateTime(DateTime.Now);
            string thePicture = CapturePicture(); // Call the method to capture a picture

            return Enumerable.Range(1, 5).Select(index => new MotionCollision
            {
                Date = theDate,
                PostalCode = thePostalCode,
                theDetection = theDetection,
                Picture = thePicture
            }).ToArray();
        }

        private bool RandomValue()
        {
            var random = new Random();
            return random.Next(2) == 1;
        }

        private string RandomDetection()
        {
            var random = new Random();
            return Type[random.Next(2)];
        }

        private string RandomPostalCode()
        {
            var random = new Random();
            int ran = random.Next(5);
            for (int i = 0; i < 5; i++)
            {
                if (i == ran)
                {
                    return PostalCodes[ran];
                }
            }
            return "";
        }

        private string CapturePicture()
        {
                // Create a new image capture handler
                using (var imgCaptureHandler = new ImageStreamCaptureHandler("../image.jpg", "jpg"))
                {
                    // Take a picture
                    camera.TakePicture(imgCaptureHandler, MMALEncoding.JPEG, MMALEncoding.I420);
                }

                // Return the path to the captured image
                return "../image.jpg";
        }
    }
}
