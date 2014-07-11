#Author: trashcutter 12th of June in 2014
import math
import ac
import acsys

appHeight = 500
appWidth = 500 #distanceFromLeft*2 + tyreWidth*3
tyreWidth = 50
tyreHeight = 90
upperDistance = 50
distanceFromLeft = 40
flLabel = 0
flMax = 0
frLabel = 0
frMax = 0
rlLabel = 0
rlMax = 0
rrLabel = 0
rrMax = 0
tractionFactor = 700
debug = None

#confusing but this is just about one tyre described as a rectangle with of course four points (corners)
tyre_corners = ["FLC", "FRC", "RRC", "RLC"]

def acMain(ac_version):
    try:
        global appHeight, appWidth, appWindow, flLabel, frLabel, rlLabel, rrLabel, upperDistance, distanceFromLeft, tyreWidth, tyreHeight
        appWindow = ac.newApp("Traction Loss")
        appWidth = distanceFromLeft*2 + tyreWidth*3
        appHeight = upperDistance*2 + tyreHeight*3
        ac.setSize(appWindow, appWidth, appHeight)
        if(debug):
            create_debug_labels()


        #ac.drawBorder(appWindow, 0)
        ac.addRenderCallback(appWindow, on_update)

        return "Traction Loss"
    except Exception as e:
        ac.console("TractionLoss: Error in function acMain(): %s" % e)
        ac.log("TractionLoss: Error in function acMain(): %s" % e)


def create_debug_labels():
    global flLabel, frLabel, rlLabel, rrLabel, upperDistance, distanceFromLeft, tyreWidth, tyreHeight
    flLabel=ac.addLabel(appWindow, "0.0")
    ac.setPosition(flLabel, distanceFromLeft, upperDistance+tyreHeight)
    ac.setFontAlignment(flLabel, "left")

    frLabel=ac.addLabel(appWindow, "0.0")
    ac.setPosition(frLabel, distanceFromLeft+tyreWidth+tyreWidth, upperDistance+tyreHeight)
    ac.setFontAlignment(frLabel, "left")

    rlLabel=ac.addLabel(appWindow, "0.0")
    ac.setPosition(rlLabel, distanceFromLeft, upperDistance+tyreHeight*2+tyreHeight)
    ac.setFontAlignment(rlLabel, "left")

    rrLabel=ac.addLabel(appWindow, "0.0")
    ac.setPosition(rrLabel, distanceFromLeft+tyreWidth+tyreWidth, upperDistance+tyreHeight*2+tyreHeight)
    ac.setFontAlignment(rrLabel, "left")


