namespace web_api;

public class WeatherForecast
{
    public DateOnly Date { get; set; }
    
    public string PostalCode { get; set; }
    
    public var Detection { get; set; }
    
    public string Picture { get; set; }
}
