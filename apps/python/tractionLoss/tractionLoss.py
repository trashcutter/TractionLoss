# Author: trashcutter 12th of June in 2014
import math
import ac
import acsys
import colorsys
import traceback

# app dimensions, some of these will be dynamically calculated
#change tyre dimensions to adjust app size
appHeight = 500
appWidth = 500
tyreWidth = 25
tyreHeight = 45
upperDistance = 50
distanceFromLeft = 40

#debug labels and stuff
debug = None
angle_delta_label = 0
flLabel = 0
flMax = 0
frLabel = 0
frMax = 0
rlLabel = 0
rlMax = 0
rrLabel = 0
rrMax = 0

#increase this value to extend slip indicator range (max_slip is red 0 is green)
max_slip = 4100

#colors
white = [1, 1, 1]
red = [1, 0, 0.1]

#indicator
top_indicator = {}
indicators = {}

#in replay angle values do not work properly and are sometimes frozen at odd angles,
# to see if the angles change we save them here
last_angles = [0, 0, 0, 0]
time_angles_are_same = 0

#confusing but this is just about one tyre described as a rectangle with of course four points (corners)
#rectangle_corners = ["FLC", "FRC", "RRC", "RLC"]
rectangle_corners = ["RLC", "RRC", "FRC", "FLC"]


#ac calls this function the name cannot be changed or script will not work
def acMain(ac_version):
    try:
        global appHeight, appWidth, appWindow, flLabel, frLabel, rlLabel, rrLabel, upperDistance, distanceFromLeft, tyreWidth, tyreHeight
        distanceFromLeft = tyreWidth * 3
        upperDistance = distanceFromLeft
        appWindow = ac.newApp("Traction Loss")
        appWidth = distanceFromLeft * 2 + tyreWidth * 3
        appHeight = upperDistance * 2 + tyreHeight * 3
        ac.setSize(appWindow, appWidth, appHeight)
        define_tachometer()
        if debug:
            create_debug_labels()

        #ac.drawBorder(appWindow, 0)
        ac.addRenderCallback(appWindow, on_update)

        return "Traction Loss"
    except Exception as e:
        ac.console("TractionLoss: Error in function acMain(): %s" % e)
        ac.log("TractionLoss: Error in function acMain(): %s" % e)


def define_tachometer():
    global top_indicator, indicators, upperDistance, distanceFromLeft, tyreHeight, tyreWidth
    car_middle_x = (distanceFromLeft + distanceFromLeft + tyreWidth + tyreWidth + tyreWidth) / 2.0
    car_middle_y = (upperDistance + upperDistance + tyreHeight * 2 + tyreHeight) / 2
    top_indicator = {"RLC": [car_middle_x - 1, upperDistance - 13], "RRC": [car_middle_x, upperDistance - 7],
                     "FRC": [car_middle_x + 1, upperDistance - 13], "FLC": [car_middle_x, upperDistance - 19]}
    for i in range(1, 10):
        indicators[-i * 10] = rotate_rectangle(car_middle_x, car_middle_y, -i * 10, top_indicator.copy())
        indicators[i * 10] = rotate_rectangle(car_middle_x, car_middle_y, i * 10, top_indicator.copy())


def create_debug_labels():
    global flLabel, frLabel, rlLabel, rrLabel, upperDistance, distanceFromLeft, tyreWidth, tyreHeight, angle_delta_label
    flLabel = ac.addLabel(appWindow, "0.0")
    ac.setPosition(flLabel, distanceFromLeft, upperDistance + tyreHeight)
    ac.setFontAlignment(flLabel, "right")

    frLabel = ac.addLabel(appWindow, "0.0")
    ac.setPosition(frLabel, distanceFromLeft + tyreWidth + tyreWidth, upperDistance + tyreHeight)
    ac.setFontAlignment(frLabel, "left")

    rlLabel = ac.addLabel(appWindow, "0.0")
    ac.setPosition(rlLabel, distanceFromLeft, upperDistance + tyreHeight * 2 + tyreHeight)
    ac.setFontAlignment(rlLabel, "right")

    rrLabel = ac.addLabel(appWindow, "0.0")
    ac.setPosition(rrLabel, distanceFromLeft + tyreWidth + tyreWidth, upperDistance + tyreHeight * 2 + tyreHeight)
    ac.setFontAlignment(rrLabel, "left")

    angle_delta_label = ac.addLabel(appWindow, "0.0")
    ac.setPosition(angle_delta_label, 0, upperDistance + tyreHeight * 3 + 50)


