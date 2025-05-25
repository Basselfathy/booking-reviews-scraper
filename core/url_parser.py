from urllib.parse import urlparse
import re

def parse_booking_url(url: str) -> tuple[str, str]:
    """Extract hotel name and country code from a Booking.com URL.
    
    Args:
        url: A Booking.com hotel URL
        
    Returns:
        Tuple of (hotel_name, country_code)
    """
    # Clean the URL first
    url = url.strip()
    
    try:
        parsed = urlparse(url)
        # Path format is typically: /hotel/{country_code}/{hotel-name}.html
        path_parts = parsed.path.split('/')
        
        # Extract country code
        country_code = path_parts[2] if len(path_parts) > 2 else None
        
        # Extract hotel name
        hotel_name = None
        if len(path_parts) > 3:
            # Remove .html and clean up the name
            hotel_name = path_parts[3].replace('.html', '')
            # Remove any query parameters if present
            hotel_name = hotel_name.split('?')[0]
        
        if not country_code or not hotel_name:
            raise ValueError("Could not extract country code or hotel name from URL")
            
        return hotel_name, country_code
        
    except Exception as e:
        raise ValueError(f"Invalid Booking.com URL format: {str(e)}")
