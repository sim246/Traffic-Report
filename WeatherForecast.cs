namespace web_api;

public class WeatherForecast
{

    public string PostalCode { get; set; }

    public int GetRandomTemperature { get; set; }

    public string Type { get; set; }
    
    public string Intensity { get; set; }
    
    public DateOnly Date { get; set; }
}