def on_update(deltaT):
    try:
        global tyreHeight, tyreWidth, upperDistance, distanceFromLeft, flLabel, frLabel, rlLabel, rrLabel, flMax, frMax, rlMax, rrMax, white, red, last_angles, time_angles_are_same, angle_delta_label
        slip_fl, slip_fr, slip_rl, slip_rr = ac.getCarState(0, acsys.CS.TyreSlip)
        angle_fl, angle_fr, angle_rl, angle_rr = ac.getCarState(0, acsys.CS.SlipAngle)
        angle_car = (angle_rl + angle_rr) / 2
        angle_steering = (angle_fl + angle_fr) / 2.0

        has_angle_changed = None
        angle_delta = sum(last_angles) - angle_fl - angle_fr - angle_rl - angle_rr
        if angle_delta == 0 or deltaT == 0:
            time_angles_are_same = time_angles_are_same + deltaT
            if time_angles_are_same > 2:
                has_angle_changed = None
        else:
            time_angles_are_same = 0
            last_angles = [angle_fl, angle_fr, angle_rl, angle_rr]
            has_angle_changed = True

        speed = ac.getCarState(0, acsys.CS.SpeedKMH)

        #the four tyres and their respective four corner points
        fl_tyre = {"FLC": [distanceFromLeft, upperDistance],
                   "FRC": [distanceFromLeft + tyreWidth, upperDistance],
                   "RLC": [distanceFromLeft, upperDistance + tyreHeight],
                   "RRC": [distanceFromLeft + tyreWidth, upperDistance + tyreHeight]}
        fr_tyre = {"FLC": [distanceFromLeft + tyreWidth + tyreWidth, upperDistance],
                   "FRC": [distanceFromLeft + tyreWidth + tyreWidth + tyreWidth, upperDistance],
                   "RLC": [distanceFromLeft + tyreWidth + tyreWidth, upperDistance + tyreHeight],
                   "RRC": [distanceFromLeft + tyreWidth + tyreWidth + tyreWidth, upperDistance + tyreHeight]}
        rl_tyre = {"FLC": [distanceFromLeft, upperDistance + tyreHeight * 2],
                   "FRC": [distanceFromLeft + tyreWidth, upperDistance + tyreHeight * 2],
                   "RLC": [distanceFromLeft, upperDistance + tyreHeight * 2 + tyreHeight],
                   "RRC": [distanceFromLeft + tyreWidth, upperDistance + tyreHeight * 2 + tyreHeight]}
        rr_tyre = {"FLC": [distanceFromLeft + tyreWidth + tyreWidth, upperDistance + tyreHeight * 2],
                   "FRC": [distanceFromLeft + tyreWidth + tyreWidth + tyreWidth, upperDistance + tyreHeight * 2],
                   "RLC": [distanceFromLeft + tyreWidth + tyreWidth, upperDistance + tyreHeight * 2 + tyreHeight],
                   "RRC": [distanceFromLeft + tyreWidth + tyreWidth + tyreWidth,
                           upperDistance + tyreHeight * 2 + tyreHeight]}
        car_middle_x = (distanceFromLeft + distanceFromLeft + tyreWidth + tyreWidth + tyreWidth) / 2.0
        car_middle_y = (upperDistance + upperDistance + tyreHeight * 2 + tyreHeight) / 2

        #arrow showing heading of car:
        arrow_car_line = {"FLC": [car_middle_x - 3, upperDistance],
                          "FRC": [car_middle_x + 3, upperDistance],
                          "RLC": [car_middle_x - 3, upperDistance + tyreHeight * 2 + tyreHeight],
                          "RRC": [car_middle_x + 3, upperDistance + tyreHeight * 2 + tyreHeight]}
        arrow_car_head = [[car_middle_x - 3, upperDistance],
                          [car_middle_x + 3, upperDistance],
                          [car_middle_x, upperDistance - 6]]

        #arrow showing desired steering direction
        arrow_steering_head = [[car_middle_x, upperDistance - 20], [car_middle_x + 6, upperDistance - 26],
                               [car_middle_x - 6, upperDistance - 26]]

        draw_tachometer()

        if speed > 2 and has_angle_changed:
            #angle individual tyres
            fl_tyre = rotate_rectangle(distanceFromLeft + tyreWidth, (upperDistance + upperDistance + tyreHeight) / 2,
                                       angle_car - angle_fl, fl_tyre)
            fr_tyre = rotate_rectangle(distanceFromLeft + tyreWidth + tyreWidth,
                                       (upperDistance + upperDistance + tyreHeight) / 2, angle_car - angle_fr, fr_tyre)
            rl_tyre = rotate_rectangle(distanceFromLeft + tyreWidth, (
                upperDistance + tyreHeight * 2 + upperDistance + tyreHeight * 2 + tyreHeight) / 2, angle_car - angle_rl,
                                       rl_tyre)
            rr_tyre = rotate_rectangle(distanceFromLeft + tyreWidth + tyreWidth, (
                upperDistance + tyreHeight * 2 + upperDistance + tyreHeight * 2 + tyreHeight) / 2, angle_car - angle_rr,
                                       rr_tyre)
            #now angle the whole car
            fl_tyre = rotate_rectangle(car_middle_x, car_middle_y, -angle_car, fl_tyre)
            fr_tyre = rotate_rectangle(car_middle_x, car_middle_y, -angle_car, fr_tyre)
            rl_tyre = rotate_rectangle(car_middle_x, car_middle_y, -angle_car, rl_tyre)
            rr_tyre = rotate_rectangle(car_middle_x, car_middle_y, -angle_car, rr_tyre)
            arrow_car_line = rotate_rectangle(car_middle_x, car_middle_y, -angle_car, arrow_car_line)
            arrow_car_head = rotate_triangle(car_middle_x, car_middle_y, -angle_car, arrow_car_head)
            arrow_steering_head = rotate_triangle(car_middle_x, car_middle_y, -angle_steering, arrow_steering_head)

        draw_triangle(arrow_steering_head, red)
        draw_bar(arrow_car_line, white)
        draw_triangle(arrow_car_head, white)

        draw_colored_bars_with_points(slip_fl, fl_tyre)
        if slip_fl > flMax:
            flMax = slip_fl

        draw_colored_bars_with_points(slip_fr, fr_tyre)
        if slip_fr > frMax:
            frMax = slip_fr

        draw_colored_bars_with_points(slip_rl, rl_tyre)
        if slip_rl > rlMax:
            rlMax = slip_rl

        draw_colored_bars_with_points(slip_rr, rr_tyre)
        if slip_rr > rrMax:
            rrMax = slip_rr

        if debug:
            ac.setText(angle_delta_label,
                       "da|t|ca: {:.1f}|{:.1f}|{:.1f}|{:.3f}".format(angle_delta, time_angles_are_same, angle_car,
                                                                     deltaT))
            ac.setText(flLabel, "fl{:.2f}|{:.2f}".format(slip_fl, flMax))
            ac.setText(frLabel, "fr{:.2f}|{:.2f}".format(slip_fr, frMax))
            ac.setText(rlLabel, "rl{:.2f}|{:.2f}".format(slip_rl, rlMax))
            ac.setText(rrLabel, "rr{:.2f}|{:.2f}".format(slip_rr, rrMax))

    except Exception as e:
        ac.log("TractionLoss: Error in function on_update(): %s" % e)
        ac.log(str(traceback.format_exc()))


