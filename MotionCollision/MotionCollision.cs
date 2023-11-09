namespace web_api;

public class MotionCollision
{
    public DateOnly Date { get; set; }
    
    public string PostalCode { get; set; }
    
    public Detection theDetection { get; set; }
    
    public string Picture { get; set; }
}

public class Detection
{
	public string type { get; set; }
	public bool value { get; set; }
}
