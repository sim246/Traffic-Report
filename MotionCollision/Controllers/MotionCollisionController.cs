using System;
using System.Collections.Generic;
using System.IdentityModel.Tokens.Jwt;
using System.IO;
using Microsoft.AspNetCore.Mvc;
using System;
using Microsoft.Extensions.Logging;
using System.Data;

namespace web_api.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class MotionCollisionSensorController : ControllerBase
    {
        private readonly string[] PostalCodes = { "H2L 4T9", "H2J 4B4", "H3H 1Y3", "H1Z 3A7", "H2H 1S9" };
        private readonly string[] Type = { "motion", "colision" };

        private readonly ILogger<MotionCollisionSensorController> _logger;

        public MotionCollisionSensorController(ILogger<MotionCollisionSensorController> logger)
        {
            _logger = logger;
        }

        [HttpGet(Name = "GetMotionCollision")]
        [ProducesResponseType(typeof(IEnumerable<MotionCollision>), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(string), StatusCodes.Status400BadRequest)]
        [ProducesResponseType(typeof(string), StatusCodes.Status404NotFound)]
        [ProducesResponseType(typeof(string), StatusCodes.Status500InternalServerError)]
        [Produces("application/json")]
        public ActionResult<Object> Get(string token)
        {
            string thePostalCode = RandomPostalCode();
            string theType = RandomDetection();
            bool theValue = RandomValue();
            var theDetection = new Detection { type = theType, value = theValue };
            var theDate = DateOnly.FromDateTime(DateTime.Now);

            try
            {
                if (!ValidateJWTExpiry(token))
                {
                    throw new DataException("Token not valid");
                }

                if (theDetection != null)
                {
                    return new MotionCollision
                    {
                        Date = theDate,
                        PostalCode = thePostalCode,
                        theDetection = theDetection,
                    };
                }
                else
                {
                    return BadRequest("MotionCollision data not found");
                }
            }
            catch (Exception e)
            {
                return BadRequest("MotionCollision data invalid: " + e.Message);
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

        public bool ValidateJWTExpiry(string idtoken)
        {
            var token = new JwtSecurityToken(jwtEncodedString: idtoken);
            string expiry = token.Claims.First(c => c.Type == "exp").Value;
            var dtExpiry = DateTimeOffset.FromUnixTimeSeconds(long.Parse(expiry)).DateTime;
            return DateTime.Now < dtExpiry;
        }
    }
}