def draw_tachometer():
    global distanceFromLeft, tyreWidth, upperDistance, white, top_indicator

    draw_bar(top_indicator, white)
    for degree in indicators:
        draw_bar(indicators[degree], white)


def draw_bar(points, color=[1, 1, 1]):
    global rectangle_corners
    r, g, b = color
    ac.glColor4f(r, g, b, 1)
    ac.glBegin(acsys.GL.Quads)
    for corner in rectangle_corners:
        x, y = points[corner]
        ac.glVertex2f(x, y)
    ac.glEnd()


def draw_triangle(points, color=[1, 1, 1]):
    r, g, b = color
    ac.glColor4f(r, g, b, 1)
    ac.glBegin(acsys.GL.Triangles)
    for x_y_tuple in points:
        x, y = x_y_tuple
        ac.glVertex2f(x, y)
    ac.glEnd()


def draw_colored_bars_with_points(slip, tyre):
    global max_slip, rectangle_corners
    r, g, b = get_color(slip)
    ac.glColor4f(r, g, b, 1)
    ac.glBegin(acsys.GL.Quads)
    for corner in rectangle_corners:
        x, y = tyre[corner]
        ac.glVertex2f(x, y)
    ac.glEnd()


def rotate_point(point_x, point_y, origin_x, origin_y, angle):
    angle = angle * math.pi / 180.0
    return math.cos(angle) * (point_x - origin_x) - math.sin(angle) * (point_y - origin_y) + origin_x, math.sin(
        angle) * (point_x - origin_x) + math.cos(angle) * (point_y - origin_y) + origin_y


def rotate_rectangle(origin_x, origin_y, angle, tyre):
    global rectangle_corners

    for corner in rectangle_corners:
        x, y = tyre[corner]
        tyre[corner] = rotate_point(x, y, origin_x, origin_y, angle)

    return tyre


def rotate_triangle(origin_x, origin_y, angle, points):
    new_points = []
    for x_y_tuple in points:
        x, y = x_y_tuple
        new_points[len(new_points):] = [rotate_point(x, y, origin_x, origin_y, angle)]
    return new_points


#dynamic color generator using 120 degree of hsv hue
def get_color(slip):
    global max_slip
    if slip > max_slip:
        slip = max_slip
    return colorsys.hsv_to_rgb((120.0 - (120 / max_slip) * slip) / 360.0, 1.0, 1.0)