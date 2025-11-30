import math

def get_distance(lat1, lon1, lat2, lon2):
    """Haversine formula to calculate distance in meters"""
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_bearing(lat1, lon1, lat2, lon2):
    """Calculate bearing between two points in degrees"""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)
    
    y = math.sin(dlambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda)
    theta = math.atan2(y, x)
    return (math.degrees(theta) + 360) % 360

def move_point(lat, lon, distance_m, bearing_deg):
    """Calculate new lat/lon given distance and bearing"""
    R = 6371000
    d = distance_m / R
    theta = math.radians(bearing_deg)
    phi1 = math.radians(lat)
    lambda1 = math.radians(lon)
    
    phi2 = math.asin(math.sin(phi1) * math.cos(d) + math.cos(phi1) * math.sin(d) * math.cos(theta))
    lambda2 = lambda1 + math.atan2(math.sin(theta) * math.sin(d) * math.cos(phi1),
                                 math.cos(d) - math.sin(phi1) * math.sin(phi2))
    
    return math.degrees(phi2), math.degrees(lambda2)

