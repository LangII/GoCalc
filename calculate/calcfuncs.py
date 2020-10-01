
import math

####################################################################################################

def getDistTwoPoints(pt1=[0, 0], pt2=[0, 0]):
    return math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1])



def getAngleTwoPoints(vertex_pt=[0, 0], ray_pt=[0, 0]):
    """ Return angle between ray(vertex_pt, [0, 1]) and ray(vertex_pt, ray_pt) represented as
    degrees between 0 and 360. """
    angle_rad = math.atan2(ray_pt[0] - vertex_pt[0], ray_pt[1] - vertex_pt[1])
    angle_deg = math.degrees(angle_rad)
    angle_deg360 = abs(180 + (180 - abs(-angle_deg)) if -angle_deg < 0 else angle_deg)
    return angle_deg360



def applyScale(values, scale_from=[], scale_to=[]):
    """
    value =         Value to have scale applied to.
    scale_from =    Array with len() of 2, representing the start and end of the 'scale_from'
                    number line.
    scale_to =      Array with len() of 2, representing the start and end of the 'scale_to'
                    number line.
    Return value with scale applied.
    """
    # Controls for handling single value or array of values.
    is_array = True
    if not isinstance(values, (list, tuple, set)):  values, is_array = [values], False
    values_to_scale = []
    for value in values:
        # Apply scale to value.
        to_scale = value - scale_from[0]
        adjust = scale_to[1] / (scale_from[1] - scale_from[0])
        to_scale = abs(to_scale * adjust)
        values_to_scale += [ to_scale ]
    return values_to_scale if is_array else values_to_scale[0]



def applyBias(values, bias_point=0.0, bias_value=0.0, bias_type='exp'):
    """
    value =         Value to have bias applied.
    bias_point =    Value designating whether 'value' is to have bias applied.  If 'bias_point' is
                    positive and 'value' is greater than 'bias_point' then bias will be applied.  if
                    'bias_point' is negative and 'value' is less than 'bias_point' than bias will be
                    applied.
    bias_value =    Growth rate of the bias.  If 'bias_value' is positive then the growrth rate will
                    be increasing in value away from 'bias_point'.  If 'bias_value' is negative then
                    the growth rate will be diminish in value away from 'bias_point'.
    bias_type =     Accepts 'l', 'lin', 'linear', 'e', 'exp', or 'exponential' designating whether
                    the growth rate is linear or exponential.
    Return value with bias applied.
    """
    # Controls for handling single value or array of values.
    is_array = True
    if not isinstance(values, (list, tuple, set)):  values, is_array = [values], False
    values_with_bias = []
    for value in values:
        bias_point_x, bias_value_x = bias_point, bias_value
        with_bias = value
        # Determine if bias needs to be applied.
        bias_less_than = bias_point_x < 0 and value < abs(bias_point_x)
        bias_greater_than = bias_point_x >= 0 and value >= abs(bias_point_x)
        if bias_less_than or bias_greater_than:
            # Controls for neg value bias_point (flip value about bias_point).
            unflip_value = False
            if bias_point < 0:
                bias_point_x = bias_point_x * -1
                value = bias_point_x + (bias_point_x - value)
                unflip_value = True
            # Apply bias_value.
            value -= bias_point_x
            bias_value_x = 1 + bias_value_x
            if bias_type in ['l', 'lin', 'linear']:  with_bias = value * bias_value_x
            elif bias_type in ['e', 'exp', 'exponential']:  with_bias = value ** bias_value_x
            with_bias += bias_point_x
            # Controls for neg value bias_point (unflip value about bias_point).
            if unflip_value:  with_bias = bias_point_x - (with_bias - bias_point_x)
        values_with_bias += [ with_bias ]
    return values_with_bias if is_array else values_with_bias[0]
