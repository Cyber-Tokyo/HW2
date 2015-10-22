# Roaming-Ralph was modified to remove collision part.

#Team: Bruno Recillas // Oscar Ramirez

import direct.directbase.DirectStart
from panda3d.core import Filename,AmbientLight,DirectionalLight
from panda3d.core import PandaNode,NodePath,Camera,TextNode
from panda3d.core import Vec3,Vec4,BitMask32
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
import random, sys, os, math
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3

SPEED = 0.5

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1), pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1), pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)

class World(DirectObject):

    def __init__(self):

        self.keyMap = {"left":0, "right":0, "forward":0, "cam-left":0, "cam-right":0}
        base.win.setClearColor(Vec4(0,0,0,1))

        # Post the instructions

        self.title = addTitle("HW2: Roaming Ralph Modified (Walking on the Moon)")
        self.inst1 = addInstructions(0.95, "[ESC]: Quit")
        self.inst2 = addInstructions(0.90, "[A]: Rotate Ralph Left")
        self.inst3 = addInstructions(0.85, "[D]: Rotate Ralph Right")
        self.inst4 = addInstructions(0.80, "[W]: Run Ralph Forward")
        self.inst6 = addInstructions(0.70, "[Left Arrow]: Rotate Camera Left")
        self.inst7 = addInstructions(0.65, "[Right Arrow]: Rotate Camera Right")

        # Set up the environment
        #
        self.environ = loader.loadModel("models/square")
        self.environ.reparentTo(render)
        self.environ.setPos(0,0,0)
        self.environ.setScale(100,100,1)
        self.moon_tex = loader.loadTexture("models/moon_1k_tex.jpg")
    	self.environ.setTexture(self.moon_tex, 1)

        # Create the main character, Ralph

        self.ralph = Actor("models/ralph", {"run":"models/ralph-run", "walk":"models/ralph-walk"})
        self.ralph.reparentTo(render)
        self.ralph.setScale(.2)
        self.ralph.setPos(0,0,0)

        #creates the car
        self.Groundroamer = Actor("models/Groundroamer.egg")
        self.Groundroamer.reparentTo(render)
        self.Groundroamer.setScale(0.2)
        self.Groundroamer.setPos(30,25,0)
        self.Groundroamer.setHpr(0,0,0)
        self.Groundroamer_texture = loader.loadTexture("models/Groundroamer.tif")
        self.Groundroamer.setTexture(self.Groundroamer_texture)


        #creates the Lander
        self.Lander = Actor("models/lunarlander")
        self.Lander.reparentTo(render)
        self.Lander.setScale(0.1)
        self.Lander.setPos(45,50,0)
        self.Lander_texture = loader.loadTexture("models/landermap_Material_#16_CL.tif")
        self.Lander.setTexture(self.Lander_texture)

        #creates Earth
        self.earth = Actor("models/planet_sphere.egg.pz")
        self.earth.reparentTo(render)
        self.earth.setScale(5.0)
        self.earth.setPos(15,25,5)
        self.earth_texture = loader.loadTexture("models/earth_1k_tex.jpg")
        self.earth.setTexture(self.earth_texture)

        #creates Mars
        self.mars = Actor("models/planet_sphere.egg.pz")
        self.mars.reparentTo(render)
        self.mars.setScale(8.0)
        self.mars.setPos(-30,25,8)
        self.mars_texture = loader.loadTexture("models/mars_1k_tex.jpg")
        self.mars.setTexture(self.mars_texture)

        #creates Mercury
        self.mercury = Actor("models/planet_sphere.egg.pz")
        self.mercury.reparentTo(render)
        self.mercury.setScale(3.0)
        self.mercury.setPos(-40,-25,3)
        self.mercury_texture = loader.loadTexture("models/mercury_1k_tex.jpg")
        self.mercury.setTexture(self.mercury_texture)

        #creates Venus
        self.venus = Actor("models/planet_sphere.egg.pz")
        self.venus.reparentTo(render)
        self.venus.setScale(10.0)
        self.venus.setPos(40,-15,10)
        self.venus_texture = loader.loadTexture("models/venus_1k_tex.jpg")
        self.venus.setTexture(self.venus_texture)

        # Create a floater object.  We use the "floater" as a temporary
        # variable in a variety of calculations.

        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)

        # Accept the control keys for movement and rotation
        self.accept("escape", sys.exit)
        self.accept("a", self.setKey, ["left",1])
        self.accept("d", self.setKey, ["right",1])
        self.accept("w", self.setKey, ["forward",1])
        self.accept("arrow_left", self.setKey, ["cam-left",1])
        self.accept("arrow_right", self.setKey, ["cam-right",1])
        self.accept("a-up", self.setKey, ["left",0])
        self.accept("d-up", self.setKey, ["right",0])
        self.accept("w-up", self.setKey, ["forward",0])
        self.accept("arrow_left-up", self.setKey, ["cam-left",0])
        self.accept("arrow_right-up", self.setKey, ["cam-right",0])

        taskMgr.add(self.move,"moveTask")

        # Game state variables
        self.isMoving = False

        # Set up the camera

        base.disableMouse()
        base.camera.setPos(self.ralph.getX(),self.ralph.getY()+10,2)


        # Create some lighting
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor(Vec4(.3, .3, .3, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(Vec3(-5, -5, -5))
        directionalLight.setColor(Vec4(1, 1, 1, 1))
        directionalLight.setSpecularColor(Vec4(1, 1, 1, 1))
        render.setLight(render.attachNewNode(ambientLight))
        render.setLight(render.attachNewNode(directionalLight))

    #Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value


    # Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    def move(self, task):

        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.

        base.camera.lookAt(self.ralph)
        if (self.keyMap["cam-left"]!=0):
            base.camera.setX(base.camera, -20 * globalClock.getDt())
        if (self.keyMap["cam-right"]!=0):
            base.camera.setX(base.camera, +20 * globalClock.getDt())

        # save ralph's initial position so that we can restore it,
        # in case he falls off the map or runs into something.

        startpos = self.ralph.getPos()

        # If a move-key is pressed, move ralph in the specified direction.

        if (self.keyMap["left"]!=0):
            self.ralph.setH(self.ralph.getH() + 300 * globalClock.getDt())
        if (self.keyMap["right"]!=0):
            self.ralph.setH(self.ralph.getH() - 300 * globalClock.getDt())
        if (self.keyMap["forward"]!=0):
            self.ralph.setY(self.ralph, -25 * globalClock.getDt())

        # If ralph is moving, loop the run animation.
        # If he is standing still, stop the animation.

        if (self.keyMap["forward"]!=0) or (self.keyMap["left"]!=0) or (self.keyMap["right"]!=0):
            if self.isMoving is False:
                self.ralph.loop("run")
                self.isMoving = True
        else:
            if self.isMoving:
                self.ralph.stop()
                self.ralph.pose("walk",5)
                self.isMoving = False

        # If the camera is too far from ralph, move it closer.
        # If the camera is too close to ralph, move it farther.

        camvec = self.ralph.getPos() - base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if (camdist > 10.0):
            base.camera.setPos(base.camera.getPos() + camvec*(camdist-10))
            camdist = 10.0
        if (camdist < 5.0):
            base.camera.setPos(base.camera.getPos() - camvec*(5-camdist))
            camdist = 5.0


        # The camera should look in ralph's direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above ralph's head.

        self.floater.setPos(self.ralph.getPos())
        self.floater.setZ(self.ralph.getZ() + 2.0)
        base.camera.lookAt(self.floater)

        return task.cont


w = World()
base.run()