def on_update(deltaT):
    try:
        global tyreHeight, tyreWidth, upperDistance, distanceFromLeft, flLabel, frLabel, rlLabel, rrLabel, flMax, frMax, rlMax, rrMax
        slipFL,slipFR,slipRL,slipRR=ac.getCarState(0,acsys.CS.TyreSlip)

        angle_fl, angle_fr, angle_rl, angle_rr = ac.getCarState(0,acsys.CS.SlipAngle)
        speed = ac.getCarState(0,acsys.CS.SpeedKMH)

        #the four tyres and their respective four corner points
        fl_tyre = {"FLC": [distanceFromLeft, upperDistance], "FRC": [distanceFromLeft+tyreWidth, upperDistance], "RLC": [distanceFromLeft, upperDistance + tyreHeight], "RRC": [distanceFromLeft+tyreWidth, upperDistance + tyreHeight]}
        fr_tyre = {"FLC": [distanceFromLeft+tyreWidth+tyreWidth, upperDistance], "FRC": [distanceFromLeft+tyreWidth+tyreWidth+tyreWidth, upperDistance], "RLC": [distanceFromLeft+tyreWidth+tyreWidth, upperDistance + tyreHeight], "RRC": [distanceFromLeft+tyreWidth+tyreWidth+tyreWidth, upperDistance + tyreHeight]}
        rl_tyre = {"FLC": [distanceFromLeft, upperDistance+tyreHeight*2], "FRC": [distanceFromLeft+tyreWidth, upperDistance+tyreHeight*2], "RLC": [distanceFromLeft, upperDistance+tyreHeight*2 + tyreHeight], "RRC": [distanceFromLeft+tyreWidth, upperDistance+tyreHeight*2 + tyreHeight]}
        rr_tyre = {"FLC": [distanceFromLeft+tyreWidth+tyreWidth, upperDistance+tyreHeight*2], "FRC": [distanceFromLeft+tyreWidth+tyreWidth+tyreWidth, upperDistance+tyreHeight*2], "RLC": [distanceFromLeft+tyreWidth+tyreWidth, upperDistance+tyreHeight*2 + tyreHeight], "RRC": [distanceFromLeft+tyreWidth+tyreWidth+tyreWidth, upperDistance+tyreHeight*2 + tyreHeight]}

        if(speed > 2):
            fl_tyre = rotate_tyre(distanceFromLeft+tyreWidth, (upperDistance+upperDistance + tyreHeight)/2, -angle_fl, fl_tyre)
            fr_tyre = rotate_tyre(distanceFromLeft+tyreWidth+tyreWidth, (upperDistance+upperDistance + tyreHeight)/2, -angle_fr, fr_tyre)
            rl_tyre = rotate_tyre(distanceFromLeft+tyreWidth, (upperDistance+tyreHeight*2 + upperDistance+tyreHeight*2 + tyreHeight)/2, -angle_rl, rl_tyre)
            rr_tyre = rotate_tyre(distanceFromLeft+tyreWidth+tyreWidth, (upperDistance+tyreHeight*2 + upperDistance+tyreHeight*2 + tyreHeight)/2, -angle_rr, rr_tyre)

        draw_bars_with_points(slipFL, fl_tyre)
        if(slipFL > flMax):
            flMax = slipFL

        draw_bars_with_points(slipFR, fr_tyre)
        if(slipFR > frMax):
            frMax = slipFR

        draw_bars_with_points(slipRL, rl_tyre)
        if(slipRL > rlMax):
            rlMax = slipRL

        draw_bars_with_points(slipRR, rr_tyre)
        if(slipRR > rrMax):
            rrMax = slipRR

        if(debug):
            ac.setText(flLabel, "fl{:.2f}|{:.2f}".format(slipFL, flMax))
            ac.setText(frLabel, "fr{:.2f}|{:.2f}".format(slipFR, frMax))
            ac.setText(rlLabel, "rl{:.2f}|{:.2f}".format(slipRL, rlMax))
            ac.setText(rrLabel, "rr{:.2f}|{:.2f}".format(slipRR, rrMax))


    except Exception as e:
        ac.console("TractionLoss: Error in function onUpdate(): %s" % e)
        ac.log("TractionLoss: Error in function onUpdate(): %s" % e)


def draw_bars(x, y, slip):
    global tyreHeight, tyreWidth, tractionFactor

    ac.glColor4f(0,1,0,1)
    if(slip>0.4*tractionFactor):
        ac.glColor4f(1, 1, 0,1)

    if(slip>1*tractionFactor):
        ac.glColor4f(1.0, 0.6, 0.0,1)

    if(slip>2*tractionFactor):
        ac.glColor4f(1,0,0,1)

    ac.glQuad(x,y,tyreWidth,tyreHeight)


def draw_bars_with_points(slip, tyre):
    global tractionFactor, tyre_corners

    ac.glColor4f(0,1,0,1)
    if(slip>0.4*tractionFactor):
        ac.glColor4f(1, 1, 0, 1)

    if(slip>1*tractionFactor):
        ac.glColor4f(1.0, 0.6, 0.0, 1)

    if(slip>2*tractionFactor):
        ac.glColor4f(1, 0, 0, 1)

    ac.glBegin(acsys.GL.Quads)
    for corner in tyre_corners:
        x, y = tyre[corner]
        ac.glVertex2f(x, y)
    ac.glEnd()


def rotate_point(point_x, point_y, origin_x, origin_y, angle):
    angle = angle * math.pi / 180.0
    return math.cos(angle) * (point_x-origin_x) - math.sin(angle) * (point_y-origin_y) + origin_x, math.sin(angle) * (point_x-origin_x) + math.cos(angle) * (point_y-origin_y) + origin_y


def rotate_tyre(origin_x, origin_y, angle, tyre):
    global tyre_corners

    for corner in tyre_corners:
        x, y = tyre[corner]
        tyre[corner] = rotate_point(x, y, origin_x, origin_y, angle)

    return tyre